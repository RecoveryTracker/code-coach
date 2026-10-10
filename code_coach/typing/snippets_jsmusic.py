"""JavaScript about music production and sound.

The lines are the ones a small studio toolkit is made of: tempo to
milliseconds, MIDI numbers and note names, frequencies from the 440 * 2 **
((m - 69) / 12) formula, transposing with a remainder that survives
negatives, scales as arrays of intervals, decibels and gain, samples per
beat, step-sequencer patterns, quantizing with Math.round, and the Web
Audio API.

The conventions are the usual ones: sharps only, MIDI note 69 is A4 at
440 Hz, middle C is 60 (so C4), and the tempo is in 4/4 unless a line says
otherwise. The Web Audio calls are lines only, because AudioContext is a
browser object and a block that needs one cannot run in Node.

The blocks are whole little programs that print their result, and the
tests run every one in Node and hold what it prints to an answer worked
out by hand - so they read no clock and roll no dice, and every
fractional result goes through toFixed or Math.round so that the last
digit does not depend on how floating point happens to round.
"""

from __future__ import annotations

from code_coach.typing.texts import Passage


def _s(text: str, note: str) -> Passage:
    return Passage(text, note)


# -- Lines ----------------------------------------------------

JSMUSIC_LINES: tuple[Passage, ...] = (
    # Tempo and time
    _s("const beatMs = 60000 / bpm;", "milliseconds in one beat"),
    _s("const barMs = beatMs * 4;", "one bar of 4/4"),
    _s("const sixteenthMs = 60000 / bpm / 4;", "a sixteenth note is a quarter of a beat"),
    _s("const bpm = Math.round(60000 / beatMs);", "tempo from the gap between beats"),
    _s("const dottedEighthMs = (60000 / bpm) * 0.75;",
       "the classic delay time: three sixteenths"),
    _s("const lfoHz = 1000 / periodMs;", "a period in ms is a frequency in Hz"),
    _s("const lengthSec = (bars * 4 * 60) / bpm;", "how long a section lasts, in seconds"),
    _s("const bar = Math.floor(beats / 4) + 1;", "bars are counted from 1, not 0"),
    _s("const beatInBar = (beats % 4) + 1;", "and so are the beats inside them"),
    _s("const avgBpm = 60000 / (gaps.reduce((a, b) => a + b) / gaps.length);",
       "tap tempo: the average gap between taps"),
    _s("const mmss = `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;",
       "seconds as 3:05"),

    # MIDI and note names
    _s("const NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];",
       "the twelve pitch classes, sharps only"),
    _s("const name = NAMES[midi % 12];", "60 is C, 61 is C#, and so on round the octave"),
    _s("const octave = Math.floor(midi / 12) - 1;", "MIDI 60 is in octave 4"),
    _s("const label = NAMES[midi % 12] + (Math.floor(midi / 12) - 1);",
       "69 becomes 'A4'"),
    _s("const midi = NAMES.indexOf(name) + (octave + 1) * 12;",
       "and back: 'A', 4 becomes 69"),
    _s("const m = /^([A-G]#?)(-?\\d+)$/.exec('C#3');", "split a note name into its two parts"),
    _s("const isBlackKey = [1, 3, 6, 8, 10].includes(midi % 12);",
       "the five sharps of each octave"),
    _s("const velocity = Math.round(level * 127);", "MIDI loudness is 0 to 127"),
    _s("const level = Math.min(127, Math.max(0, velocity)) / 127;",
       "clamp first, then scale to 0..1"),
    _s("const ticks = Math.round(beats * 480);", "480 ticks per quarter note, a common PPQ"),

    # Frequencies and pitch
    _s("const hz = 440 * 2 ** ((midi - 69) / 12);", "equal temperament: A4 is 440 Hz"),
    _s("const midiNote = 69 + 12 * Math.log2(hz / 440);",
       "and back, usually not a whole number"),
    _s("const nearest = Math.round(69 + 12 * Math.log2(hz / 440));",
       "the closest note to any frequency"),
    _s("const cents = 1200 * Math.log2(played / target);",
       "how far out of tune: 100 cents is a semitone"),
    _s("const detuned = hz * 2 ** (cents / 1200);", "move a pitch by a number of cents"),
    _s("const octaveUp = hz * 2;", "an octave doubles the frequency"),
    _s("const fifth = root * 2 ** (7 / 12);", "seven semitones up, about 1.498 times"),
    _s("const justFifth = root * (3 / 2);", "the pure fifth is exactly 3 to 2"),
    _s("console.log(`${name}: ${hz.toFixed(2)} Hz`);", "two decimal places is plenty"),
    _s("const wavelengthM = 343 / hz;", "sound travels at about 343 metres a second"),

    # Transposing and scales
    _s("const transposed = notes.map((n) => n + semitones);", "shift every note at once"),
    _s("const pitchClass = ((n % 12) + 12) % 12;",
       "a remainder that stays 0 to 11 even for negative numbers"),
    _s("const down = notes.map((n) => ((n - 5) % 12 + 12) % 12);",
       "five semitones down, wrapped round the octave"),
    _s("const MAJOR = [0, 2, 4, 5, 7, 9, 11];", "whole, whole, half, whole, whole, whole"),
    _s("const MINOR = [0, 2, 3, 5, 7, 8, 10];", "the natural minor scale, in semitones"),
    _s("const PENTATONIC = [0, 3, 5, 7, 10];", "minor pentatonic: five notes, none clash"),
    _s("const scale = MAJOR.map((step) => root + step);", "a scale in any key, as MIDI notes"),
    _s("const inScale = (n) => MAJOR.includes((((n - root) % 12) + 12) % 12);",
       "is this note in the key?"),
    _s("const triad = [0, 4, 7].map((step) => root + step);", "a major chord"),
    _s("const rotate = (a, k) => [...a.slice(k), ...a.slice(0, k)];",
       "modes are a scale started on a different note"),
    _s("const chordHz = triad.map((n) => 440 * 2 ** ((n - 69) / 12));",
       "the frequencies to play together"),

    # Decibels and gain
    _s("const db = 20 * Math.log10(ratio);", "an amplitude ratio as decibels"),
    _s("const ratio = 10 ** (db / 20);", "and back: -6 dB is about half"),
    _s("const gain = 10 ** (-6 / 20);", "0.501: close enough to half the signal"),
    _s("const powerDb = 10 * Math.log10(p1 / p2);", "power uses 10 where amplitude uses 20"),
    _s("const dbfs = 20 * Math.log10(Math.abs(sample));", "0 dBFS is the digital maximum"),
    _s("const peak = Math.max(...samples.map(Math.abs));", "the loudest sample in the buffer"),
    _s("const rms = Math.sqrt(samples.reduce((s, x) => s + x * x, 0) / samples.length);",
       "average loudness: the root of the mean square"),
    _s("const clipped = Math.max(-1, Math.min(1, sample * gain));",
       "anything past full scale is cut flat"),
    _s("const mixed = a.map((x, i) => (x + b[i]) / 2);", "two signals summed, then halved"),

    # Samples and sample rates
    _s("const samplesPerBeat = (60 / bpm) * sampleRate;", "how many samples fit in a beat"),
    _s("const frames = Math.round(seconds * 44100);", "length in samples at CD rate"),
    _s("const seconds = frames / sampleRate;", "and back to time"),
    _s("const nyquist = sampleRate / 2;", "the highest frequency a rate can hold"),
    _s("const bytesPerSecond = sampleRate * channels * (bitDepth / 8);",
       "the size of uncompressed audio"),
    _s("const periodSamples = sampleRate / hz;", "samples in one cycle of a tone"),
    _s("const delaySamples = Math.round((ms / 1000) * sampleRate);", "a delay in whole samples"),

    # Patterns and quantizing
    _s("const kick = [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0];",
       "four on the floor, in sixteen steps"),
    _s("const hits = kick.flatMap((on, i) => (on ? [i] : []));", "which steps are on"),
    _s("const steps = 'x...x...x...x...'.split('').map((c) => c === 'x');",
       "a pattern typed as text"),
    _s("const row = steps.map((on) => (on ? 'x' : '.')).join('');", "and printed back"),
    _s("const grid = Array.from({ length: 16 }, (_, i) => i % 4 === 0);",
       "a fresh array, so no step shares anything with another"),
    _s("const start = step * stepMs + (step % 2 ? swingMs : 0);",
       "swing delays every second step"),
    _s("const rotated = [...steps.slice(-1), ...steps.slice(0, -1)];",
       "shift a pattern one step later, wrapping round"),
    _s("const quantized = Math.round(time / grid) * grid;", "snap to the nearest grid line"),
    _s("const snapped = Math.round(beat * 4) / 4;", "to the nearest sixteenth of a bar"),
    _s("const bpms = tracks.map((t) => t.bpm).toSorted((a, b) => a - b);",
       "a numeric sort: the default one compares text"),

    # Web Audio, in the browser
    _s("const ctx = new AudioContext();", "the audio graph's home"),
    _s("await ctx.resume();", "browsers keep audio suspended until the user has clicked"),
    _s("const osc = ctx.createOscillator();", "a tone generator"),
    _s("osc.type = 'sawtooth';", "sine, square, sawtooth or triangle"),
    _s("osc.frequency.value = 440;", "A4"),
    _s("const gain = ctx.createGain();", "a volume control"),
    _s("gain.gain.setValueAtTime(0, ctx.currentTime);", "start silent, at this moment"),
    _s("gain.gain.linearRampToValueAtTime(1, ctx.currentTime + 0.01);",
       "a ten millisecond attack, to avoid a click"),
    _s("gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 1);",
       "an exponential decay can't reach zero, so aim just above"),
    _s("osc.connect(gain).connect(ctx.destination);", "connect returns its target, so chain"),
    _s("osc.start(ctx.currentTime);", "scheduled on the audio clock, not by setTimeout"),
    _s("osc.stop(ctx.currentTime + 0.5);", "half a second later"),
    _s("osc.frequency.setValueAtTime(hz, when);", "change pitch at an exact time"),
    _s("const filter = new BiquadFilterNode(ctx, { type: 'lowpass', frequency: 800 });",
       "a low-pass filter, built with the constructor"),
    _s("const analyser = ctx.createAnalyser();", "reads the signal for meters and scopes"),
    _s("const when = ctx.currentTime + (step * stepMs) / 1000;",
       "a step's start time on the audio clock"),
    _s("const data = await ctx.decodeAudioData(await (await fetch(url)).arrayBuffer());",
       "load a sound file as an AudioBuffer"),
)


# -- Blocks ---------------------------------------------------

def _b(code: str, note: str) -> Passage:
    return Passage(code, f"JavaScript · {note}")


JSMUSIC_BLOCKS: tuple[Passage, ...] = (
    _b(r"""function beatMs(bpm) {
  return 60000 / bpm;
}

for (const bpm of [60, 90, 120, 140, 174]) {
  const beat = beatMs(bpm);
  const bar = Math.round(beat * 4);
  console.log(`${bpm} bpm: ${beat.toFixed(1)} ms, bar ${bar} ms`);
}""",
       "tempo turned into milliseconds"),
    _b(r"""const NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];

function noteName(midi) {
  return NAMES[midi % 12] + (Math.floor(midi / 12) - 1);
}
function midiOf(name) {
  const m = /^([A-G]#?)(-?\d+)$/.exec(name);
  return NAMES.indexOf(m[1]) + (Number(m[2]) + 1) * 12;
}

console.log([60, 61, 69, 72, 21].map(noteName).join(' '));
console.log(midiOf('A4'), midiOf('C#3'), midiOf('C-1'));""",
       "MIDI numbers to note names and back"),
    _b(r"""function hz(midi) {
  return 440 * 2 ** ((midi - 69) / 12);
}

for (const [name, midi] of [['A4', 69], ['C4', 60], ['A5', 81], ['C2', 36]]) {
  console.log(`${name} ${hz(midi).toFixed(2)} Hz`);
}
console.log(Math.round(69 + 12 * Math.log2(261.63 / 440)));""",
       "equal-tempered frequencies, and the way back"),
    _b(r"""const NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
const pitchClass = (n) => ((n % 12) + 12) % 12;

function transpose(notes, semitones) {
  return notes.map((n) => NAMES[pitchClass(n + semitones)]);
}

const melody = [60, 64, 67, 71];
console.log(transpose(melody, 0).join(' '));
console.log(transpose(melody, -5).join(' '));
console.log(transpose(melody, 14).join(' '));
console.log(pitchClass(-1), -1 % 12);""",
       "transposing a melody with a remainder that handles negatives"),
    _b(r"""const NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
const SCALES = {
  major: [0, 2, 4, 5, 7, 9, 11],
  minor: [0, 2, 3, 5, 7, 8, 10],
  pentatonic: [0, 3, 5, 7, 10],
};

function scale(root, type) {
  return SCALES[type].map((i) => NAMES[(root + i) % 12]);
}
console.log(scale(0, 'major').join(' '));
console.log(scale(9, 'minor').join(' '));
console.log(scale(7, 'pentatonic').join(' '));""",
       "scales as arrays of intervals, in any key"),
    _b(r"""const toDb = (ratio) => 20 * Math.log10(ratio);
const toGain = (db) => 10 ** (db / 20);

console.log(toDb(2).toFixed(2), toDb(0.5).toFixed(2), toDb(10).toFixed(0));
console.log(toGain(-6).toFixed(3), toGain(-20), toGain(6).toFixed(3));
const peak = Math.max(...[0.1, -0.5, 0.25].map(Math.abs));
console.log(`peak ${toDb(peak).toFixed(2)} dBFS`);""",
       "decibels and gain, in both directions"),
    _b(r"""const sampleRate = 44100;

function samplesPerBeat(bpm) {
  return (60 / bpm) * sampleRate;
}

console.log(samplesPerBeat(120), samplesPerBeat(90).toFixed(0));
console.log(Math.round(samplesPerBeat(140)), samplesPerBeat(128).toFixed(2));
console.log(sampleRate / 2, Math.round(0.25 * sampleRate));
console.log((sampleRate * 2 * 16) / 8, 'bytes per second');""",
       "samples per beat at CD rate"),
    _b(r"""const patterns = {
  kick: 'x...x...x...x...',
  snare: '....x.......x...',
  hat: 'x.x.x.x.x.x.x.x.',
};

const bpm = 120;
const stepMs = 60000 / bpm / 4;
for (const [name, p] of Object.entries(patterns)) {
  const hits = [...p].flatMap((c, i) => (c === 'x' ? [i * stepMs] : []));
  console.log(name.padEnd(5), hits.length, hits.slice(0, 3).join(','));
}""",
       "a step sequencer's pattern turned into times"),
    _b(r"""const grid = 0.25;
const played = [0.02, 0.27, 0.49, 0.62, 0.88, 1.13];

const quantize = (t) => Math.round(t / grid) * grid;
const snapped = played.map(quantize);
console.log(snapped.join(' '));
const errors = played.map((t, i) => Math.abs(t - snapped[i]));
console.log(Math.max(...errors).toFixed(2));
console.log(Math.round(0.5), Math.round(1.5), Math.round(2.5), Math.round(-0.5));""",
       "quantizing played notes to a grid"),
    _b(r"""const loops = [
  { name: 'Kick', bpm: 128, gainDb: -3 },
  { name: 'Pad', bpm: 90, gainDb: -12 },
  { name: 'Lead', bpm: 100, gainDb: -6 },
];

loops.sort((a, b) => a.bpm - b.bpm);
for (const t of loops) {
  const g = (10 ** (t.gainDb / 20)).toFixed(2);
  console.log(t.name.padEnd(6) + String(t.bpm).padStart(4) + g.padStart(7));
}""",
       "a mixer table sorted by tempo and lined up"),
)
