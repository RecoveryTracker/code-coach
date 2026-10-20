"""Gotchas' built-in cards: every marked answer is held to a real run.

The oracle rule, strictly: the answer written in code_coach/gotchas/content_*.py is never trusted. Each card's
program is run in the real interpreter (python, with three different PYTHONHASHSEED values; node, twice) with
this file's own subprocess call - not the app's runner - and what it printed must be exactly the marked answer.
The three wrong options must not be what it printed, nor each other, once whitespace is ignored.

Cards the user adds are a different thing (tests/test_gotchas_store.py) and never reach this file: it reads
`DECKS`, the built-in content only.
"""

from __future__ import annotations

import functools
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from code_coach.gotchas import DECKS, served_options
from code_coach.gotchas.content_js import ITEMS as JS_ITEMS_1
from code_coach.gotchas.content_js2 import ITEMS as JS_ITEMS_2
from code_coach.gotchas.content_py import ITEMS as PY_ITEMS_1
from code_coach.gotchas.content_py2 import ITEMS as PY_ITEMS_2

#: The whole built-in deck, in the order it is served (the first modules, then the later ones).
PY_ITEMS = DECKS["python"]
JS_ITEMS = DECKS["javascript"]

NODE = shutil.which("node")
ALL = [*PY_ITEMS, *JS_ITEMS]
HASH_SEEDS = (0, 1, 4242)
LIMIT = 5.0


def _norm(text: str) -> str:
    return " ".join(text.split())


def _run(item, seed: int) -> tuple[int, str, str, float]:
    """(exit code, stdout, stderr, seconds) of the card's program in a fresh folder."""
    folder = Path(tempfile.mkdtemp(prefix="gotcha_oracle_"))
    try:
        if item.language == "python":
            script = folder / "card.py"
            command = [sys.executable, "-X", "utf8", str(script)]
        else:
            script = folder / "card.js"
            command = [NODE, str(script)]
        script.write_text(item.code + "\n", encoding="utf-8")
        env = {k: v for k, v in os.environ.items() if not k.startswith("PYTHON")}
        env["PYTHONHASHSEED"] = str(seed)
        started = time.monotonic()
        done = subprocess.run(command, cwd=folder, env=env, capture_output=True, text=True,
                              encoding="utf-8", timeout=LIMIT * 3, stdin=subprocess.DEVNULL)
        return done.returncode, done.stdout, done.stderr, time.monotonic() - started
    finally:
        shutil.rmtree(folder, ignore_errors=True)


@functools.cache
def runs() -> dict[str, list[tuple[int, str, str, float]]]:
    """Every card's real runs: Python once per hash seed, JavaScript twice."""
    jobs = []
    for item in ALL:
        if item.language == "javascript" and NODE is None:
            continue
        seeds = HASH_SEEDS if item.language == "python" else (0, 1)
        jobs.extend((item, seed) for seed in seeds)
    with ThreadPoolExecutor(4) as pool:
        results = list(pool.map(lambda job: _run(*job), jobs))
    out: dict[str, list] = {}
    for (item, _seed), res in zip(jobs, results):
        out.setdefault(item.id, []).append(res)
    return out


needs_node = pytest.mark.skipif(NODE is None, reason="needs node on the PATH")


def _items_runnable():
    return [it for it in ALL if it.language == "python" or NODE is not None]


# ── The deck itself ─────────────────────────────────────────────────────


def test_there_are_enough_cards():
    assert len(PY_ITEMS) >= 60
    assert len(JS_ITEMS) >= 40
    # the deck is the modules in order, and the later modules only ever add cards after the old ones
    assert PY_ITEMS == (*PY_ITEMS_1, *PY_ITEMS_2)
    assert JS_ITEMS == (*JS_ITEMS_1, *JS_ITEMS_2)
    assert len(PY_ITEMS_1) >= 90 and len(JS_ITEMS_1) >= 72


def test_the_first_cards_are_the_two_the_mode_started_from():
    first, second = PY_ITEMS[0], PY_ITEMS[1]
    assert first.id == "py-score-90" and "score = 90" in first.code
    assert second.id == "py-loop-var-list" and "for i in arr" in second.code
    assert second.wrong == ("[2, 4, 6]", "[1, 4, 9]", "Error")


def test_ids_are_unique_and_prefixed_by_language():
    ids = [it.id for it in ALL]
    assert len(ids) == len(set(ids))
    assert all(it.id.startswith("py-") for it in PY_ITEMS)
    assert all(it.id.startswith("js-") for it in JS_ITEMS)
    assert all(it.language == "python" for it in PY_ITEMS)
    assert all(it.language == "javascript" for it in JS_ITEMS)
    assert not any(it.mine for it in ALL), "built-in content never holds a card the user added"


def test_every_card_is_complete():
    for it in ALL:
        assert it.code.strip(), it.id
        assert len(it.wrong) == 3, it.id
        assert it.trap.strip() and len(it.trap) <= 100, it.id
        assert it.why.strip(), it.id
        sentences = [s for s in re.split(r"(?<=[.!?])\s+", it.why.strip()) if s]
        assert 1 <= len(sentences) <= 4, f"{it.id}: the explanation is {len(sentences)} sentences"
        assert it.answer.strip() and all(w.strip() for w in it.wrong), it.id


def test_the_four_options_differ_even_ignoring_whitespace():
    for it in ALL:
        normalised = [_norm(o) for o in it.options]
        assert len(set(normalised)) == 4, f"{it.id}: options collide after normalising whitespace: {it.options}"
        for wrong in it.wrong:
            assert _norm(wrong) != _norm(it.answer), it.id


def test_no_card_depends_on_randomness_the_clock_or_identity():
    banned = re.compile(r"\brandom\b|\bMath\.random\b|\bDate\.now\b|\bnew Date\(\s*\)|\bDate\(\s*\)|\btime\b"
                        r"|\bid\(|\bhash\(|\bdatetime\b"
                        r"|\bos\.environ\b|\binput\(|\bprocess\.argv\b")
    for it in ALL:
        assert not banned.search(it.code), f"{it.id} uses something that can differ between runs"


def test_each_card_is_one_short_program():
    for it in ALL:
        assert len(it.code.splitlines()) <= 16, it.id
        assert max(len(line) for line in it.code.splitlines()) <= 76, f"{it.id} has a very wide line"


def test_each_answer_is_one_line():
    for it in ALL:
        for option in it.options:
            assert "\n" not in option, it.id


# ── The oracle ──────────────────────────────────────────────────────────


def test_python_answers_are_what_python_prints():
    wrong = []
    for it in PY_ITEMS:
        for code, out, err, _secs in runs()[it.id]:
            if it.raises:
                ok = code != 0 and not out.strip() and re.search(rf"^{re.escape(it.answer)}\b", err, re.M)
            else:
                ok = code == 0 and out.strip() == it.answer
            if not ok:
                wrong.append((it.id, it.answer, out.strip(), err.strip()[-120:]))
    assert wrong == []


@needs_node
def test_javascript_answers_are_what_node_prints():
    wrong = []
    for it in JS_ITEMS:
        for code, out, err, _secs in runs()[it.id]:
            if it.raises:
                ok = code != 0 and not out.strip() and re.search(rf"^{re.escape(it.answer)}:", err, re.M)
            else:
                ok = code == 0 and out.strip() == it.answer
            if not ok:
                wrong.append((it.id, it.answer, out.strip(), err.strip()[-120:]))
    assert wrong == []


def test_no_wrong_option_is_what_the_program_really_prints():
    for it in _items_runnable():
        _code, out, _err, _secs = runs()[it.id][0]
        real = _norm(out) if not it.raises else _norm(it.answer)
        for wrong in it.wrong:
            assert _norm(wrong) != real, f"{it.id}: a 'wrong' option is the real output"


def test_every_card_prints_the_same_thing_on_every_run():
    for it in _items_runnable():
        outputs = {(out, code) for code, out, _err, _secs in runs()[it.id]}
        assert len(outputs) == 1, f"{it.id} differs between runs: {outputs}"


def test_nothing_takes_five_seconds():
    for it in _items_runnable():
        for _code, _out, _err, secs in runs()[it.id]:
            assert secs < LIMIT, f"{it.id} took {secs:.1f}s"


# ── What is served ──────────────────────────────────────────────────────


def test_served_positions_are_spread_over_all_four_letters():
    for language, deck in DECKS.items():
        spots = Counter(served_options(it, i)[1] for i, it in enumerate(deck))
        assert set(spots) == {0, 1, 2, 3}, language
        for letter, n in spots.items():
            share = n / len(deck)
            assert 0.2 <= share <= 0.3, f"{language}: letter {'ABCD'[letter]} holds the answer {share:.0%} of the time"


def test_every_four_in_a_row_use_each_letter_once():
    for deck in DECKS.values():
        for start in range(0, len(deck) - 3, 4):
            block = [served_options(deck[start + k], start + k)[1] for k in range(4)]
            if any(sorted(deck[start + k].options) == ["A", "B", "C", "D"] for k in range(4)):
                continue  # letter-answers keep their natural order
            assert sorted(block) == [0, 1, 2, 3], (start, block)


def test_serving_is_deterministic_and_keeps_the_answer_where_it_says():
    for deck in DECKS.values():
        for i, it in enumerate(deck):
            options, spot = served_options(it, i)
            assert served_options(it, i) == (options, spot)
            assert options[spot] == it.answer
            assert sorted(options) == sorted(it.options)


def test_letter_options_are_shown_in_order():
    first = PY_ITEMS[0]
    options, spot = served_options(first, 0)
    assert options == ["A", "B", "C", "D"] and options[spot] == "D"
