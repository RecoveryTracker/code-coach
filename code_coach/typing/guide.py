"""Teaching material: which finger owns which key, technique, and an FAQ.

This is data rather than markup so the trainer and any future surface (a print
sheet, a lesson panel) show the same thing, and so the finger map is generated
from the keyboard model instead of being a second copy that can drift out of
sync with it.

The tone is deliberately plain. Most typing advice is either a list of rules
with no reason attached, or posture diagrams nobody follows. What's here is
the small number of things that actually change how fast you end up typing.
"""

from __future__ import annotations

from dataclasses import dataclass

from code_coach.typing.keys import (
    ALL_KEYS,
    FINGER_NAMES,
    HOME_ROW,
    LEFT_INDEX,
    LEFT_MIDDLE,
    LEFT_PINKY,
    LEFT_RING,
    RIGHT_INDEX,
    RIGHT_MIDDLE,
    RIGHT_PINKY,
    RIGHT_RING,
    THUMB,
)

# The key each finger rests on. Everything else is a reach from here, and
# "return to home" is the single habit that separates touch typing from fast
# hunting.
RESTING_KEY: dict[str, str] = {
    LEFT_PINKY: "a",
    LEFT_RING: "s",
    LEFT_MIDDLE: "d",
    LEFT_INDEX: "f",
    RIGHT_INDEX: "j",
    RIGHT_MIDDLE: "k",
    RIGHT_RING: "l",
    RIGHT_PINKY: ";",
    THUMB: "space",
}

LEFT_FINGERS = (LEFT_PINKY, LEFT_RING, LEFT_MIDDLE, LEFT_INDEX)
RIGHT_FINGERS = (RIGHT_INDEX, RIGHT_MIDDLE, RIGHT_RING, RIGHT_PINKY)


@dataclass(frozen=True)
class FingerGuide:
    finger: str
    name: str
    hand: str  # left | right
    home: str
    keys: tuple[str, ...]
    note: str


# Why each finger is worth thinking about separately. The index fingers do the
# most work and the pinkies do the hardest, which is backwards from how much
# attention they usually get.
FINGER_NOTES: dict[str, str] = {
    LEFT_PINKY: (
        "The weakest finger with the most awkward job: A, Q, Z, Tab, Caps and "
        "the left Shift. Expect it to be your slowest, and don't fix that by "
        "letting the ring finger take over — that twists the whole hand."
    ),
    LEFT_RING: (
        "S, W and X. Ring and pinky move together whether you want them to or "
        "not, so this one improves mostly by slowing down until it stops "
        "dragging its neighbour along."
    ),
    LEFT_MIDDLE: (
        "D, E and C. The longest finger, so it reaches the top row easily — "
        "which makes E, the most common letter in English, one of the cheapest "
        "keys on the board."
    ),
    LEFT_INDEX: (
        "F, G, R, T, V, B — six keys, the most of any finger. The bump on F is "
        "there so you can find home position without looking."
    ),
    RIGHT_INDEX: (
        "J, H, U, Y, N, M. The other six-key finger, and the other bump. If "
        "you only ever check one thing about your hands, check that these two "
        "fingers are on F and J."
    ),
    RIGHT_MIDDLE: (
        "K, I and the comma. Reaches up as easily as its left-hand twin, which "
        "is why I is fast and O is not."
    ),
    RIGHT_RING: (
        "L, O and the period. Same ring-finger problem as the left, made worse "
        "because O is far more common than W."
    ),
    RIGHT_PINKY: (
        "Semicolon, P, slash, quotes, brackets, Enter, right Shift — and every "
        "shifted symbol on the right of the board. It is the busiest pinky in "
        "typing and the reason braces and pipes feel so awkward."
    ),
    THUMB: (
        "Space, and nothing else. Use one thumb consistently rather than "
        "whichever is closer; alternating adds a decision to the most frequent "
        "keystroke you make."
    ),
}


def finger_guide() -> list[dict]:
    """Every finger, the keys it owns, and why it behaves the way it does."""
    out: list[dict] = []
    for finger in (*LEFT_FINGERS, *RIGHT_FINGERS, THUMB):
        keys = [k.char for k in ALL_KEYS if k.finger == finger]
        out.append(
            {
                "finger": finger,
                "name": FINGER_NAMES[finger],
                "hand": "left" if finger in LEFT_FINGERS else "right",
                "home": RESTING_KEY[finger],
                "keys": keys if finger != THUMB else [" "],
                "note": FINGER_NOTES[finger],
            }
        )
    return out


def home_row_guide() -> list[dict]:
    """The resting position, left to right, for drawing the hand diagram."""
    return [
        {
            "char": k.char,
            "finger": k.finger,
            "name": FINGER_NAMES[k.finger],
            "anchor": k.char in ("f", "j"),  # the two keys with a bump
        }
        for k in HOME_ROW
    ]


# ── Technique ───────────────────────────────────────────────

TIPS: tuple[tuple[str, str], ...] = (
    (
        "Accuracy first, speed second",
        "Every mistake costs three things: noticing it, deleting it, and "
        "typing it again. That's slower than having typed it carefully the "
        "first time. Speed is what happens to accurate typing over a few "
        "weeks; it isn't something you practise directly.",
    ),
    (
        "Return to home position",
        "After a reach, the finger comes back to a s d f / j k l ;. This is "
        "the whole trick. It means your hands always know where they are, so "
        "the next key is a known distance away instead of a fresh search.",
    ),
    (
        "Find F and J by feel",
        "Both have a raised bump. Put your index fingers on them without "
        "looking, let the other fingers fall into place, and you're home. Do "
        "this every time you come back to the keyboard.",
    ),
    (
        "Don't look down",
        "Looking down is the habit that caps your speed, because it means "
        "your eyes leave the text and have to find their place again. It "
        "feels slower not to look, for about a week.",
    ),
    (
        "Use the far Shift",
        "Capital A uses the right Shift, capital L uses the left. Reaching "
        "for the near Shift with the same hand contorts it and costs more "
        "than the reach saves.",
    ),
    (
        "Practise the keys you avoid",
        "Most people are fluent across the letters and hunt for braces, "
        "pipes, tildes and the number row. That's where your time actually "
        "goes — the results screen here ranks keys by how long you took, so "
        "you can see it rather than guess.",
    ),
    (
        "Short and often beats long and rare",
        "Ten minutes a day builds the habit better than an hour on Sunday. "
        "This is motor learning, and motor learning consolidates between "
        "sessions rather than during them.",
    ),
    (
        "Let your wrists float",
        "Resting your wrists on the desk anchors your hands, so reaches "
        "become finger stretches instead of small hand movements. Keep them "
        "off the desk and let the whole hand shift slightly.",
    ),
)

FAQ: tuple[tuple[str, str], ...] = (
    (
        "What's a good words-per-minute?",
        "Around 40 wpm is an average adult typist. 60–70 is comfortably fast "
        "and enough that typing stops being the bottleneck. Above 90 is rare "
        "and mostly matters for transcription. For programming, accuracy on "
        "symbols matters far more than raw prose speed.",
    ),
    (
        "How is wpm calculated here?",
        "The standard way: five characters counts as one word, so \"word\" and "
        "\"words\" aren't scored differently for being different lengths. Only "
        "correct keystrokes count toward the total.",
    ),
    (
        "Should I delete my mistakes or not?",
        "Both are worth practising, which is why it's a toggle. Blocking "
        "wrong keys keeps a drill flowing and trains your fingers on the "
        "right movement. Making you backspace is what real typing is like, "
        "and trains you to notice errors rather than let them accumulate. "
        "Use blocking while you learn a section, and switch to deleting once "
        "it's comfortable.",
    ),
    (
        "Why does it stop me repeating the same key?",
        "In the reaction drills, pressing a key you're already on measures "
        "how fast you can press twice, not how fast you can find it. The "
        "generator never asks for the same target twice in a row.",
    ),
    (
        "Why isn't the key lit up in Name to Key?",
        "Because that mode is asking whether you remember where it lives. "
        "The board stays dark until you get it wrong, and then it shows you "
        "— being shown at the moment you needed it is what makes it stick.",
    ),
    (
        "Why doesn't the bottom row have a Words mode?",
        "Z X C V B N M contains no vowels, so no English word can be typed "
        "from that row alone. A mode is only offered where it can teach "
        "something.",
    ),
    (
        "Does it matter which fingers I use?",
        "Yes, more than anything else on this page. Any consistent assignment "
        "beats an inconsistent one, and the standard assignment is worth "
        "learning because it minimises how far each finger travels. "
        "Retraining costs a couple of frustrating weeks and then pays out "
        "for the rest of your life.",
    ),
    (
        "My speed got worse when I stopped looking down. Is that normal?",
        "Yes, and it's the usual reason people give up. You're trading a "
        "technique with a low ceiling for one with a high ceiling, and the "
        "new one starts slower. It typically takes one to two weeks to get "
        "back to where you were, and then it keeps going.",
    ),
    (
        "What are Key Pairs for?",
        "Fast typing isn't produced one key at a time — the hand learns "
        "combinations. TH, ER, ING and the rest are the units English is "
        "actually built from, and drilling them directly is faster than "
        "waiting to meet them inside words.",
    ),
    (
        "Where does the scripture text come from?",
        "The King James Version, published in 1611 and in the public domain "
        "worldwide. Modern translations such as the NIV and ESV are under "
        "copyright and aren't included.",
    ),
)


def guide_payload() -> dict:
    return {
        "fingers": finger_guide(),
        "home_row": home_row_guide(),
        "tips": [{"title": t, "body": b} for t, b in TIPS],
        "faq": [{"question": q, "answer": a} for q, a in FAQ],
    }
