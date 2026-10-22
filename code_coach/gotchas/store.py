"""Gotchas' memory: which cards you have seen, missed and answered, and the cards you added.

Two files beside the progress file, written with the same atomic writer as every other save
(Momentum's), and read the same way (a broken file is kept as `.bad`, never thrown away):

* `gotchas.json` - per-card stats, a per-language answer counter, the streak, today's Daily 5::

    {"version": 1,
     "stats": {"python:py-score-90": {"seen": 2, "right": 1, "last_day": "2026-10-19",
                                      "last_tick": 12, "due": null | 17}},
     "ticks": {"python": 12},
     "streak": {"python": {"now": 3, "best": 9}},
     "daily": {"python": {"day": "2026-10-19", "ids": [...5 ids...], "results": {"<id>": true}}}}

* `gotchas_user.json` - the cards the user typed in: `{"version": 1, "next": 4, "cards": [...]}`.

Nothing here ever touches the progress file's own schema.

How a card is chosen (`GotchaStore.pick`), in order:

1. a card you just added and have not answered yet ("Yours"),
2. the first two cards of a language's deck while you have seen fewer than two (so the score=90
   card is the very first thing you meet),
3. a card that is due (`tick` counts answers in a language): a miss comes back 5-10 answers later; a miss
   you were SURE about comes back sooner, 2-4 later, and sorts ahead of the other due cards; a right answer
   you only GUESSED is "shaky" and comes back once, 10-20 answers later (answer it right and Sure and it is
   done like any right card),
4. an unseen card, at random,
5. otherwise the card seen longest ago.

How sure you were (`confidence`: "sure", "guess" or "") and an optional note of your reasoning (300 characters,
the last 3 kept per card) are recorded with each answer; neither changes the Momentum XP. `traps()` lists the
cards you have missed and not yet mastered (mastered = your last two answers were right AND marked Sure).

`exclude` (the cards on screen a moment ago) is honoured unless it would leave nothing.
The answer is never part of what `pick` returns; it is only known to `answer()`.
"""

from __future__ import annotations

import hashlib
import random
import threading
from datetime import date
from pathlib import Path
from typing import Any, Callable

from .items import Item
from .langs import ORDER as LANGUAGES  # every registered language id, in display order

VERSION = 1
#: A missed card comes back after this many other answers, plus up to RETURN_SPREAD more.
RETURN_AFTER = 5
RETURN_SPREAD = 5
#: How long until a card is due again, by why it is coming back: (fewest answers later, most answers later).
#: `miss` is a wrong answer (or a wrong guess), `sure_wrong` a wrong answer you were sure about, `shaky` a right
#: answer you only guessed. Note the browser also withholds the last 3 cards it showed (`exclude`), so a card due
#: at +2 is, in the feed, served from +3.
RETURNS = {"miss": (RETURN_AFTER, RETURN_AFTER + RETURN_SPREAD), "sure_wrong": (2, 4), "shaky": (10, 20)}
#: Among due cards the one that was sure-and-wrong comes first, then ordinary misses, then shaky ones.
DUE_RANK = {"sure_wrong": 0, "miss": 1, "shaky": 2}
CONFIDENCE = ("sure", "guess")
#: A note of your own reasoning: at most this many characters, and the last NOTE_KEEP are kept per card.
NOTE_MAX = 300
NOTE_KEEP = 3
#: Mastered = this many answers in a row that were right and marked Sure.
MASTERED_RUN = 2
#: How many cards of a language's deck are served in deck order before it goes random.
LEAD = 2
DAILY_SIZE = 5
MAX_USER_CARDS = 200


class UnknownCard(ValueError):
    """The id (or language) names no card in the deck."""


class BadChoice(ValueError):
    """The chosen option is not one of the card's options."""


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    from code_coach.momentum.engine import _write_json as write

    write(path, payload)


def _read(path: Path, clean: Callable[[Any], dict[str, Any] | None],
          fresh: Callable[[], dict[str, Any]], label: str) -> dict[str, Any]:
    from code_coach.momentum.engine import read_state

    return read_state(path, clean, fresh, label)


def _int(value: Any, default: int = 0) -> int:
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return default


def clean_confidence(value: Any) -> str:
    """"sure" or "guess"; anything else (missing, wrong type, other words) is "" - no claim either way."""
    return value if isinstance(value, str) and value in CONFIDENCE else ""


def clean_note(value: Any) -> str:
    """The note as stored: a string, trimmed, at most NOTE_MAX characters ("" when there is none)."""
    if not isinstance(value, str):
        return ""
    return value.strip()[:NOTE_MAX].strip()


def return_offset(kind: str, key: str, tick: int) -> int:
    """How many answers later a card is due again: inside RETURNS[kind], spread by a hash of the card and the
    answer count (so it is the same on every run, and different for different cards)."""
    low, high = RETURNS[kind]
    return low + _digest(f"{key}:{tick}") % (high - low + 1)


def _blank_stat() -> dict[str, Any]:
    return {"seen": 0, "right": 0, "last_day": "", "last_tick": 0, "due": None, "due_kind": None,
            "sure_right": 0, "sure_wrong": 0, "guess_right": 0, "guess_wrong": 0, "sure_run": 0,
            "note": "", "notes": []}


def _clean_notes(raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    out = []
    for n in raw:
        if isinstance(n, dict) and clean_note(n.get("note")):
            out.append({"day": str(n.get("day") or ""), "note": clean_note(n.get("note")),
                        "correct": bool(n.get("correct"))})
    return out[-NOTE_KEEP:]


def _beside_progress(name: str) -> Path:
    from code_coach.progress.store import active_store

    return active_store().path.with_name(name)


# ── gotchas.json ────────────────────────────────────────────────────────


def _fresh() -> dict[str, Any]:
    return {"version": VERSION, "stats": {}, "ticks": {}, "streak": {}, "daily": {}}


def _clean(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    state = _fresh()
    stats = raw.get("stats")
    if isinstance(stats, dict):
        for key, s in stats.items():
            if not isinstance(key, str) or not isinstance(s, dict):
                continue
            due = s.get("due")
            due = _int(due) if isinstance(due, (int, float)) and not isinstance(due, bool) else None
            kind = s.get("due_kind")
            notes = _clean_notes(s.get("notes"))
            # An old file has no confidence fields: they start at nothing, and a card that was due is a plain miss.
            state["stats"][key] = {
                **_blank_stat(),
                "seen": _int(s.get("seen")), "right": _int(s.get("right")),
                "last_day": str(s.get("last_day") or ""), "last_tick": _int(s.get("last_tick")),
                "due": due, "due_kind": (kind if kind in RETURNS else "miss") if due is not None else None,
                "sure_right": _int(s.get("sure_right")), "sure_wrong": _int(s.get("sure_wrong")),
                "guess_right": _int(s.get("guess_right")), "guess_wrong": _int(s.get("guess_wrong")),
                "sure_run": _int(s.get("sure_run")),
                "note": clean_note(s.get("note")) or (notes[-1]["note"] if notes else ""), "notes": notes,
            }
    if isinstance(raw.get("ticks"), dict):
        state["ticks"] = {str(k): _int(v) for k, v in raw["ticks"].items()}
    if isinstance(raw.get("streak"), dict):
        for lang, s in raw["streak"].items():
            if isinstance(s, dict):
                state["streak"][str(lang)] = {"now": _int(s.get("now")), "best": _int(s.get("best"))}
    if isinstance(raw.get("daily"), dict):
        for lang, d in raw["daily"].items():
            if not isinstance(d, dict) or not isinstance(d.get("ids"), list):
                continue
            results = d.get("results") if isinstance(d.get("results"), dict) else {}
            state["daily"][str(lang)] = {
                "day": str(d.get("day") or ""),
                "ids": [str(i) for i in d["ids"]],
                "results": {str(k): bool(v) for k, v in results.items()},
            }
    return state


# ── gotchas_user.json ───────────────────────────────────────────────────


def _fresh_user() -> dict[str, Any]:
    return {"version": VERSION, "next": 1, "cards": []}


def _clean_user(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict) or not isinstance(raw.get("cards", []), list):
        return None
    state = _fresh_user()
    state["next"] = max(1, _int(raw.get("next"), 1))
    seen: set[str] = set()
    for c in raw.get("cards", []):
        if not isinstance(c, dict):
            continue
        wrong = c.get("wrong")
        if not (isinstance(c.get("id"), str) and c.get("language") in LANGUAGES
                and isinstance(c.get("code"), str) and isinstance(c.get("answer"), str)
                and isinstance(wrong, list) and 1 <= len(wrong) <= 3
                and all(isinstance(w, str) for w in wrong)) or c["id"] in seen:
            continue
        seen.add(c["id"])
        state["cards"].append({
            "id": c["id"], "language": c["language"], "code": c["code"], "answer": c["answer"],
            "wrong": list(wrong), "raises": bool(c.get("raises")),
            "trap": str(c.get("trap") or "Added by you"), "why": str(c.get("why") or ""),
            "added": str(c.get("added") or ""),
        })
    return state


def _user_item(c: dict[str, Any]) -> Item:
    return Item(id=c["id"], language=c["language"], code=c["code"], answer=c["answer"],
                wrong=tuple(c["wrong"]), trap=c["trap"], why=c["why"], raises=c["raises"],
                mine=True, added=c["added"])


# ── Serving a card: the options, shuffled the same way every time ──────────


def _digest(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16)


def served_options(item: Item, index: int | None = None) -> tuple[list[str], int]:
    """The options in the order they are shown, and where the right one sits.

    The order is fixed by the card alone, so it is the same on every request and every restart.
    A built-in card (`index` = its place in its language's deck) takes its spot from a
    block-wise balanced shuffle - every run of four consecutive cards uses each letter once - so
    the right answer is spread evenly over A-D. A card the user added is placed by its id."""
    options = list(item.options)
    n = len(options)
    if sorted(options) == ["A", "B", "C", "D"]:
        # Options that are themselves the letters A-D are shown in order: buttons labelled A-D that
        # hold C, A, D, B would be a puzzle of their own.
        return sorted(options), sorted(options).index(item.answer)
    if index is not None and n == 4:
        perm = random.Random(f"gotchas:{item.language}:{index // 4}").sample(range(4), 4)
        spot = perm[index % 4]
    else:
        spot = _digest(f"gotchas:{item.id}") % n
    wrong = list(item.wrong)
    random.Random(f"gotchas:{item.id}").shuffle(wrong)
    shown = wrong[:spot] + [item.answer] + wrong[spot:]
    return shown, spot


def card_title(item: Item) -> str:
    """A short name for a card from its id: py-score-90 is "Score 90", mine-3 is "Your card 3"."""
    slug = item.id.partition("-")[2]
    if item.mine:
        return f"Your card {slug}"
    return slug.replace("-", " ").capitalize() or item.id


def sort_traps(traps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sure-but-wrong first, then most misses, then most recent (day, then answer count), then id."""
    out = sorted(traps, key=lambda t: t["id"])
    out.sort(key=lambda t: t["last_tick"], reverse=True)
    out.sort(key=lambda t: t["last_day"], reverse=True)
    out.sort(key=lambda t: t["misses"], reverse=True)
    out.sort(key=lambda t: t["sure_wrong"] < 1)
    return out


class GotchaStore:
    """The deck, the stats, the Daily 5 and the user's own cards."""

    def __init__(self, path: Path | None = None, user_path: Path | None = None,
                 clock: Callable[[], date] = date.today, rng: Any = None,
                 builtin: Callable[[str], tuple[Item, ...]] | None = None) -> None:
        self._path = path
        self._user_path = user_path
        self.clock = clock
        self.rng = rng if rng is not None else random.Random()
        self._builtin = builtin
        self._lock = threading.RLock()

    # ── files ───────────────────────────────────────────────────────────

    @property
    def path(self) -> Path:
        return self._path if self._path is not None else _beside_progress("gotchas.json")

    @property
    def user_path(self) -> Path:
        return self._user_path if self._user_path is not None else _beside_progress("gotchas_user.json")

    def _load(self) -> dict[str, Any]:
        return _read(self.path, _clean, _fresh, "gotchas")

    def _save(self, state: dict[str, Any]) -> None:
        _write_json(self.path, state)

    def _load_user(self) -> dict[str, Any]:
        return _read(self.user_path, _clean_user, _fresh_user, "gotchas_user")

    # ── the deck ────────────────────────────────────────────────────────

    def builtin(self, language: str) -> tuple[Item, ...]:
        if self._builtin is not None:
            return self._builtin(language)
        from . import builtin_deck

        return builtin_deck(language)

    def counts(self, languages: list[str] | tuple[str, ...]) -> dict[str, int]:
        """How many cards each language has (built in plus yours), reading the user's file once."""
        user = self._load_user()["cards"]
        return {lang: len(self.builtin(lang)) + sum(1 for c in user if c["language"] == lang)
                for lang in languages}

    def mine(self, language: str) -> list[Item]:
        return [_user_item(c) for c in self._load_user()["cards"] if c["language"] == language]

    def deck(self, language: str) -> list[Item]:
        if language not in LANGUAGES:
            raise UnknownCard(f"unknown language {language!r}")
        return [*self.builtin(language), *self.mine(language)]

    def find(self, language: str, item_id: str) -> tuple[Item, int | None]:
        """The card and its place in the built-in deck (None for a card the user added)."""
        if language not in LANGUAGES:
            raise UnknownCard(f"unknown language {language!r}")
        for i, it in enumerate(self.builtin(language)):
            if it.id == item_id:
                return it, i
        for it in self.mine(language):
            if it.id == item_id:
                return it, None
        raise UnknownCard(f"no card {item_id!r} in {language}")

    def present(self, item: Item) -> dict[str, Any]:
        """A card as the browser gets it before answering: no answer, no trap, no explanation."""
        _, index = self.find(item.language, item.id)
        options, _spot = served_options(item, index)
        return {"id": item.id, "language": item.language, "code": item.code, "options": options,
                "mine": item.mine}

    # ── serving ─────────────────────────────────────────────────────────

    def pick(self, language: str, exclude: set[str] | frozenset[str] = frozenset(),
             daily: bool = False) -> tuple[Item, str]:
        """The next card and why it was chosen: "yours", "new", "again" or "review"."""
        with self._lock:
            state = self._load()
            deck = self.deck(language)
            stats = state["stats"]
            tick = state["ticks"].get(language, 0)

            def stat(it: Item) -> dict[str, Any]:
                return stats.get(f"{language}:{it.id}", _blank_stat())

            if daily:
                plan = self._daily_saved(state, language)
                todo = [it for it in deck if it.id in plan["ids"] and it.id not in plan["results"]]
                todo.sort(key=lambda it: plan["ids"].index(it.id))
                if todo:
                    return todo[0], "daily"
            pool = [it for it in deck if it.id not in exclude] or deck
            if not pool:
                raise UnknownCard("the deck is empty")

            fresh = [it for it in pool if it.mine and stat(it)["seen"] == 0]
            if fresh:
                return fresh[0], "yours"
            builtin = self.builtin(language)
            if sum(1 for it in builtin if stat(it)["seen"]) < LEAD:
                lead = [it for it in builtin[:LEAD] if stat(it)["seen"] == 0 and it in pool]
                if lead:
                    return lead[0], "new"
            due = [it for it in pool if stat(it)["due"] is not None and stat(it)["due"] <= tick]
            if due:
                return min(due, key=lambda it: (DUE_RANK.get(stat(it)["due_kind"], 1), stat(it)["due"],
                                                stat(it)["last_tick"])), "again"
            unseen = [it for it in pool if stat(it)["seen"] == 0]
            if unseen:
                return self.rng.choice(unseen), "new"
            oldest = min(stat(it)["last_tick"] for it in pool)
            return self.rng.choice([it for it in pool if stat(it)["last_tick"] == oldest]), "review"

    # ── answering ───────────────────────────────────────────────────────

    def answer(self, language: str, item_id: str, chosen: int, confidence: Any = "",
               note: Any = "") -> dict[str, Any]:
        """Mark an answer. `confidence` ("sure", "guess"; anything else counts as "") and `note` (your own
        reasoning, trimmed and cut to 300 characters) are optional and never change the score or the XP; they
        change when the card comes back (see the module notes) and what `traps()` says about it."""
        confidence = clean_confidence(confidence)
        note = clean_note(note)
        item, index = self.find(language, item_id)
        options, spot = served_options(item, index)
        if not isinstance(chosen, int) or isinstance(chosen, bool) or not 0 <= chosen < len(options):
            raise BadChoice(f"choose 0-{len(options) - 1}")
        correct = chosen == spot
        with self._lock:
            state = self._load()
            today = self.clock().isoformat()
            plan = self._daily(state, language)  # made first, from the record as it stood this morning
            tick = state["ticks"].get(language, 0) + 1
            state["ticks"][language] = tick
            key = f"{language}:{item.id}"
            st = state["stats"].setdefault(key, _blank_stat())
            st["seen"] += 1
            st["right"] += 1 if correct else 0
            st["last_day"], st["last_tick"] = today, tick
            if confidence:
                st[f"{confidence}_{'right' if correct else 'wrong'}"] += 1
            st["sure_run"] = st["sure_run"] + 1 if correct and confidence == "sure" else 0
            if correct:
                kind = "shaky" if confidence == "guess" else None
            else:
                kind = "sure_wrong" if confidence == "sure" else "miss"
            st["due_kind"] = kind
            st["due"] = tick + return_offset(kind, key, tick) if kind else None
            if note:
                st["note"] = note
                st["notes"] = [*st["notes"], {"day": today, "note": note, "correct": correct}][-NOTE_KEEP:]
            run = state["streak"].setdefault(language, {"now": 0, "best": 0})
            run["now"] = run["now"] + 1 if correct else 0
            run["best"] = max(run["best"], run["now"])
            just_done = False
            if item.id in plan["ids"] and item.id not in plan["results"]:
                plan["results"][item.id] = correct
                just_done = all(i in plan["results"] for i in plan["ids"])
            self._save(state)
            return {
                "correct": correct, "answer": item.answer, "answer_index": spot, "chosen": chosen,
                "trap": item.trap, "why": item.why, "mine": item.mine,
                "streak": run["now"], "streak_best": run["best"], "seen_before": st["seen"] - 1,
                "again_soon": not correct,
                "confidence": confidence, "comes_back": st["due"] is not None, "note": note,
                "daily": {**self._daily_view(plan), "just_completed": just_done},
                "summary": {**self._summary(state, language), "daily": self._daily_view(plan)},
            }

    # ── the Daily 5 ─────────────────────────────────────────────────────

    def _daily(self, state: dict[str, Any], language: str) -> dict[str, Any]:
        """Today's set for a language (made, and kept in `state`, on first use today).

        Five cards, chosen by a generator seeded by the date and the language, from the built-in
        deck, favouring cards you missed (weight 4) and have not seen (3) over ones you got right (1).
        Kept in the file, so it is the same set all day however your stats move meanwhile."""
        today = self.clock().isoformat()
        plan = state["daily"].get(language)
        live = {it.id for it in self.deck(language)}
        if plan and plan["day"] == today:
            plan["ids"] = [i for i in plan["ids"] if i in live]
            plan["results"] = {k: v for k, v in plan["results"].items() if k in plan["ids"]}
            if plan["ids"]:
                return plan
        pool = list(self.builtin(language))
        stats = state["stats"]

        def weight(it: Item) -> int:
            s = stats.get(f"{language}:{it.id}")
            if not s or not s["seen"]:
                return 3
            return 4 if s["due"] is not None else 1

        rng = random.Random(_digest(f"daily:{today}:{language}"))
        ids: list[str] = []
        while pool and len(ids) < DAILY_SIZE:
            pick = rng.choices(pool, weights=[weight(it) for it in pool])[0]
            pool.remove(pick)
            ids.append(pick.id)
        state["daily"][language] = {"day": today, "ids": ids, "results": {}}
        return state["daily"][language]

    def _daily_saved(self, state: dict[str, Any], language: str) -> dict[str, Any]:
        """`_daily`, writing the file only when today's set was just made or tidied."""
        before = repr(state["daily"].get(language))
        plan = self._daily(state, language)
        if repr(plan) != before:
            self._save(state)
        return plan

    @staticmethod
    def _daily_view(plan: dict[str, Any]) -> dict[str, Any]:
        dots = ["todo" if i not in plan["results"] else ("right" if plan["results"][i] else "wrong")
                for i in plan["ids"]]
        done = sum(1 for d in dots if d != "todo")
        return {"day": plan["day"], "total": len(plan["ids"]), "done": done,
                "complete": bool(plan["ids"]) and done == len(plan["ids"]), "dots": dots}

    def daily(self, language: str) -> dict[str, Any]:
        with self._lock:
            state = self._load()
            return self._daily_view(self._daily_saved(state, language))

    # ── My traps ────────────────────────────────────────────────────────

    def traps(self, languages: list[str] | tuple[str, ...]) -> list[dict[str, Any]]:
        """The cards you have missed and not yet mastered, in the languages given.

        The rule, in full: a card is a trap when you have answered it WRONG at least once and your last two
        answers have not both been right-and-Sure (`sure_run < MASTERED_RUN`). Only cards you have answered are
        ever listed (a card with no record is never here), so showing the code, the trap and the why spoils
        nothing; cards of your own are included on the same terms; a record whose card no longer exists in its
        deck is skipped. Order: a card you were sure about and got wrong first, then the most misses, then the
        most recent (the same rule is `sortTraps` in lib/gotchas.ts)."""
        from .langs import get

        with self._lock:
            state = self._load()
            out: list[dict[str, Any]] = []
            for language in languages:
                if language not in LANGUAGES:
                    continue
                deck = {it.id: it for it in self.deck(language)}
                for key, s in state["stats"].items():
                    lang, _, card_id = key.partition(":")
                    item = deck.get(card_id) if lang == language else None
                    misses = s["seen"] - s["right"]
                    if item is None or misses < 1 or s["sure_run"] >= MASTERED_RUN:
                        continue
                    out.append({
                        "id": item.id, "language": language, "language_name": get(language).name,
                        "title": card_title(item), "code": item.code, "trap": item.trap, "why": item.why,
                        "mine": item.mine, "misses": misses, "sure_wrong": s["sure_wrong"],
                        "guess_wrong": s["guess_wrong"], "shaky": s["due_kind"] == "shaky",
                        "note": s["note"], "last_day": s["last_day"], "last_tick": s["last_tick"],
                    })
            return sort_traps(out)

    # ── summaries ───────────────────────────────────────────────────────

    def _summary(self, state: dict[str, Any], language: str) -> dict[str, Any]:
        deck = self.deck(language)
        stats = [state["stats"].get(f"{language}:{it.id}") for it in deck]
        run = state["streak"].get(language, {"now": 0, "best": 0})
        return {
            "language": language, "total": len(deck),
            "seen": sum(1 for s in stats if s and s["seen"]),
            "right": sum(1 for s in stats if s and s["right"]),
            "mine": sum(1 for it in deck if it.mine),
            "streak": run["now"], "streak_best": run["best"],
        }

    def summary(self, language: str) -> dict[str, Any]:
        if language not in LANGUAGES:
            raise UnknownCard(f"unknown language {language!r}")
        with self._lock:
            state = self._load()
            plan = self._daily_saved(state, language)
            return {**self._summary(state, language), "daily": self._daily_view(plan)}

    # ── the user's own cards ────────────────────────────────────────────

    def add_card(self, language: str, code: str, answer: str, wrong: list[str], raises: bool,
                 trap: str, why: str) -> Item:
        with self._lock:
            user = self._load_user()
            if len(user["cards"]) >= MAX_USER_CARDS:
                raise ValueError(f"You already have {MAX_USER_CARDS} cards of your own; delete some first.")
            card = {"id": f"mine-{user['next']}", "language": language, "code": code, "answer": answer,
                    "wrong": list(wrong), "raises": raises, "trap": trap, "why": why,
                    "added": self.clock().isoformat()}
            user["next"] += 1
            user["cards"].append(card)
            _write_json(self.user_path, user)
            return _user_item(card)

    def delete_card(self, language: str, item_id: str) -> bool:
        with self._lock:
            user = self._load_user()
            keep = [c for c in user["cards"] if not (c["id"] == item_id and c["language"] == language)]
            if len(keep) == len(user["cards"]):
                return False
            user["cards"] = keep
            _write_json(self.user_path, user)
            state = self._load()
            state["stats"].pop(f"{language}:{item_id}", None)
            self._save(state)
            return True

    def my_cards(self, language: str | None = None) -> list[Item]:
        return [_user_item(c) for c in self._load_user()["cards"]
                if language is None or c["language"] == language]
