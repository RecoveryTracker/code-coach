"""Pages 248-257: JavaScript, music production and sound.

Studio arithmetic, with the recording desk as the flavour and the JavaScript
as the lesson. The first pages are formulas, each a step harder than the one
before: tempo and time, note names and MIDI numbers, frequencies, intervals
and transposing, scales and chords, decibels, and sample-rate arithmetic.
The last three work on patterns and lists: step sequencer strings,
quantizing and swing, and an array of tracks to filter, sort and print as a
table that lines up.

Every prompt states the numbers and tables it needs (the twelve note names,
the steps of a scale), so nobody has to look anything up. Pitch uses the
standard conventions: sharps only, MIDI note 69 is A4 at 440 Hz, middle C is
60. Tempo pages work in 4/4 unless a prompt says otherwise.

Numbered after the bodybuilding pages (228-237, content_jslifting) and the
node pages (238-247), so this tuple has to be registered after them for the
book to stay in order. The tempo page and the time-in-bars rows share one
page (the first), which keeps the set to ten.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page
from code_coach.workbook.emit_jsmusic import NAMES, PPQ

JS_ONLY = ("javascript",)


def _page(page_id, number, name, teaches, example, shape, rows) -> Page:
    return Page(
        id=page_id,
        number=number,
        name=name,
        teaches=teaches,
        example=example,
        exercises=tuple(
            Exercise(
                id=f"{page_id}-{i + 1:02d}",
                prompt=prompt,
                shape=shape,
                args=args,
            )
            for i, (prompt, args) in enumerate(rows)
        ),
        languages=JS_ONLY,
        tier="intermediate",
    )


# ── Saying things ────────────────────────────────────────────


def _say(x) -> str:
    """A value as a prompt writes it: 0.5, 128, -6."""
    return repr(x) if isinstance(x, float) else str(x)


def _and(words) -> str:
    words = list(words)
    return ", ".join(words[:-1]) + " and " + words[-1] if len(words) > 1 else words[0]


def _plural(n: int, word: str) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


_NOTES = ", ".join(NAMES)
_NOTES_SAY = (f"Within an octave the twelve notes are named {_NOTES}, using "
              f"sharps and no flats.")
_MIDI_SAY = ("MIDI numbers the notes upward by semitones, twelve to an "
             "octave: C0 is note 12, middle C (C4) is 60 and A4 is 69.")
_A440_SAY = ("A4, MIDI note 69, sounds at 440 Hz, and every 12 semitones "
             "doubles the frequency, so a note's frequency is 440 times 2 "
             "raised to the power of (its note number minus 69) divided "
             "by 12.")
_WRAP_SAY = (f"Going up one semitone moves to the next name in {_NOTES}, and "
             f"after B it wraps round to C.")

#: Steps in semitones above the root.
MODES = {
    "major": (0, 2, 4, 5, 7, 9, 11),
    "minor": (0, 2, 3, 5, 7, 8, 10),
    "dorian": (0, 2, 3, 5, 7, 9, 10),
    "minor pentatonic": (0, 3, 5, 7, 10),
    "blues": (0, 3, 5, 6, 7, 10),
}
CHORDS = {
    "major": (0, 4, 7),
    "minor": (0, 3, 7),
    "diminished": (0, 3, 6),
    "major 7th": (0, 4, 7, 11),
    "minor 7th": (0, 3, 7, 10),
    "dominant 7th": (0, 4, 7, 10),
}


def _steps(steps) -> str:
    return ", ".join(str(s) for s in steps)


# ── 248. Tempo and time ──────────────────────────────────────

_TEMPOS = (
    ("beat", 128),
    ("beat", 100),
    ("beat", 140),
    ("beat", 174),
    ("delay", 120, 0.5, "an eighth note, half a beat"),
    ("delay", 128, 0.75, "a dotted eighth note, three quarters of a beat"),
    ("delay", 140, 0.25, "a sixteenth note, a quarter of a beat"),
    ("delay", 90, 1.5, "a dotted quarter note, a beat and a half"),
    ("length", 16, 4, 128),
    ("length", 4, 3, 100),
    ("length", 12, 4, 140),
    ("length", 32, 4, 174),
    ("position", 37.3, 120),
    ("position", 12.7, 128),
    ("position", 52, 140),
    ("position", 8.9, 100),
    ("fit", 200, 128),
    ("fit", 95, 140),
    ("fit", 185, 120),
    ("fit", 230, 174),
)


def _tempo_row(row):
    want = row[0]
    if want == "beat":
        bpm = row[1]
        return (f"A track runs at {bpm} beats per minute, and a minute is "
                f"60000 milliseconds. Print the length of one beat in "
                f"milliseconds, to two decimal places.",
                {"want": want, "bpm": bpm})
    if want == "delay":
        _, bpm, beats, label = row
        return (f"A delay effect should repeat on {label} at {bpm} beats per "
                f"minute. Work out how long one beat lasts in milliseconds, "
                f"multiply by the note's share of a beat, and print the delay "
                f"time in milliseconds to two decimal places.",
                {"want": want, "bpm": bpm, "beats": beats})
    if want == "length":
        _, bars, per_bar, bpm = row
        return (f"A section is {bars} bars long, with {per_bar} beats in "
                f"every bar, at {bpm} beats per minute. Print how many "
                f"seconds it lasts, to two decimal places.",
                {"want": want, "bars": bars, "per_bar": per_bar, "bpm": bpm})
    if want == "position":
        _, seconds, bpm = row
        return (f"A song at {bpm} beats per minute, in 4/4, has been playing "
                f"for {_say(seconds)} seconds. Count the whole beats played, "
                f"then print the bar and beat it is in, counting bars and "
                f"beats from 1, in the form bar 3, beat 2.",
                {"want": want, "seconds": seconds, "bpm": bpm})
    _, seconds, bpm = row
    return (f"A sample is {seconds} seconds long and the song runs at {bpm} "
            f"beats per minute in 4/4, so a bar is four beats. Print how "
            f"many whole bars fit in the sample, then how many seconds are "
            f"left over, to two decimal places.",
            {"want": want, "seconds": seconds, "bpm": bpm})


TEMPO_PAGE = _page(
    "js-music-tempo", 248, "Music: tempo and time",
    "Tempo is beats per minute, and a minute is 60000 milliseconds, so one "
    "beat lasts 60000 / bpm milliseconds: a faster tempo gives a shorter "
    "beat. Every note length is a share of a beat, so a delay set to an "
    "eighth note repeats after half a beat, 60000 / bpm * 0.5, and a dotted "
    "note is one and a half times its plain length. A bar of 4/4 is four "
    "beats, so a section's length in seconds is bars * beatsPerBar * 60 / "
    "bpm. To find where a playhead is, turn seconds into beats with seconds "
    "* bpm / 60 and keep the whole beats with Math.floor. Bars come from "
    "dividing the beats by four, again floored, and the beat inside the bar "
    "is what % 4 leaves; both count from 1 in music, so add 1. Decimals "
    "like 468.75 are stored in binary, so toFixed(2) rounds a number for "
    "printing and hands back a string.",
    "at 128 bpm, 60000 / 128 is 468.75, so a beat lasts 468.75 ms and an "
    "eighth note, 60000 / 128 * 0.5, lasts 234.375 ms; after 37.3 seconds at "
    "120 bpm, Math.floor(37.3 * 120 / 60) is 74 beats, which is bar "
    "Math.floor(74 / 4) + 1 = 19 and beat 74 % 4 + 1 = 3",
    "js_music_tempo",
    tuple(_tempo_row(row) for row in _TEMPOS),
)


# ── 249. Note names and MIDI numbers ─────────────────────────

_MIDIS = (
    ("name", 61),
    ("name", 81),
    ("name", 45),
    ("name", 100),
    ("number", "E", 2),
    ("number", "F#", 3),
    ("number", "A#", 4),
    ("number", "C", 6),
    ("pitch", 63),
    ("pitch", 66),
    ("pitch", 70),
    ("pitch", 79),
    ("octave", 36),
    ("octave", 60),
    ("octave", 77),
    ("octave", 108),
    ("black", 61),
    ("black", 64),
    ("black", 70),
    ("black", 71),
)


def _midi_row(row):
    want = row[0]
    if want == "number":
        _, note, octave = row
        return (f"{_MIDI_SAY} {_NOTES_SAY} Print the MIDI note number of "
                f"{note}{octave}.",
                {"want": want, "note": note, "octave": octave})
    midi = row[1]
    args = {"want": want, "midi": midi}
    if want == "name":
        return (f"{_MIDI_SAY} {_NOTES_SAY} Print the name and octave of MIDI "
                f"note {midi}, written like C4.", args)
    if want == "pitch":
        return (f"{_NOTES_SAY} Print the name of MIDI note {midi}, without "
                f"its octave: note 60 is C, 61 is C#, and the names repeat "
                f"every 12 notes.", args)
    if want == "octave":
        return (f"{_MIDI_SAY} Print the octave number of MIDI note {midi}.",
                args)
    return (f"On a piano the black keys are the sharps: C#, D#, F#, G# and "
            f"A#. {_MIDI_SAY} Print whether MIDI note {midi} is a black "
            f"key, true or false.", args)


MIDI_PAGE = _page(
    "js-music-midi", 249, "Music: note names and MIDI numbers",
    "MIDI numbers every note with one whole number, counting semitones, so "
    "an array of the twelve names turns a number into a name. The notes "
    "repeat every 12, so midi % 12 is the position within the octave, an "
    "index into [\"C\", \"C#\", \"D\", ...], and Math.floor(midi / 12) is "
    "how many whole octaves have gone by; the octave number is one less, "
    "because the numbering starts a step below, so C4 is 60, not 48. "
    "Going back, indexOf finds a name's position in the array, and "
    "(octave + 1) * 12 is where its octave starts: names.indexOf(\"F#\") + "
    "(3 + 1) * 12 is 6 + 48 = 54. A template literal glues the name and the "
    "octave together. includes asks whether an array holds a value, which "
    "is how to ask if a position is one of the black keys.",
    "with names = [\"C\", \"C#\", \"D\", ...], names[61 % 12] is \"C#\" and "
    "Math.floor(61 / 12) - 1 is 4, so `${names[midi % 12]}${octave}` prints "
    "C#4; names.indexOf(\"E\") + (2 + 1) * 12 is 4 + 36, so E2 is note 40",
    "js_music_midi",
    tuple(_midi_row(row) for row in _MIDIS),
)


# ── 250. MIDI to frequency ───────────────────────────────────

_FREQS = (
    ("hz", 60),
    ("hz", 64),
    ("hz", 36),
    ("hz", 100),
    ("note", "C", 4),
    ("note", "E", 2),
    ("note", "G", 3),
    ("note", "A#", 5),
    ("octaves", 261.63, 1, "up"),
    ("octaves", 55, 3, "up"),
    ("octaves", 880, 2, "down"),
    ("octaves", 329.63, 2, "down"),
    ("tune", 69, 432),
    ("tune", 60, 432),
    ("tune", 72, 442),
    ("tune", 57, 415),
    ("fifth", 60),
    ("fifth", 57),
    ("fifth", 64),
    ("fifth", 45),
)


def _freq_row(row):
    want = row[0]
    if want == "hz":
        midi = row[1]
        return (f"{_A440_SAY} Print the frequency of MIDI note {midi} in Hz, "
                f"to two decimal places.", {"want": want, "midi": midi})
    if want == "note":
        _, note, octave = row
        return (f"{_MIDI_SAY} {_NOTES_SAY} {_A440_SAY} Print the frequency "
                f"of {note}{octave} in Hz, to two decimal places.",
                {"want": want, "note": note, "octave": octave})
    if want == "octaves":
        _, hz, n, way = row
        high = "higher" if way == "up" else "lower"
        return (f"A note sounds at {_say(hz)} Hz. Every octave up doubles the "
                f"frequency and every octave down halves it: print the "
                f"frequency {_plural(n, 'octave')} {high}, in Hz to two "
                f"decimal places.",
                {"want": want, "hz": hz, "octaves": n, "way": way})
    if want == "tune":
        _, midi, ref = row
        return (f"Some producers tune A4 to {ref} Hz instead of 440. Keeping "
                f"A4 as MIDI note 69, and the rule that 12 semitones double "
                f"the frequency, print the frequency of MIDI note {midi} in "
                f"Hz, to two decimal places.",
                {"want": want, "midi": midi, "ref": ref})
    midi = row[1]
    return (f"{_A440_SAY} A fifth above a note is 7 semitones up. For MIDI "
            f"note {midi}, print the frequency of the equal-tempered fifth "
            f"above it, then the frequency of a just fifth, which is exactly "
            f"1.5 times the root, both in Hz to two decimal places.",
            {"want": want, "midi": midi})


FREQ_PAGE = _page(
    "js-music-freq", 250, "Music: MIDI notes as frequencies",
    "Pitch is a frequency in hertz, and the ear hears equal steps as equal "
    "ratios: twelve semitones make an octave, which doubles the frequency, "
    "so each semitone multiplies it by the twelfth root of 2. That is a "
    "power with a fraction in it: 2 ** (1 / 12) is about 1.0595. Anchored "
    "on A4 at 440 Hz, MIDI note 69, a note m has the frequency "
    "440 * 2 ** ((m - 69) / 12): notes below A4 give a negative exponent "
    "and so a smaller number. The ** operator does the power, and the "
    "brackets matter, because ** binds tighter than * and /. A whole "
    "number of octaves is just a power of 2 with a whole exponent, "
    "hz * 2 ** n, and a different tuning only changes the 440. The fifth "
    "shows why instruments disagree: seven semitones is 2 ** (7 / 12), "
    "about 1.4983, a hair under the pure ratio 1.5.",
    "440 * 2 ** ((60 - 69) / 12) is 440 * 2 ** -0.75, about 261.6256, so "
    "middle C prints 261.63 with toFixed(2); 261.63 * 2 ** 1 is 523.26, "
    "the C an octave up",
    "js_music_freq",
    tuple(_freq_row(row) for row in _FREQS),
)


# ── 251. Intervals and transposing ───────────────────────────

_TRANSPOSES = (
    ("up", "A", 5),
    ("up", "D", 7),
    ("up", "B", 13),
    ("up", "F#", 8),
    ("down", "C", 1),
    ("down", "D", 4),
    ("down", "G", 19),
    ("down", "A#", 14),
    ("interval", "C", "E"),
    ("interval", "A", "D"),
    ("interval", "G", "F"),
    ("interval", "B", "C#"),
    ("named", "C", "G"),
    ("named", "E", "C"),
    ("named", "A", "G"),
    ("named", "F", "B"),
    ("melody", ("C", "E", "G", "E"), 5),
    ("melody", ("A", "C", "E"), 3),
    ("melody", ("E", "G", "B", "G"), -5),
    ("melody", ("C", "D#", "G"), 7),
)

_INTERVAL_SAY = ("The twelve intervals going up from a unison are called "
                 "unison, minor 2nd, major 2nd, minor 3rd, major 3rd, "
                 "perfect 4th, tritone, perfect 5th, minor 6th, major 6th, "
                 "minor 7th and major 7th, for 0 to 11 semitones.")


def _transpose_row(row):
    want = row[0]
    if want in ("up", "down"):
        _, note, steps = row
        way = "above" if want == "up" else "below"
        return (f"{_WRAP_SAY} Print the note {_plural(steps, 'semitone')} "
                f"{way} {note}.",
                {"want": want, "note": note, "steps": steps})
    if want == "interval":
        _, one, two = row
        return (f"{_WRAP_SAY} Print how many semitones you go up from {one} "
                f"to reach the next {two}, a number from 1 to 11.",
                {"want": want, "one": one, "two": two})
    if want == "named":
        _, one, two = row
        return (f"{_WRAP_SAY} {_INTERVAL_SAY} Print the name of the interval "
                f"going up from {one} to the next {two}.",
                {"want": want, "one": one, "two": two})
    _, notes, steps = row
    way = f"up by {steps}" if steps > 0 else f"down by {-steps}"
    return (f"{_WRAP_SAY} Move this melody {way} semitones: "
            f"{' '.join(notes)}. Print the new notes in the same order, "
            f"joined by spaces.",
            {"want": want, "notes": notes, "steps": steps})


TRANSPOSE_PAGE = _page(
    "js-music-transpose", 251, "Music: intervals and transposing",
    "An interval is a distance in semitones, and transposing is adding one "
    "to every note. With the names in an array, a note's position is "
    "indexOf, and the new note is names[(index + steps) % 12]: the % wraps "
    "past the end of the octave, so 10 + 5 = 15 becomes 3 and A# moves up "
    "to D#. Going down needs care, because JavaScript's % keeps the sign of "
    "what it divides, so (2 - 4) % 12 is -2, not 10, and -2 is no index. "
    "Adding 12 before the last % repairs it: ((index - steps) % 12 + 12) % "
    "12. The distance between two notes is the same trick, (to - from + 12) "
    "% 12, always between 0 and 11, and that number can index a second "
    "array of interval names. A whole melody is transposed by calling the "
    "same step on each note with map.",
    "with A# at index 10, names[(10 + 5) % 12] is names[3], D#; going down "
    "one from C, (0 - 1) % 12 is -1, so ((0 - 1) % 12 + 12) % 12 is 11, B; "
    "from C to G is (7 - 0 + 12) % 12, 7 semitones, a perfect 5th",
    "js_music_transpose",
    tuple(_transpose_row(row) for row in _TRANSPOSES),
)


# ── 252. Scales and chords ───────────────────────────────────

_SCALES = (
    ("scale", "G", "major"),
    ("scale", "A", "minor"),
    ("scale", "D", "minor pentatonic"),
    ("scale", "E", "blues"),
    ("chord", "F#", "minor"),
    ("chord", "A", "minor 7th"),
    ("chord", "D", "major 7th"),
    ("chord", "G", "dominant 7th"),
    ("inscale", "A", "minor", "G"),
    ("inscale", "C", "major", "F#"),
    ("inscale", "G", "blues", "D#"),
    ("inscale", "D", "major", "F#"),
    ("degree", "D", "major", 5),
    ("degree", "A", "minor", 3),
    ("degree", "F", "dorian", 4),
    ("degree", "C", "minor pentatonic", 4),
    ("progression", "C", (1, 4, 5, 1)),
    ("progression", "G", (1, 5, 6, 4)),
    ("progression", "D", (2, 5, 1)),
    ("progression", "A", (1, 6, 4, 5)),
)


def _scale_say(steps) -> str:
    return (f"{_NOTES_SAY} A pattern of steps counts semitones above the "
            f"root, wrapping round after B.")


def _scales_row(row):
    want, root = row[0], row[1]
    if want == "chord":
        kind = row[2]
        steps = CHORDS[kind]
        return (f"{_scale_say(steps)} The {kind} chord uses the steps "
                f"{_steps(steps)}. Print the notes of {root} {kind}, joined "
                f"by a comma and a space.",
                {"want": want, "root": root, "steps": steps})
    if want == "progression":
        degrees = row[2]
        steps = MODES["major"]
        return (f"{_scale_say(steps)} The major scale uses the steps "
                f"{_steps(steps)}. Chords are named by the scale degree "
                f"their root sits on, counting the root as degree 1. In "
                f"{root} major, print the root notes of the chords on "
                f"degrees {_steps(degrees)}, in that order, joined by a "
                f"space, a dash and a space.",
                {"want": want, "root": root, "steps": steps,
                 "degrees": degrees})
    mode = row[2]
    steps = MODES[mode]
    base = f"{_scale_say(steps)} The {mode} scale uses the steps {_steps(steps)}."
    args = {"want": want, "root": root, "steps": steps}
    if want == "scale":
        return (f"{base} Print the notes of the {root} {mode} scale, joined "
                f"by spaces.", args)
    if want == "inscale":
        test = row[3]
        return (f"{base} Print whether {test} is one of the notes of the "
                f"{root} {mode} scale, true or false.", {**args, "test": test})
    degree = row[3]
    return (f"{base} Print the note at degree {degree} of the {root} {mode} "
            f"scale, counting the root as degree 1.", {**args, "degree": degree})


SCALES_PAGE = _page(
    "js-music-scales", 252, "Music: scales and chords",
    "A scale or a chord is a pattern: how many semitones each note sits "
    "above the root. The major scale is [0, 2, 4, 5, 7, 9, 11], a minor "
    "triad [0, 3, 7], and the same pattern works from any root. Find the "
    "root's position with indexOf, then map every step to "
    "names[(root + step) % 12]; the % wraps notes that run past B back "
    "round to C. join glues the names into one line with whatever "
    "separator you pass. Because the result is an array of names, the "
    "ordinary array tools answer the other questions: includes asks "
    "whether a note belongs to the scale, and scale[degree - 1] picks a "
    "note by its degree, minus 1 because degrees count from 1 while "
    "indexes count from 0. A chord progression is a list of degrees, and "
    "mapping them through the scale gives the root of each chord.",
    "for D, indexOf gives 2, and with steps [0, 4, 7], map gives "
    "names[2], names[6], names[9]: D, F#, A, so join(\", \") prints D, F#, "
    "A; in the D major scale, scale[5 - 1] is A",
    "js_music_scales",
    tuple(_scales_row(row) for row in _SCALES),
)


# ── 253. Decibels ────────────────────────────────────────────

_DBS = (
    ("ratio", 2),
    ("ratio", 0.25),
    ("ratio", 3),
    ("ratio", 0.7),
    ("power", 2),
    ("power", 0.5),
    ("power", 5),
    ("power", 100),
    ("db", -6),
    ("db", 6),
    ("db", -12),
    ("db", 3),
    ("gain", -18, (6, -3.5, 2)),
    ("gain", 0, (-6, -6, 3)),
    ("gain", -24, (12, 6, -1.5, 4)),
    ("gain", -12, (6, 4.5, 3.5)),
    ("fader", 0.5, -6),
    ("fader", 0.8, -3),
    ("fader", 0.9, -1),
    ("fader", 0.25, 6),
)


def _signed(n) -> str:
    return f"+{_say(n)}" if n > 0 else _say(n)


def _db_row(row):
    want = row[0]
    if want == "ratio":
        ratio = row[1]
        return (f"The level of a signal in decibels is 20 times the "
                f"base-10 logarithm of its amplitude ratio. A fader move "
                f"multiplies a signal's amplitude by {_say(ratio)}: print "
                f"the change in decibels, to two decimal places.",
                {"want": want, "ratio": ratio})
    if want == "power":
        ratio = row[1]
        return (f"For power, a change in decibels is 10 times the base-10 "
                f"logarithm of the power ratio. An amplifier stage uses "
                f"{_say(ratio)} times as much power as before: print the "
                f"change in decibels, to two decimal places.",
                {"want": want, "ratio": ratio})
    if want == "db":
        db = row[1]
        return (f"A gain of {db} dB multiplies amplitude by 10 raised to the "
                f"power of the gain divided by 20. Print that amplitude "
                f"ratio, to three decimal places.",
                {"want": want, "db": db})
    if want == "gain":
        _, start, stages = row
        listing = _and(_signed(g) for g in stages)
        return (f"A signal starts at {start} dB and passes through stages "
                f"that change it by {listing} dB. Decibels simply add, so "
                f"print the final level, in the form -13.5 dB.",
                {"want": want, "start": start, "stages": stages})
    _, sample, db = row
    return (f"A sample has an amplitude of {_say(sample)}. A gain of {db} dB "
            f"multiplies amplitude by 10 raised to the power of the gain "
            f"divided by 20: apply it and print the new amplitude, to three "
            f"decimal places.",
            {"want": want, "sample": sample, "db": db})


DB_PAGE = _page(
    "js-music-decibels", 253, "Music: decibels",
    "Loudness is heard in ratios, so engineers use decibels, a logarithmic "
    "scale. For amplitude, dB = 20 * Math.log10(ratio): doubling the "
    "amplitude is +6 dB, halving it is -6 dB, and ten times is +20. A "
    "ratio below 1 gives a negative number, a cut. Power uses 10 instead "
    "of 20, because power goes with the square of amplitude. Going back, "
    "ratio = 10 ** (db / 20), where a fractional power is no problem for "
    "**. The great convenience is that gains in a chain multiply as "
    "ratios but simply add as decibels, so the level after several stages "
    "is a sum: reduce with a starting value does it, and a template "
    "literal adds the unit. Applying a gain to a sample multiplies it by "
    "the ratio. The logarithm of a number that is not a power of 10 is a "
    "long decimal, so toFixed rounds it for printing.",
    "20 * Math.log10(2) is 6.0206, which toFixed(2) prints as 6.02; "
    "10 ** (-6 / 20) is 0.5012, so -6 dB halves the amplitude, and "
    "[6, -3.5].reduce((sum, g) => sum + g, -18) is -15.5",
    "js_music_db",
    tuple(_db_row(row) for row in _DBS),
)


# ── 254. Sample rate arithmetic ──────────────────────────────

_SAMPLES = (
    ("perbeat", 44100, 128),
    ("perbeat", 48000, 140),
    ("perbeat", 44100, 174),
    ("perbeat", 48000, 95),
    ("wav", 44100, 60, 2, 16),
    ("wav", 48000, 60, 2, 24),
    ("wav", 44100, 30, 1, 16),
    ("wav", 96000, 10, 2, 24),
    ("duration", 441000, 44100),
    ("duration", 1000000, 44100),
    ("duration", 96000, 48000),
    ("duration", 123456, 48000),
    ("latency", 512, 44100),
    ("latency", 256, 48000),
    ("latency", 1024, 44100),
    ("latency", 128, 44100),
    ("bitdepth", 8),
    ("bitdepth", 16),
    ("bitdepth", 24),
    ("bitdepth", 32),
)


def _samples_row(row):
    want = row[0]
    if want == "perbeat":
        _, rate, bpm = row
        return (f"A project runs at {rate} samples per second and {bpm} "
                f"beats per minute. Print how many samples one beat lasts, "
                f"to one decimal place.",
                {"want": want, "rate": rate, "bpm": bpm})
    if want == "wav":
        _, rate, seconds, channels, bits = row
        kind = "mono" if channels == 1 else "stereo"
        return (f"An uncompressed WAV file stores {rate} samples per second "
                f"for each channel, each sample {bits // 8} bytes "
                f"({bits}-bit), plus a 44-byte header. For {seconds} seconds "
                f"of {kind} audio, print the file size in bytes, then in "
                f"megabytes (1024 * 1024 bytes) to two decimal places.",
                {"want": want, "rate": rate, "seconds": seconds,
                 "channels": channels, "bits": bits})
    if want == "duration":
        _, count, rate = row
        return (f"An audio clip holds {count} samples recorded at {rate} "
                f"samples per second. Print its length in seconds, to three "
                f"decimal places.",
                {"want": want, "count": count, "rate": rate})
    if want == "latency":
        _, buffer, rate = row
        return (f"An audio interface works in buffers of {buffer} samples at "
                f"{rate} samples per second, and each buffer adds its own "
                f"length in delay. Print that delay in milliseconds, to two "
                f"decimal places.",
                {"want": want, "buffer": buffer, "rate": rate})
    bits = row[1]
    return (f"A {bits}-bit sample can hold 2 to the power of {bits} different "
            f"values, and each bit adds about 6.02 dB of dynamic range. "
            f"Print the number of values, then the dynamic range in dB, to "
            f"two decimal places.",
            {"want": want, "bits": bits})


SAMPLES_PAGE = _page(
    "js-music-samples", 254, "Music: sample rate arithmetic",
    "Digital audio is a list of numbers: a sample rate of 44100 means "
    "44100 of them every second. Everything else is multiplying and "
    "dividing by that rate. A beat lasts 60 / bpm seconds, so it holds "
    "rate * 60 / bpm samples, not always a whole number. A clip's length "
    "is its sample count divided by the rate. The size of an uncompressed "
    "WAV is its samples, rate * seconds * channels, times the bytes in "
    "each sample, bits / 8, plus a small header; dividing by 1024 twice "
    "turns bytes into megabytes. A buffer of 256 samples is 256 / rate "
    "seconds long, times 1000 for milliseconds, and that is the delay it "
    "adds. A sample of b bits holds 2 ** b values, a whole number for a "
    "whole exponent, and each bit adds roughly 6.02 dB of range. The "
    "numbers get big, a minute of audio is millions of samples, but JavaScript "
    "holds whole numbers exactly up to 9 quadrillion, so none of this loses "
    "a digit.",
    "44100 * 60 / 128 is 20671.875, so toFixed(1) prints 20671.9 samples "
    "per beat at 128 bpm; a stereo minute of 16-bit audio at 44100 Hz is "
    "44100 * 60 * 2 * (16 / 8) + 44 = 10584044 bytes, about 10.09 MB",
    "js_music_samples",
    tuple(_samples_row(row) for row in _SAMPLES),
)


# ── 255. Step sequencer patterns ─────────────────────────────

_P = {
    1: "x---x---x---x---",
    2: "--x---x---x---x-",
    3: "x--x--x---x-x---",
    4: "----x-------x---",
    5: "x-x-x-x-x-x-x-x-",
    6: "x--x--x-x--x--x-",
    7: "x-xx-x--x-x-xx--",
}

_STEPS = (
    ("count", 1),
    ("count", 4),
    ("count", 6),
    ("count", 7),
    ("rotate", 3, 1),
    ("rotate", 6, 5),
    ("rotate", 4, 3),
    ("rotate", 5, 3),
    ("positions", 3),
    ("positions", 6),
    ("positions", 4),
    ("positions", 7),
    ("euclid", 16, 5),
    ("euclid", 8, 3),
    ("euclid", 12, 5),
    ("euclid", 16, 3),
    ("layer", 1, 2, "or"),
    ("layer", 4, 3, "or"),
    ("layer", 3, 5, "and"),
    ("layer", 7, 5, "and"),
)

_STEP_SAY = ("A step sequencer pattern is a string of sixteen steps, x for a "
             "hit and - for a rest.")


def _steps_row(row):
    want = row[0]
    if want == "euclid":
        _, steps, hits = row
        return (f"Spread {hits} hits over {steps} steps as evenly as "
                f"possible: hit number i, counting from 0, lands on step "
                f"floor(i times {steps} divided by {hits}), counting steps "
                f"from 0. Print the pattern with x for a hit and - for a "
                f"rest.",
                {"want": want, "steps": steps, "hits": hits})
    if want == "layer":
        _, one, two, how = row
        rule = ("a hit in either pattern" if how == "or"
                else "a hit in both patterns")
        return (f"{_STEP_SAY} Layer the patterns {_P[one]} and {_P[two]} into "
                f"one, where a step is a hit if it is {rule}, and print the "
                f"result.",
                {"want": want, "one": _P[one], "two": _P[two], "how": how})
    pattern = _P[row[1]]
    args = {"want": want, "pattern": pattern}
    if want == "count":
        return (f"{_STEP_SAY} Print how many hits the pattern {pattern} has.",
                args)
    if want == "rotate":
        shift = row[2]
        return (f"{_STEP_SAY} Rotate the pattern {pattern} left by "
                f"{_plural(shift, 'step')}, so its first "
                f"{_plural(shift, 'step')} move to the end, and print the "
                f"new pattern.", {**args, "shift": shift})
    return (f"{_STEP_SAY} For the pattern {pattern}, print the step numbers "
            f"of its hits, counting the first step as 1, joined by a comma "
            f"and a space.", args)


STEPS_PAGE = _page(
    "js-music-steps", 255, "Music: step sequencer patterns",
    "A drum pattern fits in a string: sixteen steps, \"x\" for a hit and "
    "\"-\" for a rest. Spreading the string with [...pattern] makes an "
    "array of its characters, so the array tools apply. filter keeps the "
    "hits and its length counts them. slice cuts a string: pattern.slice(3) "
    "is everything from step 3 on and slice(0, 3) the first three, so "
    "putting them back the other way round, pattern.slice(3) + "
    "pattern.slice(0, 3), rotates the pattern left. A loop with an index "
    "finds where the hits are, and since musicians count steps from 1, "
    "push i + 1. To build a pattern rather than read one, start from "
    "Array(16).fill(\"-\") and set steps to \"x\", then join(\"\") glues "
    "them into a string. The same index reaches two patterns at once, so "
    "map can layer them: || keeps a step if either has a hit and && only "
    "if both do. Placing k hits among n steps evenly means hit i lands at "
    "Math.floor(i * n / k).",
    "with s = \"x--x--x-\", s.slice(3) is \"x--x-\" and s.slice(0, 3) is "
    "\"x--\", so s.slice(3) + s.slice(0, 3) is \"x--x-x--\"; "
    "[...s].filter((c) => c === \"x\").length is 3",
    "js_music_steps",
    tuple(_steps_row(row) for row in _STEPS),
)


# ── 256. Quantize and swing ──────────────────────────────────

_QUANTS = (
    ("snap", 120, 250),
    ("snap", 60, 90),
    ("snap", 240, 700),
    ("snap", 120, 420),
    ("late", 120, 250),
    ("late", 120, 190),
    ("late", 60, 80),
    ("late", 240, 600),
    ("snaplist", 120, (10, 130, 250, 370)),
    ("snaplist", 60, (95, 170, 310)),
    ("snaplist", 240, (100, 360, 610, 900)),
    ("snaplist", 120, (60, 180, 300)),
    ("swing", 125, 55, 4),
    ("swing", 125, 66, 4),
    ("swing", 120, 60, 6),
    ("swing", 100, 58, 4),
    ("bbt", 5000),
    ("bbt", 1920),
    ("bbt", 7777),
    ("bbt", 3000),
)


def _quant_row(row):
    want = row[0]
    if want == "snap":
        _, grid, played = row
        return (f"A drum hit was played at tick {played}, and the grid has a "
                f"line every {grid} ticks. Snap it to the nearest grid line, "
                f"rounding exact halves up, and print the tick it lands on.",
                {"want": want, "grid": grid, "played": played})
    if want == "late":
        _, grid, played = row
        return (f"A drum hit was played at tick {played}, and the grid has a "
                f"line every {grid} ticks. Snap it to the nearest grid line, "
                f"rounding exact halves up, and print how many ticks the "
                f"note moves, positive if it moves later and negative if "
                f"earlier.",
                {"want": want, "grid": grid, "played": played})
    if want == "snaplist":
        _, grid, played = row
        return (f"The grid has a line every {grid} ticks. Snap each of these "
                f"played ticks to its nearest grid line, rounding exact "
                f"halves up: {_steps(played)}. Print the snapped ticks in the "
                f"same order, joined by a comma and a space.",
                {"want": want, "grid": grid, "played": played})
    if want == "swing":
        _, step, swing, count = row
        return (f"A sixteenth-note grid has a step every {step} "
                f"milliseconds. Steps are counted from 0 and come in pairs, "
                f"and the second step of each pair is pushed back so that it "
                f"lands {swing} percent of the way through the pair: the "
                f"pair's start plus 2 times the step length times {swing} "
                f"over 100. Round every step's time to the nearest "
                f"millisecond, halves up, and print the first {count} step "
                f"times, joined by a comma and a space.",
                {"want": want, "step": step, "swing": swing, "count": count})
    ticks = row[1]
    return (f"A MIDI clock has {PPQ} ticks to a beat, and a bar has 4 beats. "
            f"Print the position of tick {ticks} as bar:beat:tick, counting "
            f"bars and beats from 1 and ticks from 0, written like 3:2:15.",
            {"want": want, "ticks": ticks})


QUANTIZE_PAGE = _page(
    "js-music-quantize", 256, "Music: quantize and swing",
    "Quantizing pulls a note that was played a little early or late onto the "
    "nearest line of a grid. Divide the time by the grid to say how many "
    "grid lines in it is, Math.round to the nearest whole line, and "
    "multiply back: Math.round(played / grid) * grid. Math.round sends a "
    "number exactly halfway up, so 2.5 becomes 3 and 1.5 becomes 2: a note "
    "right between two lines goes to the later one. Subtracting the "
    "original shows how far it moved. Swing delays every second step of a "
    "pair: a swing of 50 percent is straight, 66 is a triplet feel, and "
    "the late step lands at the pair's start plus 2 * step * swing / 100. "
    "Reading a position in a MIDI file is the same arithmetic as clock "
    "hands: Math.floor splits off whole bars and beats, and % keeps what "
    "is left over, counting ticks from 0 but bars and beats from 1.",
    "Math.round(250 / 120) * 120 is 2 * 120, so tick 250 snaps to 240, "
    "while Math.round(90 / 60) is Math.round(1.5), which is 2, so tick 90 "
    "on a 60 grid goes to 120; tick 5000 is bar Math.floor(5000 / 1920) + 1 "
    "= 3, beat Math.floor(5000 % 1920 / 480) + 1 = 3, tick 5000 % 480 = "
    "200",
    "js_music_quantize",
    tuple(_quant_row(row) for row in _QUANTS),
)


# ── 257. Tracks: filter, sort, reduce and a table ────────────

_T1 = (("Neon", 124, "Am", 215), ("Dusk", 98, "F#m", 187),
       ("Pulse", 140, "Am", 244), ("Drift", 85, "C", 301))
_T2 = (("Haze", 120, "Dm", 198), ("Wave", 128, "Am", 232),
       ("Ember", 90, "Dm", 176), ("Static", 150, "G", 210))
_T3 = (("Glow", 110, "C", 190), ("Loop", 126, "Em", 205),
       ("Rush", 174, "Em", 175), ("Moon", 80, "A", 260))
_T4 = (("Cloud", 92, "Bm", 240), ("Tide", 132, "Bm", 199),
       ("Bloom", 78, "G", 260), ("Spark", 140, "D", 185))
_T5 = (("Glow", 110, "C", 180), ("Loop", 126, "Em", 200),
       ("Rush", 174, "Em", 175), ("Moon", 80, "A", 230))

_TRACKS = (
    ("filter", _T1, ("bpm", ">", 100)),
    ("filter", _T2, ("key", "=", "Dm")),
    ("filter", _T3, ("secs", "<", 200)),
    ("filter", _T4, ("bpm", "<", 100)),
    ("sort", _T1, "bpm", "up"),
    ("sort", _T2, "bpm", "down"),
    ("sort", _T3, "secs", "up"),
    ("sort", _T4, "secs", "down"),
    ("total", _T1),
    ("total", _T2),
    ("total", _T5),
    ("average", _T2),
    ("average", _T3),
    ("average", _T4),
    ("longest", _T1),
    ("longest", _T3),
    ("longest", _T4),
    ("table", _T1, (8, 4, 5), False),
    ("table", _T2, (8, 4, 5), True),
    ("table", _T4, (9, 5, 6), True),
)

_TRACK_FIELDS = {"bpm": "tempo in bpm", "secs": "length in seconds"}


def _tracks_make(items) -> str:
    listing = "; ".join(f"{n} {b} {k} {s}" for n, b, k, s in items)
    return (f"Make an array of track objects, each with a name, a bpm, a key "
            f"and its length in seconds as secs: {listing}.")


def _which(field: str, op: str, limit) -> str:
    if op == "=":
        return f"in the key of {limit}"
    if field == "bpm":
        return f"faster than {limit} bpm" if op == ">" else f"slower than {limit} bpm"
    return f"longer than {limit} seconds" if op == ">" else f"shorter than {limit} seconds"


def _tracks_row(row):
    want, items = row[0], row[1]
    make = _tracks_make(items)
    args = {"want": want, "items": items}
    if want == "filter":
        field, op, limit = row[2]
        return (f"{make} Print the names of the tracks "
                f"{_which(field, op, limit)}, in the same order, joined by a "
                f"comma and a space.",
                {**args, "test": row[2]})
    if want == "sort":
        field, way = row[2], row[3]
        order = ({"bpm": ("slowest", "fastest"), "secs": ("shortest", "longest")}
                 [field])
        first, last = order if way == "up" else order[::-1]
        return (f"{make} Sort a copy of the array from the {first} track to "
                f"the {last} and print the names in that order, joined by a "
                f"comma and a space.",
                {**args, "field": field, "way": way})
    if want == "total":
        return (f"{make} With reduce, add up the lengths and print the total "
                f"as minutes and seconds in the form 12:05, with the seconds "
                f"padded to two digits.", args)
    if want == "average":
        return (f"{make} With reduce, add up the tempos, divide by how many "
                f"tracks there are, and print the average bpm to one decimal "
                f"place.", args)
    if want == "longest":
        return (f"{make} With reduce, find the longest track and print its "
                f"name and its length in seconds, with a space between.",
                args)
    widths, header = row[2], row[3]
    nw, kw, bw = widths
    lead = ("First print a header line made the same way from the words "
            "Track, Key and BPM, then one line for each track: " if header
            else "For each track print one line: ")
    return (f"{make} {lead}the name padded at the end to {nw} characters, a | "
            f"with a space on each side, the key padded at the end to {kw} "
            f"characters, another such |, and the bpm padded at the start to "
            f"{bw} characters.",
            {**args, "widths": widths, "header": header})


TRACKS_PAGE = _page(
    "js-music-tracks", 257, "Music: a list of tracks",
    "A set list is an array of objects, { name: \"Neon\", bpm: 124, key: "
    "\"Am\", secs: 215 }, and the array methods answer questions about it. "
    "filter((t) => t.bpm > 100) keeps the tracks the test says true for, "
    "map((t) => t.name) pulls one field out, and join(\", \") glues the "
    "result into one line. sort needs a compare function, (a, b) => a.bpm - "
    "b.bpm for slowest first and b.bpm - a.bpm for fastest first; it "
    "rearranges the array itself, so sort a copy, [...tracks]. reduce "
    "carries one value along: a running total from 0, or the longest so "
    "far, (best, t) => (t.secs > best.secs ? t : best). Seconds read better "
    "as minutes and seconds: Math.floor(total / 60), then total % 60 turned "
    "into a string and padded with padStart(2, \"0\") so 5 shows as 05. A "
    "table lines up when every column has one width: padEnd(8) on names, "
    "which read from the left, and padStart(5) on numbers, which line up on "
    "the right, with \" | \" between the columns.",
    "tracks.filter((t) => t.bpm > 100).map((t) => t.name).join(\", \") "
    "gives Neon, Pulse for the first four tracks; a total of 947 seconds is "
    "Math.floor(947 / 60) = 15 minutes and 947 % 60 = 47 seconds, so it "
    "prints 15:47",
    "js_music_tracks",
    tuple(_tracks_row(row) for row in _TRACKS),
)


JSMUSIC_PAGES: tuple[Page, ...] = (
    TEMPO_PAGE,
    MIDI_PAGE,
    FREQ_PAGE,
    TRANSPOSE_PAGE,
    SCALES_PAGE,
    DB_PAGE,
    SAMPLES_PAGE,
    STEPS_PAGE,
    QUANTIZE_PAGE,
    TRACKS_PAGE,
)
