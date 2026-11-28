"""Slides: the decks' shape, the oracle (every program really prints its `output`), and the routes.

The oracle rule: each slide's `output` was worked out by hand when the slide was written. Here every
`code` is run with the real Python in a bare environment (-I, a scratch directory) and its stdout
must equal `output` exactly. Nothing here touches ~/.code_coach.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile

import pytest

from code_coach import slides

PY_DECKS = slides.decks_for("python")
ALL_SLIDES = [(d.id, i, s) for d in slides.DECKS for i, s in enumerate(d.slides)]
SLIDE_IDS = [f"{d}-{i + 1}" for d, i, _ in ALL_SLIDES]


def test_there_are_three_python_decks():
    ids = {d.id for d in PY_DECKS}
    assert {"py-types", "py-syntax", "py-patterns"} <= ids


def test_deck_ids_unique_and_languages_set():
    ids = [d.id for d in slides.DECKS]
    assert len(ids) == len(set(ids))
    for d in slides.DECKS:
        assert d.language and d.title.strip() and d.blurb.strip()


@pytest.mark.parametrize("d", PY_DECKS, ids=lambda d: d.id)
def test_python_decks_have_enough_slides(d):
    assert len(d.slides) >= 12


@pytest.mark.parametrize("deck_id,i,s", ALL_SLIDES, ids=SLIDE_IDS)
def test_slide_shape(deck_id, i, s):
    assert 0 < len(s.title) <= 40
    assert 0 < len(s.text) <= 300
    assert s.text.count(". ") + s.text.count("; ") <= 4  # a few plain sentences, not a lecture
    assert s.point.strip() and "\n" not in s.point and len(s.point) <= 120
    if s.code:
        lines = s.code.splitlines()
        assert len(lines) <= 10, f"{deck_id} slide {i + 1} has {len(lines)} code lines"
        assert not s.code.endswith("\n")
        assert s.output.strip(), "a slide with code must show what it prints"
        assert not s.output.endswith("\n")
    else:
        assert s.output == ""


@pytest.mark.parametrize("deck_id,i,s", [x for x in ALL_SLIDES if x[2].code], ids=[
    f"{d}-{i + 1}" for d, i, s in ALL_SLIDES if s.code
])
def test_oracle_code_prints_its_output(deck_id, i, s):
    with tempfile.TemporaryDirectory(prefix="slides_oracle_") as scratch:
        ran = subprocess.run(
            [sys.executable, "-I", "-c", s.code],
            capture_output=True, text=True, encoding="utf-8", timeout=30, cwd=scratch,
        )
    assert ran.returncode == 0, ran.stderr[-1500:]
    assert ran.stdout == s.output + "\n", f"{deck_id} slide {i + 1} ({s.title})"


# -- the routes (called directly, like the other API tests) ----------------------------------------


def test_list_for_python():
    from code_coach.api.server import slides_list

    got = slides_list(language="python")
    assert {d["id"] for d in got["decks"]} >= {"py-types", "py-syntax", "py-patterns"}
    by_id = {d["id"]: d for d in got["decks"]}
    assert by_id["py-types"]["count"] == len(slides.deck("py-types").slides)
    assert set(by_id["py-types"]) == {"id", "title", "blurb", "count"}


def test_list_for_a_language_with_no_decks_is_empty_not_an_error():
    from code_coach.api.server import slides_list

    assert slides_list(language="rust")["decks"] == []


def test_one_deck_comes_whole():
    from code_coach.api.server import slides_deck

    got = slides_deck("py-syntax")
    assert got["id"] == "py-syntax" and got["language"] == "python"
    assert len(got["slides"]) == len(slides.deck("py-syntax").slides)
    assert set(got["slides"][0]) == {"title", "text", "code", "output", "point"}
    assert got["syntax"] and "keywords" in got["syntax"]


def test_unknown_deck_is_404():
    from fastapi import HTTPException

    from code_coach.api.server import slides_deck

    with pytest.raises(HTTPException) as err:
        slides_deck("nope")
    assert err.value.status_code == 404


def test_every_deck_module_loads_and_the_beginner_decks_come_first():
    """Decks are found by file name (`content_*.py` with a DECK); a broken one is skipped and named here."""
    assert slides.LOAD_ERRORS == {}
    ids = [d.id for d in slides.decks_for("python")]
    assert ids[:3] == ["py-types", "py-syntax", "py-patterns"], ids
