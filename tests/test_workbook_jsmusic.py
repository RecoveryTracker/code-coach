"""The "Music" JavaScript pages (248-257).

Written to pass both before and after the pages are registered: the
reference programs and expected outputs are taken from emit_jsmusic
directly, so nothing here depends on the dispatch in emit.py or the
workbook package. Once registered, the checks that go through
Exercise.expect and Exercise.answer switch on as well.

The expected outputs are worked out in Python from the formulas, never by
running the JavaScript; the run test is what proves node prints the same
characters.
"""

from __future__ import annotations

import importlib
import pkgutil
import unittest

import code_coach.workbook as workbook
from code_coach.engine import run_code
from code_coach.workbook import Page, _value, matches, pages
from code_coach.workbook import content_jsmusic, emit_jsmusic
from code_coach.workbook.content_jsmusic import JSMUSIC_PAGES

NEW = [(p, e) for p in JSMUSIC_PAGES for e in p.exercises]
REGISTERED = any(p.id == JSMUSIC_PAGES[0].id for p in pages())
BY_ID = {p.id: p for p in JSMUSIC_PAGES}


def _expect(e) -> str:
    return emit_jsmusic.expected_output(e.shape, e.args, _value)


def _answer(e) -> str:
    code = emit_jsmusic.solution("javascript", e.shape, e.args)
    assert code is not None
    return code


def _others() -> list[Page]:
    """Every page that is not one of these, registered or not.

    A set written alongside this one may not be registered yet, so every
    content module's *_PAGES tuple is read as well as pages(). A module
    that will not import is skipped: it is that set's own test's business.
    """
    mine = {id(p) for p in JSMUSIC_PAGES}
    found = {id(p): p for p in pages() if id(p) not in mine}
    for info in pkgutil.iter_modules(workbook.__path__):
        if not info.name.startswith("content_"):
            continue
        try:
            module = importlib.import_module(f"code_coach.workbook.{info.name}")
        except Exception:  # noqa: BLE001 - a set still being written
            continue
        for name, value in vars(module).items():
            if name.endswith("_PAGES") and isinstance(value, tuple):
                for p in value:
                    if isinstance(p, Page) and id(p) not in mine:
                        found.setdefault(id(p), p)
    return list(found.values())


class ShapeTests(unittest.TestCase):
    def test_ten_pages_of_about_twenty(self) -> None:
        self.assertEqual(len(JSMUSIC_PAGES), 10)
        for p in JSMUSIC_PAGES:
            with self.subTest(page=p.id):
                self.assertTrue(p.id.startswith("js-music-"))
                self.assertTrue(p.name.startswith("Music: "))
                self.assertGreaterEqual(len(p.exercises), 18)
                self.assertLessEqual(len(p.exercises), 22)
                self.assertEqual(len({e.shape for e in p.exercises}), 1)
                self.assertEqual(p.languages, ("javascript",))
                self.assertEqual(p.tier, "intermediate")
                self.assertGreater(len(p.teaches), 20)
                self.assertGreater(len(p.example), 60)

    def test_exercise_ids_follow_the_page(self) -> None:
        for p in JSMUSIC_PAGES:
            for i, e in enumerate(p.exercises, start=1):
                with self.subTest(exercise=e.id):
                    self.assertEqual(e.id, f"{p.id}-{i:02d}")

    def test_every_shape_has_a_page_and_a_note(self) -> None:
        used = [p.exercises[0].shape for p in JSMUSIC_PAGES]
        self.assertEqual(used, list(emit_jsmusic.SHAPE_IDS))
        for shape in emit_jsmusic.SHAPE_IDS:
            with self.subTest(shape=shape):
                self.assertTrue(shape.startswith("js_music_"))
                self.assertTrue(emit_jsmusic.handles(shape))
                self.assertIsNotNone(emit_jsmusic.for_shape(shape))
        self.assertFalse(emit_jsmusic.handles("js_planets_weight"))

    def test_shapes_are_new(self) -> None:
        from code_coach.workbook.emit import all_shape_ids

        mine = set(emit_jsmusic.SHAPE_IDS)
        self.assertEqual(len(mine), len(emit_jsmusic.SHAPE_IDS))
        others = {e.shape for p in _others() for e in p.exercises}
        others |= set(all_shape_ids()) - mine
        self.assertFalse(mine & others)

    def test_ids_are_new(self) -> None:
        mine_pages = {p.id for p in JSMUSIC_PAGES}
        mine_ex = [e.id for _, e in NEW]
        self.assertEqual(len(mine_ex), len(set(mine_ex)))
        self.assertEqual(len(mine_pages), len(JSMUSIC_PAGES))
        others = _others()
        self.assertFalse(mine_pages & {p.id for p in others})
        self.assertFalse(
            set(mine_ex) & {e.id for p in others for e in p.exercises})

    def test_numbers_are_consecutive_and_unused(self) -> None:
        numbers = [p.number for p in JSMUSIC_PAGES]
        self.assertEqual(numbers, list(range(248, 258)))
        mine = {p.id for p in JSMUSIC_PAGES}
        # No other JavaScript page uses these numbers, registered or not;
        # later pages may follow at 258.
        theirs = {p.number for p in pages("javascript") if p.id not in mine}
        theirs |= {p.number for p in _others() if "javascript" in p.languages}
        self.assertFalse(theirs & set(numbers))

    def test_prompts_are_sentences_without_syntax(self) -> None:
        for p, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertGreater(len(e.prompt), 20)
                self.assertTrue(e.prompt.strip().endswith("."))
                for giveaway in ("print(", "console.log", "println", "printf"):
                    self.assertNotIn(giveaway, e.prompt)

    def test_no_two_exercises_on_a_page_are_the_same(self) -> None:
        for p in JSMUSIC_PAGES:
            with self.subTest(page=p.id):
                asked = [(e.prompt, _expect(e)) for e in p.exercises]
                self.assertEqual(len(asked), len(set(asked)))
                prompts = [e.prompt for e in p.exercises]
                self.assertEqual(len(prompts), len(set(prompts)))

    def test_every_exercise_prints_something(self) -> None:
        for _, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertTrue(_expect(e).strip())

    def test_other_languages_get_no_answer(self) -> None:
        for _, e in NEW:
            for language in ("python", "typescript", "dart", "rust"):
                with self.subTest(exercise=e.id, language=language):
                    self.assertIsNone(
                        emit_jsmusic.solution(language, e.shape, e.args))

    def test_programs_are_short(self) -> None:
        """3-10 lines: a formula or a small array, not a project."""
        for _, e in NEW:
            lines = _answer(e).splitlines()
            with self.subTest(exercise=e.id):
                self.assertGreaterEqual(len(lines), 3)
                self.assertLessEqual(len(lines), 10)

    def test_the_pages_really_vary(self) -> None:
        """Each page mixes its variants, and yes-no answers go both ways."""
        for p in JSMUSIC_PAGES:
            with self.subTest(page=p.id):
                wants = {e.args["want"] for e in p.exercises}
                self.assertGreaterEqual(len(wants), 3)

        def said(page: str, want: str) -> set[str]:
            return {_expect(e) for e in BY_ID[page].exercises
                    if e.args["want"] == want}

        self.assertEqual(said("js-music-midi", "black"), {"true", "false"})
        self.assertEqual(said("js-music-scales", "inscale"), {"true", "false"})
        # Decibels go both ways: cuts keep their minus sign through toFixed.
        for want in ("ratio", "power", "gain"):
            signs = {out.startswith("-") for out in said("js-music-decibels", want)}
            with self.subTest(want=want):
                self.assertEqual(signs, {True, False})
        # Transposing down wraps past C, and up wraps past B.
        names = emit_jsmusic.NAMES
        up = [e for e in BY_ID["js-music-transpose"].exercises
              if e.args["want"] == "up"]
        self.assertTrue(any(
            names.index(e.args["note"]) + e.args["steps"] >= 12 for e in up))
        down = [e for e in BY_ID["js-music-transpose"].exercises
                if e.args["want"] == "down"]
        self.assertTrue(any(
            names.index(e.args["note"]) - e.args["steps"] < 0 for e in down))
        # Some snaps are exact halves, which Math.round sends up, and some
        # are not; some notes move earlier and some later.
        def tie(e) -> bool:
            played = e.args["played"]
            times = played if isinstance(played, tuple) else (played,)
            return any(t % e.args["grid"] * 2 == e.args["grid"] for t in times)

        snaps = [e for e in BY_ID["js-music-quantize"].exercises
                 if e.args["want"] in ("snap", "late", "snaplist")]
        self.assertEqual({tie(e) for e in snaps}, {True, False})
        late = {_expect(e)[0] == "-" for e in BY_ID["js-music-quantize"].exercises
                if e.args["want"] == "late"}
        self.assertEqual(late, {True, False})
        # Swing lands on halves in a row or two, so the rounding matters.
        swings = [e for e in BY_ID["js-music-quantize"].exercises
                  if e.args["want"] == "swing"]
        self.assertTrue(any(
            (2 * e.args["step"] * e.args["swing"]) % 100 == 50 for e in swings))
        # A pad of zeros: some totals have seconds under ten.
        totals = [_expect(e) for e in BY_ID["js-music-tracks"].exercises
                  if e.args["want"] == "total"]
        self.assertTrue(any(out.split(":")[1][0] == "0" for out in totals))
        # Both ways of sorting and both ends of every list appear.
        sorts = {(e.args["field"], e.args["way"])
                 for e in BY_ID["js-music-tracks"].exercises
                 if e.args["want"] == "sort"}
        self.assertEqual({w for _, w in sorts}, {"up", "down"})
        self.assertEqual({f for f, _ in sorts}, {"bpm", "secs"})
        # Both layerings, both octave directions.
        hows = {e.args["how"] for e in BY_ID["js-music-steps"].exercises
                if e.args["want"] == "layer"}
        self.assertEqual(hows, {"or", "and"})
        ways = {e.args["way"] for e in BY_ID["js-music-freq"].exercises
                if e.args["want"] == "octaves"}
        self.assertEqual(ways, {"up", "down"})

    def test_the_tables_agree(self) -> None:
        c, m = content_jsmusic, emit_jsmusic
        self.assertEqual(len(m.NAMES), 12)
        self.assertEqual(len(set(m.NAMES)), 12)
        self.assertEqual(len(m.INTERVALS), 12)
        # A4 is MIDI note 69, A is the tenth name, and middle C is 60.
        self.assertEqual(m._midi("A", 4), 69)
        self.assertEqual(m._midi("C", 4), 60)
        self.assertEqual(m._called(69), "A4")
        # The black keys are the sharps in the names.
        self.assertEqual(
            [i for i, n in enumerate(m.NAMES) if "#" in n], list(m.BLACK))
        # Every scale and chord starts on the root and stays inside an octave.
        for table in (c.MODES, c.CHORDS):
            for name, steps in table.items():
                with self.subTest(pattern=name):
                    self.assertEqual(steps[0], 0)
                    self.assertEqual(list(steps), sorted(set(steps)))
                    self.assertLess(steps[-1], 12)
        # Major and minor scales are the usual seven notes.
        self.assertEqual(c.MODES["major"], (0, 2, 4, 5, 7, 9, 11))
        self.assertEqual(c.MODES["minor"], (0, 2, 3, 5, 7, 8, 10))
        # The prompts quote the same names the programs use.
        self.assertIn(", ".join(m.NAMES), c._NOTES_SAY)
        self.assertEqual(m.PPQ, 480)

    def test_answers_worked_out_by_hand(self) -> None:
        """A few outputs worked out on paper, held against the oracle."""
        out = emit_jsmusic.expected_output
        hand = (
            ("js_music_tempo", {"want": "beat", "bpm": 120}, "500.00"),
            ("js_music_tempo",
             {"want": "length", "bars": 8, "per_bar": 4, "bpm": 120}, "16.00"),
            ("js_music_tempo", {"want": "position", "seconds": 1.2, "bpm": 120},
             "bar 1, beat 3"),
            ("js_music_midi", {"want": "name", "midi": 60}, "C4"),
            ("js_music_midi", {"want": "name", "midi": 69}, "A4"),
            ("js_music_midi", {"want": "number", "note": "A", "octave": 4}, "69"),
            ("js_music_midi", {"want": "black", "midi": 61}, "true"),
            ("js_music_freq", {"want": "hz", "midi": 69}, "440.00"),
            ("js_music_freq", {"want": "hz", "midi": 81}, "880.00"),
            ("js_music_freq", {"want": "hz", "midi": 60}, "261.63"),
            ("js_music_freq", {"want": "tune", "midi": 69, "ref": 432}, "432.00"),
            ("js_music_transpose", {"want": "up", "note": "B", "steps": 1}, "C"),
            ("js_music_transpose", {"want": "down", "note": "C", "steps": 1}, "B"),
            ("js_music_transpose",
             {"want": "named", "one": "C", "two": "G"}, "perfect 5th"),
            ("js_music_scales",
             {"want": "scale", "root": "C",
              "steps": (0, 2, 4, 5, 7, 9, 11)}, "C D E F G A B"),
            ("js_music_scales",
             {"want": "chord", "root": "A", "steps": (0, 3, 7)}, "A, C, E"),
            ("js_music_db", {"want": "ratio", "ratio": 10}, "20.00"),
            ("js_music_db", {"want": "ratio", "ratio": 2}, "6.02"),
            ("js_music_db", {"want": "db", "db": -20}, "0.100"),
            ("js_music_db",
             {"want": "gain", "start": -18, "stages": (6, -3.5, 2)}, "-13.5 dB"),
            ("js_music_samples",
             {"want": "wav", "rate": 44100, "seconds": 60, "channels": 2,
              "bits": 16}, "10584044\n10.09"),
            ("js_music_samples", {"want": "bitdepth", "bits": 16},
             "65536\n96.32"),
            ("js_music_steps", {"want": "count", "pattern": "x---x---x---x---"},
             "4"),
            ("js_music_steps", {"want": "euclid", "steps": 8, "hits": 3},
             "x-x--x--"),
            ("js_music_quantize", {"want": "snap", "grid": 120, "played": 420},
             "480"),
            ("js_music_quantize", {"want": "snap", "grid": 120, "played": 250},
             "240"),
            ("js_music_quantize", {"want": "bbt", "ticks": 1920}, "2:1:0"),
            ("js_music_quantize",
             {"want": "swing", "step": 125, "swing": 55, "count": 4},
             "0, 138, 250, 388"),
        )
        for shape, args, want in hand:
            with self.subTest(shape=shape, want=args["want"]):
                self.assertEqual(out(shape, args), want)

    def test_the_oracle_refuses_bad_data(self) -> None:
        out = emit_jsmusic.expected_output
        with self.assertRaises(ValueError):  # 75.0 beats: a hair from whole
            out("js_music_tempo",
                {"want": "position", "seconds": 37.5, "bpm": 120})
        with self.assertRaises(ValueError):  # 0.25 is a tie at one place
            out("js_music_samples", {"want": "perbeat", "rate": 1, "bpm": 240})
        with self.assertRaises(ValueError):  # a note below C0
            out("js_music_midi", {"want": "name", "midi": 3})
        with self.assertRaises(ValueError):  # not a note name
            out("js_music_midi", {"want": "number", "note": "H", "octave": 4})
        with self.assertRaises(ValueError):  # a unison is not an interval here
            out("js_music_transpose", {"want": "interval", "one": "C", "two": "C"})
        with self.assertRaises(ValueError):  # steps must start on the root
            out("js_music_scales",
                {"want": "scale", "root": "C", "steps": (2, 4, 5, 7, 9)})
        with self.assertRaises(ValueError):  # a thirds-only "scale"
            out("js_music_scales",
                {"want": "scale", "root": "C", "steps": (0, 4, 7)})
        with self.assertRaises(ValueError):  # a quarter-dB stage is not exact
            out("js_music_db",
                {"want": "gain", "start": 0, "stages": (0.25, 1)})
        with self.assertRaises(ValueError):  # a rotation that changes nothing
            out("js_music_steps",
                {"want": "rotate", "pattern": "x---x---x---x---", "shift": 4})
        with self.assertRaises(ValueError):  # P4 is inside P1
            out("js_music_steps",
                {"want": "layer", "one": "x---x---x---x---",
                 "two": "----x-------x---", "how": "or"})
        with self.assertRaises(ValueError):  # a note already on the grid
            out("js_music_quantize",
                {"want": "late", "grid": 120, "played": 240})
        with self.assertRaises(ValueError):  # swing 50 is straight
            out("js_music_quantize",
                {"want": "swing", "step": 125, "swing": 50, "count": 4})
        items = (("A", 100, "C", 100), ("B", 100, "D", 200),
                 ("C", 120, "E", 300), ("D", 130, "F", 400))
        with self.assertRaises(ValueError):  # a tie on bpm
            out("js_music_tracks",
                {"want": "sort", "items": items, "field": "bpm", "way": "up"})
        with self.assertRaises(ValueError):  # a track on the limit
            out("js_music_tracks",
                {"want": "filter", "items": items, "test": ("bpm", ">", 120)})
        with self.assertRaises(ValueError):  # Track does not fit in 5
            out("js_music_tracks",
                {"want": "table", "items": items, "widths": (5, 4, 5),
                 "header": True})
        with self.assertRaises(ValueError):  # a note that is not a name
            emit_jsmusic.solution(
                "javascript", "js_music_transpose",
                {"want": "up", "note": "H!", "steps": 3})

    def test_a_snap_that_is_a_tie_goes_up(self) -> None:
        snap = emit_jsmusic._snap
        self.assertEqual(snap(30, 60), 1)
        self.assertEqual(snap(90, 60), 2)
        self.assertEqual(snap(150, 60), 3)
        self.assertEqual(snap(29, 60), 0)

    @unittest.skipUnless(REGISTERED, "not registered in content.py yet")
    def test_registered_dispatch_agrees(self) -> None:
        from code_coach.workbook.complexity import for_shape

        for _, e in NEW:
            with self.subTest(exercise=e.id):
                self.assertEqual(e.expect, _expect(e))
                self.assertEqual(e.answer("javascript"), _answer(e))
                self.assertIsNone(e.answer("python"))
        for shape in emit_jsmusic.SHAPE_IDS:
            with self.subTest(shape=shape):
                self.assertIsNotNone(for_shape(shape))


class ReferenceRunTests(unittest.TestCase):
    TIMED_OUT = 124

    def test_every_reference_answer_prints_what_it_should(self) -> None:
        for _, e in NEW:
            code = _answer(e)
            with self.subTest(exercise=e.id):
                stdout, stderr, code_ = run_code(code, language="javascript")
                if code_ == self.TIMED_OUT:
                    stdout, stderr, code_ = run_code(code, language="javascript")
                self.assertEqual(code_, 0, (stderr or stdout)[:400])
                self.assertTrue(
                    matches(stdout, _expect(e)),
                    f"printed {stdout!r}, wanted {_expect(e)!r}\n{code}")


if __name__ == "__main__":
    unittest.main()
