"""JavaScript: music production and sound.

Ten pages of studio arithmetic, each one a short program that runs in plain
node with no DOM: tempo and time, note names and MIDI numbers, frequencies,
transposing, scales and chords, decibels, sample-rate arithmetic, step
sequencer patterns, quantizing and swing, and a list of tracks to filter,
sort and print as a table.

The facts arrive in the arguments: the content module states every number
and table (the twelve note names, the interval patterns) in its prompts, so
this module only does the arithmetic.

The oracle never runs the JavaScript. It works each answer out in Python,
doing the same operations in the same order so the doubles come out
identical, and the tests then hold node to it. Anything that is not a whole
number is printed with toFixed, which emit_jsgame._fixed models exactly. A
learner may well divide before multiplying, which can move the last bit of
a double; that only changes what prints when the answer sits right on a
rounding edge, so rows that do are refused here. The one place a tie is
wanted, snapping to a grid with Math.round, is worked out on exact
fractions instead, because there the tie is the lesson.

Powers with a fractional exponent (2 ** (n / 12), 10 ** (db / 20)) and
Math.log10 are allowed because every one is printed to a few decimals: the
last bit of a double cannot change the digits unless the value is on a
rounding edge, which the guard refuses, and node confirms every row.
"""

from __future__ import annotations

import math
from fractions import Fraction

from code_coach.workbook.complexity import Cost
from code_coach.workbook.emit import NL, Shape, _lines
from code_coach.workbook.emit_jsgame import _bool, _fixed, _lit, _num

LANGUAGES: tuple[str, ...] = ("javascript",)

SHAPES: tuple[Shape, ...] = (
    Shape("js_music_tempo", "tempo and time: milliseconds per beat, note lengths, bars"),
    Shape("js_music_midi", "note names and MIDI numbers, with % and an array of names"),
    Shape("js_music_freq", "MIDI notes and octaves as frequencies in Hz"),
    Shape("js_music_transpose", "intervals and transposing with wraparound"),
    Shape("js_music_scales", "scales and chords as interval arrays mapped to note names"),
    Shape("js_music_db", "decibels and amplitude ratios"),
    Shape("js_music_samples", "sample rate arithmetic: samples, bytes and milliseconds"),
    Shape("js_music_steps", "step sequencer patterns as strings"),
    Shape("js_music_quantize", "quantizing to a grid, swing and ticks"),
    Shape("js_music_tracks", "an array of tracks to filter, sort, reduce and print as a table"),
)

SHAPE_IDS: tuple[str, ...] = tuple(s.id for s in SHAPES)


def handles(shape: str) -> bool:
    return shape in SHAPE_IDS


# ── The tables, as the program writes them ───────────────────

#: The twelve pitch classes, sharps only. Index 0 is C.
NAMES: tuple[str, ...] = (
    "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B",
)
NAMES_LIT = "[" + ", ".join(f'"{n}"' for n in NAMES) + "]"

#: What twelve semitone distances are called, 0 to 11.
INTERVALS: tuple[str, ...] = (
    "unison", "minor 2nd", "major 2nd", "minor 3rd", "major 3rd",
    "perfect 4th", "tritone", "perfect 5th", "minor 6th", "major 6th",
    "minor 7th", "major 7th",
)
INTERVALS_LIT = "[" + ", ".join(f'"{n}"' for n in INTERVALS) + "]"

#: Black keys, as pitch classes.
BLACK = (1, 3, 6, 8, 10)

#: Ticks in a quarter note, for the MIDI-clock rows.
PPQ = 480


# ── Writing numbers and names ────────────────────────────────


def _code(x) -> str:
    """A number literal. A whole float such as 128.0 is written 128."""
    if isinstance(x, float) and x.is_integer():
        x = int(x)
    return _lit(x)


def _str(s: str) -> str:
    """A short string literal: a note, a key, a track name."""
    if not s or not all(c.isalnum() or c in "# -" for c in s):
        raise ValueError(f"{s!r}: plain letters, digits, # and spaces")
    return f'"{s}"'


def _list(values, write=_code) -> str:
    return "[" + ", ".join(write(v) for v in values) + "]"


def _pitch(name: str) -> int:
    if name not in NAMES:
        raise ValueError(f"{name!r} is not one of the twelve note names")
    return NAMES.index(name)


def _midi(name: str, octave: int) -> int:
    return 12 * (octave + 1) + _pitch(name)


def _called(midi: int) -> str:
    return f"{NAMES[midi % 12]}{midi // 12 - 1}"


def _steps(steps) -> list[int]:
    steps = list(steps)
    if steps != sorted(set(steps)) or steps[0] != 0 or steps[-1] > 11:
        raise ValueError("steps rise from 0 and stay inside an octave")
    return steps


# ── Refusing anything that could print two ways ──────────────

#: How close, relative to its size, a value may come to an edge.
_TOO_CLOSE = 1e-9


def _edge(x, digits: int) -> None:
    scaled = abs(x) * 10 ** digits
    if abs(scaled - math.floor(scaled) - 0.5) < _TOO_CLOSE * max(1.0, scaled):
        raise ValueError(f"{x} sits on a rounding edge at {digits} places")


def _shown(x, digits: int) -> str:
    """toFixed(digits), for a value no order of operations can tip over."""
    _edge(x, digits)
    return _fixed(x, digits)


def _floor(x: float) -> int:
    """Math.floor of a computed value, refused a hair from a whole number."""
    near = round(x)
    if abs(x - near) < _TOO_CLOSE * max(1.0, abs(x)):
        raise ValueError(f"{x} is too near {near} to round down safely")
    return math.floor(x)


def _snap(top: int, bottom: int) -> int:
    """Math.round(top / bottom) with halves going up, on exact fractions.

    The quotient of two small whole numbers is a tie only when it is exactly
    k + 1/2, a value a double holds exactly, so JavaScript lands on the same
    side. Kept to positive values: Math.round of a small negative is -0.
    """
    if top <= 0 or bottom <= 0:
        raise ValueError("positive times and grids only")
    return math.floor(Fraction(top, bottom) + Fraction(1, 2))


# ── 1. Tempo and time ────────────────────────────────────────


def _tempo(a: dict) -> str:
    want, bpm = a["want"], _code(a["bpm"])
    if want == "beat":
        return _lines(
            f"const bpm = {bpm};",
            "const msPerBeat = 60000 / bpm;",
            "console.log(msPerBeat.toFixed(2));",
        )
    if want == "delay":
        return _lines(
            f"const bpm = {bpm};",
            f"const noteBeats = {_code(a['beats'])};",
            "const delayMs = 60000 / bpm * noteBeats;",
            "console.log(delayMs.toFixed(2));",
        )
    if want == "length":
        return _lines(
            f"const bars = {_code(a['bars'])};",
            f"const beatsPerBar = {_code(a['per_bar'])};",
            f"const bpm = {bpm};",
            "const seconds = bars * beatsPerBar * 60 / bpm;",
            "console.log(seconds.toFixed(2));",
        )
    if want == "position":
        return _lines(
            f"const seconds = {_code(a['seconds'])};",
            f"const bpm = {bpm};",
            "const beats = Math.floor(seconds * bpm / 60);",
            "const bar = Math.floor(beats / 4) + 1;",
            "const beat = beats % 4 + 1;",
            "console.log(`bar ${bar}, beat ${beat}`);",
        )
    if want == "fit":
        return _lines(
            f"const seconds = {_code(a['seconds'])};",
            f"const bpm = {bpm};",
            "const barSeconds = 240 / bpm;",
            "const bars = Math.floor(seconds / barSeconds);",
            "console.log(bars);",
            "console.log((seconds - bars * barSeconds).toFixed(2));",
        )
    raise ValueError(want)


def _tempo_out(a: dict) -> str:
    want, bpm = a["want"], a["bpm"]
    if not isinstance(bpm, int) or bpm <= 0:
        raise ValueError("a whole number of beats per minute")
    if want == "beat":
        return _shown(60000 / bpm, 2)
    if want == "delay":
        return _shown(60000 / bpm * a["beats"], 2)
    if want == "length":
        return _shown(a["bars"] * a["per_bar"] * 60 / bpm, 2)
    if want == "position":
        beats = _floor(a["seconds"] * bpm / 60)
        return f"bar {beats // 4 + 1}, beat {beats % 4 + 1}"
    if want == "fit":
        bar_seconds = 240 / bpm
        bars = _floor(a["seconds"] / bar_seconds)
        if bars < 1:
            raise ValueError("one whole bar at least")
        return NL.join([str(bars), _shown(a["seconds"] - bars * bar_seconds, 2)])
    raise ValueError(want)


# ── 2. Note names and MIDI numbers ───────────────────────────


def _midi_page(a: dict) -> str:
    want = a["want"]
    names = f"const names = {NAMES_LIT};"
    if want == "name":
        return _lines(
            names,
            f"const midi = {a['midi']};",
            "console.log(`${names[midi % 12]}${Math.floor(midi / 12) - 1}`);",
        )
    if want == "number":
        return _lines(
            names,
            f"const note = {_str(a['note'])};",
            f"const octave = {a['octave']};",
            "const midi = names.indexOf(note) + (octave + 1) * 12;",
            "console.log(midi);",
        )
    if want == "pitch":
        return _lines(
            names,
            f"const midi = {a['midi']};",
            "console.log(names[midi % 12]);",
        )
    if want == "octave":
        return _lines(
            f"const midi = {a['midi']};",
            "const octave = Math.floor(midi / 12) - 1;",
            "console.log(octave);",
        )
    if want == "black":
        return _lines(
            f"const blackKeys = {_list(BLACK)};",
            f"const midi = {a['midi']};",
            "console.log(blackKeys.includes(midi % 12));",
        )
    raise ValueError(want)


def _midi_out(a: dict) -> str:
    want = a["want"]
    if want == "number":
        return str(_midi(a["note"], a["octave"]))
    midi = a["midi"]
    if not 12 <= midi <= 127:
        raise ValueError("MIDI notes run 0-127; keep to C0 and up")
    if want == "name":
        return _called(midi)
    if want == "pitch":
        return NAMES[midi % 12]
    if want == "octave":
        return str(midi // 12 - 1)
    if want == "black":
        return _bool(midi % 12 in BLACK)
    raise ValueError(want)


# ── 3. Frequencies ───────────────────────────────────────────


def _freq(a: dict) -> str:
    want = a["want"]
    if want == "hz":
        return _lines(
            f"const midi = {a['midi']};",
            "const hz = 440 * 2 ** ((midi - 69) / 12);",
            "console.log(hz.toFixed(2));",
        )
    if want == "note":
        return _lines(
            f"const names = {NAMES_LIT};",
            f"const note = {_str(a['note'])};",
            f"const octave = {a['octave']};",
            "const midi = names.indexOf(note) + (octave + 1) * 12;",
            "const hz = 440 * 2 ** ((midi - 69) / 12);",
            "console.log(hz.toFixed(2));",
        )
    if want == "octaves":
        op = "*" if a["way"] == "up" else "/"
        return _lines(
            f"const hz = {_code(a['hz'])};",
            f"const octaves = {a['octaves']};",
            f"const shifted = hz {op} 2 ** octaves;",
            "console.log(shifted.toFixed(2));",
        )
    if want == "tune":
        return _lines(
            f"const reference = {a['ref']};",
            f"const midi = {a['midi']};",
            "const hz = reference * 2 ** ((midi - 69) / 12);",
            "console.log(hz.toFixed(2));",
        )
    if want == "fifth":
        return _lines(
            f"const midi = {a['midi']};",
            "const root = 440 * 2 ** ((midi - 69) / 12);",
            "const equal = root * 2 ** (7 / 12);",
            "const just = root * 1.5;",
            "console.log(equal.toFixed(2));",
            "console.log(just.toFixed(2));",
        )
    raise ValueError(want)


def _hz(midi: int, reference: int = 440) -> float:
    return reference * 2 ** ((midi - 69) / 12)


def _freq_out(a: dict) -> str:
    want = a["want"]
    if want == "hz":
        return _shown(_hz(a["midi"]), 2)
    if want == "note":
        return _shown(_hz(_midi(a["note"], a["octave"])), 2)
    if want == "octaves":
        n = a["octaves"]
        if not isinstance(n, int) or n < 1:
            raise ValueError("whole octaves, at least one")
        if a["way"] not in ("up", "down"):
            raise ValueError(a["way"])
        hz = a["hz"] * 2 ** n if a["way"] == "up" else a["hz"] / 2 ** n
        return _shown(hz, 2)
    if want == "tune":
        return _shown(_hz(a["midi"], a["ref"]), 2)
    if want == "fifth":
        root = _hz(a["midi"])
        return NL.join([_shown(root * 2 ** (7 / 12), 2), _shown(root * 1.5, 2)])
    raise ValueError(want)


# ── 4. Intervals and transposing ─────────────────────────────


def _transpose(a: dict) -> str:
    want = a["want"]
    names = f"const names = {NAMES_LIT};"
    if want == "up":
        return _lines(
            names,
            f"const note = {_str(a['note'])};",
            f"const steps = {a['steps']};",
            "const index = (names.indexOf(note) + steps) % 12;",
            "console.log(names[index]);",
        )
    if want == "down":
        return _lines(
            names,
            f"const note = {_str(a['note'])};",
            f"const steps = {a['steps']};",
            "const index = ((names.indexOf(note) - steps) % 12 + 12) % 12;",
            "console.log(names[index]);",
        )
    if want == "interval":
        return _lines(
            names,
            f"const from = {_str(a['one'])};",
            f"const to = {_str(a['two'])};",
            "const semitones = (names.indexOf(to) - names.indexOf(from) + 12) % 12;",
            "console.log(semitones);",
        )
    if want == "named":
        return _lines(
            names,
            f"const intervals = {INTERVALS_LIT};",
            f"const from = {_str(a['one'])};",
            f"const to = {_str(a['two'])};",
            "const semitones = (names.indexOf(to) - names.indexOf(from) + 12) % 12;",
            "console.log(intervals[semitones]);",
        )
    if want == "melody":
        return _lines(
            names,
            f"const melody = {_list(a['notes'], _str)};",
            f"const steps = {a['steps']};",
            "const moved = melody.map((n) => names[(names.indexOf(n) + steps + 12) % 12]);",
            'console.log(moved.join(" "));',
        )
    raise ValueError(want)


def _transpose_out(a: dict) -> str:
    want = a["want"]
    if want in ("up", "down"):
        steps = a["steps"]
        if steps < 1:
            raise ValueError("at least one step")
        i = _pitch(a["note"]) + (steps if want == "up" else -steps)
        return NAMES[i % 12]
    if want in ("interval", "named"):
        one, two = _pitch(a["one"]), _pitch(a["two"])
        if one == two:
            raise ValueError("two different notes, or it is a unison")
        semis = (two - one) % 12
        return str(semis) if want == "interval" else INTERVALS[semis]
    if want == "melody":
        steps = a["steps"]
        if not -12 <= steps <= 11 or steps == 0:
            raise ValueError("a shift of up to an octave either way")
        return " ".join(NAMES[(_pitch(n) + steps) % 12] for n in a["notes"])
    raise ValueError(want)


# ── 5. Scales and chords ─────────────────────────────────────


def _scale_lines(a: dict) -> list[str]:
    return [
        f"const names = {NAMES_LIT};",
        f"const root = names.indexOf({_str(a['root'])});",
        f"const steps = {_list(a['steps'])};",
        "const scale = steps.map((s) => names[(root + s) % 12]);",
    ]


def _scales(a: dict) -> str:
    want = a["want"]
    if want == "scale":
        return _lines(*_scale_lines(a), 'console.log(scale.join(" "));')
    if want == "chord":
        return _lines(*_scale_lines(a), 'console.log(scale.join(", "));')
    if want == "inscale":
        return _lines(*_scale_lines(a),
                      f"console.log(scale.includes({_str(a['test'])}));")
    if want == "degree":
        return _lines(*_scale_lines(a),
                      f"console.log(scale[{a['degree']} - 1]);")
    if want == "progression":
        return _lines(
            *_scale_lines(a),
            f"const degrees = {_list(a['degrees'])};",
            'console.log(degrees.map((d) => scale[d - 1]).join(" - "));',
        )
    raise ValueError(want)


def _scales_out(a: dict) -> str:
    want = a["want"]
    root, steps = _pitch(a["root"]), _steps(a["steps"])
    notes = [NAMES[(root + s) % 12] for s in steps]
    if want == "scale":
        if len(steps) < 5:
            raise ValueError("a scale has five notes at least")
        return " ".join(notes)
    if want == "chord":
        if not 3 <= len(steps) <= 4:
            raise ValueError("a chord is three or four notes")
        return ", ".join(notes)
    if want == "inscale":
        test = a["test"]
        _pitch(test)
        return _bool(test in notes)
    if want == "degree":
        if not 1 <= a["degree"] <= len(notes):
            raise ValueError("a degree the scale has")
        return notes[a["degree"] - 1]
    if want == "progression":
        if any(not 1 <= d <= len(notes) for d in a["degrees"]):
            raise ValueError("degrees the scale has")
        return " - ".join(notes[d - 1] for d in a["degrees"])
    raise ValueError(want)


# ── 6. Decibels ──────────────────────────────────────────────


def _db(a: dict) -> str:
    want = a["want"]
    if want == "ratio":
        return _lines(
            f"const ratio = {_code(a['ratio'])};",
            "const db = 20 * Math.log10(ratio);",
            "console.log(db.toFixed(2));",
        )
    if want == "power":
        return _lines(
            f"const ratio = {_code(a['ratio'])};",
            "const db = 10 * Math.log10(ratio);",
            "console.log(db.toFixed(2));",
        )
    if want == "db":
        return _lines(
            f"const db = {_code(a['db'])};",
            "const ratio = 10 ** (db / 20);",
            "console.log(ratio.toFixed(3));",
        )
    if want == "gain":
        return _lines(
            f"const start = {_code(a['start'])};",
            f"const stages = {_list(a['stages'])};",
            "const total = stages.reduce((sum, g) => sum + g, start);",
            "console.log(`${total} dB`);",
        )
    if want == "fader":
        return _lines(
            f"const sample = {_code(a['sample'])};",
            f"const db = {_code(a['db'])};",
            "const quieter = sample * 10 ** (db / 20);",
            "console.log(quieter.toFixed(3));",
        )
    raise ValueError(want)


def _db_out(a: dict) -> str:
    want = a["want"]
    if want == "ratio":
        return _shown(20 * math.log10(a["ratio"]), 2)
    if want == "power":
        return _shown(10 * math.log10(a["ratio"]), 2)
    if want == "db":
        return _shown(10 ** (a["db"] / 20), 3)
    if want == "gain":
        # Left to right, as reduce does. Every value is a whole number or a
        # half, which a double holds exactly, so the sum is exact too.
        total = a["start"]
        for g in a["stages"]:
            if (g * 2) % 1:
                raise ValueError("whole numbers or halves only")
            total = total + g
        return f"{_num(total)} dB"
    if want == "fader":
        return _shown(a["sample"] * 10 ** (a["db"] / 20), 3)
    raise ValueError(want)


# ── 7. Sample rate arithmetic ────────────────────────────────


def _samples(a: dict) -> str:
    want = a["want"]
    if want == "perbeat":
        return _lines(
            f"const rate = {a['rate']};",
            f"const bpm = {a['bpm']};",
            "const samples = rate * 60 / bpm;",
            "console.log(samples.toFixed(1));",
        )
    if want == "wav":
        return _lines(
            f"const rate = {a['rate']};",
            f"const seconds = {a['seconds']};",
            f"const channels = {a['channels']};",
            f"const bits = {a['bits']};",
            "const bytes = rate * seconds * channels * (bits / 8) + 44;",
            "console.log(bytes);",
            "console.log((bytes / 1024 / 1024).toFixed(2));",
        )
    if want == "duration":
        return _lines(
            f"const count = {a['count']};",
            f"const rate = {a['rate']};",
            "console.log((count / rate).toFixed(3));",
        )
    if want == "latency":
        return _lines(
            f"const buffer = {a['buffer']};",
            f"const rate = {a['rate']};",
            "const ms = buffer / rate * 1000;",
            "console.log(ms.toFixed(2));",
        )
    if want == "bitdepth":
        return _lines(
            f"const bits = {a['bits']};",
            "console.log(2 ** bits);",
            "console.log((bits * 6.02).toFixed(2));",
        )
    raise ValueError(want)


def _samples_out(a: dict) -> str:
    want = a["want"]
    if want == "perbeat":
        return _shown(a["rate"] * 60 / a["bpm"], 1)
    if want == "wav":
        if a["bits"] % 8:
            raise ValueError("whole bytes per sample")
        total = a["rate"] * a["seconds"] * a["channels"] * (a["bits"] // 8) + 44
        return NL.join([str(total), _shown(total / 1024 / 1024, 2)])
    if want == "duration":
        return _shown(a["count"] / a["rate"], 3)
    if want == "latency":
        return _shown(a["buffer"] / a["rate"] * 1000, 2)
    if want == "bitdepth":
        return NL.join([str(2 ** a["bits"]), _shown(a["bits"] * 6.02, 2)])
    raise ValueError(want)


# ── 8. Step sequencer patterns ───────────────────────────────


def _pattern(p: str) -> str:
    if len(p) != 16 or set(p) - {"x", "-"} or "x" not in p:
        raise ValueError(f"{p!r}: sixteen steps of x and -, with a hit")
    return f'"{p}"'


def _steps_prog(a: dict) -> str:
    want = a["want"]
    if want == "count":
        return _lines(
            f"const pattern = {_pattern(a['pattern'])};",
            'const hits = [...pattern].filter((c) => c === "x").length;',
            "console.log(hits);",
        )
    if want == "rotate":
        return _lines(
            f"const pattern = {_pattern(a['pattern'])};",
            f"const shift = {a['shift']};",
            "console.log(pattern.slice(shift) + pattern.slice(0, shift));",
        )
    if want == "positions":
        return _lines(
            f"const pattern = {_pattern(a['pattern'])};",
            "const hits = [];",
            "for (let i = 0; i < pattern.length; i++) {",
            '  if (pattern[i] === "x") hits.push(i + 1);',
            "}",
            'console.log(hits.join(", "));',
        )
    if want == "euclid":
        return _lines(
            f"const steps = {a['steps']};",
            f"const hits = {a['hits']};",
            'const pattern = Array(steps).fill("-");',
            "for (let i = 0; i < hits; i++) {",
            '  pattern[Math.floor(i * steps / hits)] = "x";',
            "}",
            'console.log(pattern.join(""));',
        )
    if want == "layer":
        word = {"or": "||", "and": "&&"}[a["how"]]
        return _lines(
            f"const a = {_pattern(a['one'])};",
            f"const b = {_pattern(a['two'])};",
            f'const both = [...a].map((c, i) => (c === "x" {word} b[i] === "x" ? "x" : "-"));',
            'console.log(both.join(""));',
        )
    raise ValueError(want)


def _steps_out(a: dict) -> str:
    want = a["want"]
    if want == "count":
        return str(a["pattern"].count("x"))
    if want == "rotate":
        p, n = a["pattern"], a["shift"]
        _pattern(p)
        if not 1 <= n <= 15 or p[n:] + p[:n] == p:
            raise ValueError("a rotation that changes the pattern")
        return p[n:] + p[:n]
    if want == "positions":
        _pattern(a["pattern"])
        return ", ".join(str(i + 1) for i, c in enumerate(a["pattern"]) if c == "x")
    if want == "euclid":
        steps, hits = a["steps"], a["hits"]
        if not 2 <= hits < steps:
            raise ValueError("some hits and some rests")
        out = ["-"] * steps
        for i in range(hits):
            out[i * steps // hits] = "x"
        return "".join(out)
    if want == "layer":
        one, two = a["one"], a["two"]
        _pattern(one)
        _pattern(two)
        if a["how"] not in ("or", "and"):
            raise ValueError(a["how"])
        pick = any if a["how"] == "or" else all
        merged = "".join("x" if pick(c == "x" for c in pair) else "-"
                         for pair in zip(one, two))
        if "x" not in merged or merged in (one, two):
            raise ValueError("a layer that changes something and keeps a hit")
        return merged
    raise ValueError(want)


# ── 9. Quantize and swing ────────────────────────────────────


def _quantize(a: dict) -> str:
    want = a["want"]
    if want == "snap":
        return _lines(
            f"const grid = {a['grid']};",
            f"const played = {a['played']};",
            "const snapped = Math.round(played / grid) * grid;",
            "console.log(snapped);",
        )
    if want == "late":
        return _lines(
            f"const grid = {a['grid']};",
            f"const played = {a['played']};",
            "const snapped = Math.round(played / grid) * grid;",
            "console.log(snapped - played);",
        )
    if want == "snaplist":
        return _lines(
            f"const grid = {a['grid']};",
            f"const played = {_list(a['played'])};",
            "const snapped = played.map((t) => Math.round(t / grid) * grid);",
            'console.log(snapped.join(", "));',
        )
    if want == "swing":
        return _lines(
            f"const stepMs = {a['step']};",
            f"const swing = {a['swing']};",
            "const times = [];",
            f"for (let i = 0; i < {a['count']}; i++) {{",
            "  const pair = Math.floor(i / 2) * 2 * stepMs;",
            "  times.push(Math.round(i % 2 === 0 ? pair : pair + 2 * stepMs * swing / 100));",
            "}",
            'console.log(times.join(", "));',
        )
    if want == "bbt":
        return _lines(
            f"const ppq = {PPQ};",
            f"const ticks = {a['ticks']};",
            "const bar = Math.floor(ticks / (ppq * 4)) + 1;",
            "const beat = Math.floor(ticks % (ppq * 4) / ppq) + 1;",
            "console.log(`${bar}:${beat}:${ticks % ppq}`);",
        )
    raise ValueError(want)


def _quantize_out(a: dict) -> str:
    want = a["want"]
    if want in ("snap", "late"):
        grid, played = a["grid"], a["played"]
        snapped = _snap(played, grid) * grid
        if want == "snap":
            return str(snapped)
        if snapped == played:
            raise ValueError("a note already on the grid has nothing to show")
        return str(snapped - played)
    if want == "snaplist":
        grid = a["grid"]
        return ", ".join(str(_snap(t, grid) * grid) for t in a["played"])
    if want == "swing":
        step, swing, count = a["step"], a["swing"], a["count"]
        if swing == 50 or not 50 < swing < 100 or count % 2:
            raise ValueError("real swing, and whole pairs of steps")
        times = []
        for i in range(count):
            pair = i // 2 * 2 * step
            times.append(pair if i % 2 == 0
                         else math.floor(pair + Fraction(2 * step * swing, 100)
                                         + Fraction(1, 2)))
        return ", ".join(str(t) for t in times)
    if want == "bbt":
        t, bar = a["ticks"], PPQ * 4
        return f"{t // bar + 1}:{t % bar // PPQ + 1}:{t % PPQ}"
    raise ValueError(want)


# ── 10. Tracks ───────────────────────────────────────────────

FIELD_WORDS = {"bpm": "bpm", "key": "key", "secs": "secs"}


def _tracks_data(items) -> list[str]:
    items = [tuple(r) for r in items]
    if len(items) != 4:
        raise ValueError("four tracks, so the program stays short")
    if len({r[0] for r in items}) != 4:
        raise ValueError("names must be unique, or the output is ambiguous")
    lines = []
    for name, bpm, key, secs in items:
        lines.append(f"  {{ name: {_str(name)}, bpm: {_code(bpm)}, "
                     f"key: {_str(key)}, secs: {_code(secs)} }},")
    return ["const tracks = [", *lines, "];"]


def _test(field: str, op: str, limit) -> str:
    if op == "=":
        return f"t.{field} === {_str(limit)}"
    if op not in (">", "<"):
        raise ValueError(op)
    return f"t.{field} {op} {_code(limit)}"


def _tracks(a: dict) -> str:
    want = a["want"]
    data = _tracks_data(a["items"])
    if want == "filter":
        field, op, limit = a["test"]
        return _lines(
            *data,
            f"const names = tracks.filter((t) => {_test(field, op, limit)}).map((t) => t.name);",
            'console.log(names.join(", "));',
        )
    if want == "sort":
        f = a["field"]
        compare = f"a.{f} - b.{f}" if a["way"] == "up" else f"b.{f} - a.{f}"
        return _lines(
            *data,
            f"const sorted = [...tracks].sort((a, b) => {compare});",
            'console.log(sorted.map((t) => t.name).join(", "));',
        )
    if want == "total":
        return _lines(
            *data,
            "const total = tracks.reduce((sum, t) => sum + t.secs, 0);",
            'const seconds = String(total % 60).padStart(2, "0");',
            "console.log(`${Math.floor(total / 60)}:${seconds}`);",
        )
    if want == "average":
        return _lines(
            *data,
            "const total = tracks.reduce((sum, t) => sum + t.bpm, 0);",
            "console.log((total / tracks.length).toFixed(1));",
        )
    if want == "longest":
        return _lines(
            *data,
            "const longest = tracks.reduce((best, t) => (t.secs > best.secs ? t : best));",
            "console.log(`${longest.name} ${longest.secs}`);",
        )
    if want == "table":
        nw, kw, bw = a["widths"]
        row = (f"`${{t.name.padEnd({nw})}} | ${{t.key.padEnd({kw})}} | "
               f"${{String(t.bpm).padStart({bw})}}`")
        head = []
        if a["header"]:
            head = [f'console.log(`${{"Track".padEnd({nw})}} | ${{"Key".padEnd({kw})}} | '
                    f'${{"BPM".padStart({bw})}}`);']
        return _lines(
            *data,
            *head,
            "for (const t of tracks) {",
            f"  console.log({row});",
            "}",
        )
    raise ValueError(want)


def _tracks_out(a: dict) -> str:
    want = a["want"]
    items = [tuple(r) for r in a["items"]]
    _tracks_data(items)
    if want == "filter":
        field, op, limit = a["test"]
        index = {"bpm": 1, "key": 2, "secs": 3}[field]
        if op == "=":
            kept = [r for r in items if r[index] == limit]
        else:
            if any(r[index] == limit for r in items):
                raise ValueError("a track on the limit: > and < would disagree")
            kept = [r for r in items if (r[index] > limit if op == ">" else r[index] < limit)]
        if not kept or len(kept) == len(items):
            raise ValueError("the filter has to keep some tracks and drop some")
        return ", ".join(r[0] for r in kept)
    if want == "sort":
        index = {"bpm": 1, "secs": 3}[a["field"]]
        values = [r[index] for r in items]
        if len(set(values)) != len(values):
            raise ValueError("a tie makes the order depend on the compare")
        ordered = sorted(items, key=lambda r: r[index], reverse=a["way"] == "down")
        if ordered == items:
            raise ValueError("already in order, so sorting shows nothing")
        return ", ".join(r[0] for r in ordered)
    if want == "total":
        total = sum(r[3] for r in items)
        if any(not isinstance(r[3], int) for r in items) or total < 60:
            raise ValueError("whole seconds, and a minute at least")
        return f"{total // 60}:{total % 60:02d}"
    if want == "average":
        total = 0
        for r in items:
            total = total + r[1]
        return _shown(total / len(items), 1)
    if want == "longest":
        secs = [r[3] for r in items]
        if len(set(secs)) != len(secs):
            raise ValueError("a tie: which is the longest?")
        best = max(items, key=lambda r: r[3])
        return f"{best[0]} {best[3]}"
    if want == "table":
        nw, kw, bw = a["widths"]

        def fit(text: str, width: int) -> str:
            if len(text) >= width:
                raise ValueError(f"{text} does not fit in {width} with a space to spare")
            return text

        rows = [f"{fit(n, nw).ljust(nw)} | {fit(k, kw).ljust(kw)} | "
                f"{fit(str(b), bw).rjust(bw)}" for n, b, k, _ in items]
        if a["header"]:
            rows.insert(0, f"{fit('Track', nw).ljust(nw)} | {fit('Key', kw).ljust(kw)} | "
                           f"{fit('BPM', bw).rjust(bw)}")
        return NL.join(rows)
    raise ValueError(want)


_BUILDERS = {
    "js_music_tempo": _tempo,
    "js_music_midi": _midi_page,
    "js_music_freq": _freq,
    "js_music_transpose": _transpose,
    "js_music_scales": _scales,
    "js_music_db": _db,
    "js_music_samples": _samples,
    "js_music_steps": _steps_prog,
    "js_music_quantize": _quantize,
    "js_music_tracks": _tracks,
}


def solution(language: str, shape: str, args: dict) -> str | None:
    if language not in LANGUAGES:
        return None
    build = _BUILDERS.get(shape)
    return build(args) if build else None


# ── What each should print, worked out in Python ─────────────

_ORACLES = {
    "js_music_tempo": _tempo_out,
    "js_music_midi": _midi_out,
    "js_music_freq": _freq_out,
    "js_music_transpose": _transpose_out,
    "js_music_scales": _scales_out,
    "js_music_db": _db_out,
    "js_music_samples": _samples_out,
    "js_music_steps": _steps_out,
    "js_music_quantize": _quantize_out,
    "js_music_tracks": _tracks_out,
}


def expected_output(shape: str, args: dict, value=None) -> str:
    oracle = _ORACLES.get(shape)
    if oracle is None:
        raise KeyError(shape)
    return oracle(args)


# ── Complexity notes ─────────────────────────────────────────

NOTES: dict[str, Cost] = {
    "js_music_tempo": Cost(
        "O(1)",
        "Constant: a divide, a multiply and sometimes a floor, whatever the "
        "tempo. Counting milliseconds off one beat at a time until you pass "
        "the length of the song would grow with it; dividing jumps there."),
    "js_music_midi": Cost(
        "O(1)",
        "Constant for a name from a number: one % and one divide. Going the "
        "other way, indexOf looks through the names array, at most twelve "
        "entries, which is a fixed amount of work."),
    "js_music_freq": Cost(
        "O(1)",
        "Constant: one power and a multiply. A keyboard of n keys would take "
        "n of them, one per key, but each is a single step."),
    "js_music_transpose": Cost(
        "O(1)",
        "Constant for one note: an indexOf over twelve names and a %. "
        "Transposing a melody of n notes with map is linear in n, one "
        "constant step per note."),
    "js_music_scales": Cost(
        "O(n)",
        "Linear in the number of notes in the scale or chord, n: map visits "
        "each step once. A scale is at most twelve notes, so in practice it "
        "is a handful of steps."),
    "js_music_db": Cost(
        "O(1)",
        "Constant: a log or a power and a multiply. Adding up a signal chain "
        "of n gain stages with reduce is linear in n, and in decibels it is "
        "a plain sum, which is why engineers use them."),
    "js_music_samples": Cost(
        "O(1)",
        "Constant: a few multiplies and divides. The numbers are big, a "
        "minute of audio is millions of samples, but arithmetic on them costs "
        "the same as on small ones; looping over every sample would not."),
    "js_music_steps": Cost(
        "O(n)",
        "Linear in the number of steps, n: counting, rotating (slice copies "
        "n characters), listing the hits and layering all visit each step "
        "once. A pattern is sixteen steps, so n stays small."),
    "js_music_quantize": Cost(
        "O(1)",
        "Constant for one note: a divide, a Math.round and a multiply. "
        "Snapping a list of n notes with map is linear in n, one constant "
        "step each."),
    "js_music_tracks": Cost(
        "O(n log n)",
        "Filtering, reducing and printing a table are each one pass over the "
        "n tracks, linear. Sorting takes about n log n comparisons, so sorting "
        "dominates when it is used; reduce finds the longest in one pass "
        "instead of sorting everything."),
}


def for_shape(shape: str) -> Cost | None:
    return NOTES.get(shape)
