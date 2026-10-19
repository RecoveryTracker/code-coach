"""'Add a quiz I found': turn code the user pasted into a card, with the truth taken from a real run.

Everything is typed or pasted by the user; nothing is fetched from anywhere. The code is run for real
(`runner.run_program`, same limits as Run it: 5 s, no input, a bare environment), twice, and only a program
that prints the same thing both times can become a card. What it printed is the correct option - whatever
the user thought. The options they typed are kept as the misreads; blank slots are filled only by the cheap
generators below, each of which makes a mistake a person really makes (an item dropped, a boolean flipped, a
number off by one, only the first line). If none of them applies the card simply has fewer options (never
fewer than two) rather than a made-up one.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .runner import LIMIT_SECONDS, RunnerUnavailable, error_name, last_error_line, run_program

MAX_LINES = 60
MAX_CODE = 4_000
MAX_OPTION = 200
MAX_WHY = 400
MAX_ANSWER_LINES = 10
MAX_ANSWER = 300
OPTION_SLOTS = 4


class CardRefused(ValueError):
    """The pasted code cannot become a card; the message says why, in words for the person."""


@dataclass
class Built:
    answer: str
    wrong: list[str]
    raises: bool
    note: str = ""
    stdout: str = ""
    #: What the user typed, as found: did one of their options match the real output?
    matched: bool | None = None
    notes: list[str] = field(default_factory=list)


def norm(text: str) -> str:
    """Compare outputs the way a person does: whitespace and a trailing newline do not count."""
    return " ".join(text.split())


# ── Distractors that are honest ─────────────────────────────────────────


def _split_top(inner: str) -> list[str]:
    """Split on commas that are not inside brackets or quotes."""
    parts, depth, quote, cur, i = [], 0, "", [], 0
    while i < len(inner):
        ch = inner[i]
        if quote:
            cur.append(ch)
            if ch == "\\" and i + 1 < len(inner):
                cur.append(inner[i + 1])
                i += 1
            elif ch == quote:
                quote = ""
        elif ch in "\"'`":
            quote = ch
            cur.append(ch)
        elif ch in "([{":
            depth += 1
            cur.append(ch)
        elif ch in ")]}":
            depth -= 1
            cur.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
        i += 1
    parts.append("".join(cur).strip())
    return [p for p in parts if p]


_CONTAINER = re.compile(r"^([\[({]\s?)(.*?)(\s?[\])}])$", re.S)


def generate_distractors(real: str) -> list[str]:
    """Plausible, honest misreads of a real output, best first. Possibly none."""
    text = real.strip()
    out: list[str] = []
    lines = text.splitlines()
    if len(lines) >= 2:
        out.append(lines[0])
        if len(lines) >= 3:
            out.append("\n".join(lines[:-1]))
        return out
    if text in ("True", "False"):
        return ["False" if text == "True" else "True"]
    if text in ("true", "false"):
        return ["false" if text == "true" else "true"]
    if re.fullmatch(r"-?\d+", text):
        n = int(text)
        return [str(n + 1), str(n - 1)] if n != 0 else ["1", "-1"]
    m = _CONTAINER.match(text)
    if m:
        items = _split_top(m.group(2))
        if len(items) >= 2:
            head, tail = m.group(1), m.group(3)
            out.append(f"{head}{', '.join(items[:-1])}{tail}")
            out.append(f"{head}{', '.join(items[1:])}{tail}")
            return out
    words = text.split(" ")
    if len(words) >= 2 and all(w for w in words):
        return [" ".join(words[:-1]), " ".join(words[1:])]
    return out


# ── The card ────────────────────────────────────────────────────────────


def check_code(code: str) -> str:
    code = code.replace("\r\n", "\n").strip("\n")
    if not code.strip():
        raise CardRefused("Paste the program first - there is nothing to run.")
    if len(code.splitlines()) > MAX_LINES or len(code) > MAX_CODE:
        raise CardRefused(f"That is too long for a card: keep it to {MAX_LINES} lines.")
    return code


def run_for_truth(language: str, code: str) -> tuple[str, bool]:
    """(what it printed, whether it died with an error). Refuses anything that cannot be a fair question."""
    try:
        first = run_program(language, code, hashseed=0)
        if not first.timed_out:
            second = run_program(language, code, hashseed=1)
    except RunnerUnavailable as exc:
        raise CardRefused(str(exc)) from None
    if first.timed_out or second.timed_out:
        raise CardRefused(f"It ran for longer than {LIMIT_SECONDS:g} seconds, so it cannot be a quick question.")
    if "EOFError" in first.stderr or re.search(r"\binput\s*\(", code) and language == "python":
        raise CardRefused("It waits for input; a card has to run on its own.")
    if re.search(r"\b(prompt|readline)\s*\(", code) and language == "javascript":
        raise CardRefused("It waits for input; a card has to run on its own.")
    if (first.stdout, error_name(language, first), first.returncode == 0) != \
       (second.stdout, error_name(language, second), second.returncode == 0):
        raise CardRefused("It prints something different each time it runs (random, the clock or the order "
                          "of a set), so there is no single right answer.")
    if first.ok:
        out = first.stdout.rstrip()
        if not out.strip():
            raise CardRefused("It ran but printed nothing, so there is no answer to guess. Add a print.")
        return out, False
    err = error_name(language, first)
    if first.stdout.strip() or not err or err in ("SyntaxError", "IndentationError", "TabError"):
        raise CardRefused("It stopped with an error"
                          + (f" ({last_error_line(first)})" if last_error_line(first) else "")
                          + ", after printing" + (" something" if first.stdout.strip() else " nothing")
                          + ". A card needs a program that finishes, or one that fails straight away with a clear error.")
    return err, True


def build(language: str, code: str, options: list[str] | None = None, guess: int | None = None) -> Built:
    """Run the code and build the options. Raises CardRefused with a plain-words reason."""
    code = check_code(code)
    typed_all = [(o or "").strip() for o in (options or [])][:OPTION_SLOTS]
    if any(len(o) > MAX_OPTION for o in typed_all):
        raise CardRefused(f"An option is too long (over {MAX_OPTION} characters).")
    if guess is not None and not (0 <= guess < len(typed_all) and typed_all[guess]):
        guess = None
    real, raises = run_for_truth(language, code)
    if len(real.splitlines()) > MAX_ANSWER_LINES or len(real) > MAX_ANSWER:
        raise CardRefused("It prints too much for a card: a question has one short answer.")

    notes: list[str] = []
    typed: list[tuple[int, str]] = [(i, o) for i, o in enumerate(typed_all) if o]
    seen: set[str] = set()
    unique: list[tuple[int, str]] = []
    for i, o in typed:
        if norm(o) not in seen:
            seen.add(norm(o))
            unique.append((i, o))
    matched = [i for i, o in unique if norm(o) == norm(real)]
    wrong = [o for i, o in unique if norm(o) != norm(real)]
    verdict: bool | None = None
    if unique:
        verdict = bool(matched)
        if not matched:
            notes.append("None of the options you typed match what it actually prints.")
            if len(unique) >= OPTION_SLOTS:
                # No room: the real output takes the place of the option they believed was right
                # (or, if they did not say, the last one typed).
                drop = guess if guess is not None and typed_all[guess] in wrong else None
                if drop is not None:
                    wrong.remove(typed_all[drop])
                else:
                    wrong = wrong[:-1]
                notes.append("The real output took the place of one of your options.")
    wrong = wrong[:OPTION_SLOTS - 1]
    for cand in generate_distractors(real):
        if len(wrong) >= OPTION_SLOTS - 1:
            break
        if norm(cand) and norm(cand) != norm(real) and norm(cand) not in {norm(w) for w in wrong}:
            wrong.append(cand)
    if not wrong:
        raise CardRefused("It prints a single value I cannot honestly make a second option for. Type at least "
                          "one other option you saw, and try again.")
    if guess is not None:
        notes.append("Your pick was right." if norm(typed_all[guess]) == norm(real)
                     else "Your pick was not what it prints.")
    return Built(answer=real, wrong=wrong, raises=raises, stdout=real, matched=verdict, notes=notes)


def why_text(real: str, raises: bool, note: str) -> str:
    note = " ".join((note or "").split())[:MAX_WHY]
    if note:
        return note
    if raises:
        return f"Added by you - it stopped with a {real}."
    shown = real if len(real) <= 60 and "\n" not in real else real.splitlines()[0][:60] + " ..."
    return f"Added by you - it printed {shown}"
