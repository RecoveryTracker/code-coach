"""The keyboard itself: what keys exist, where they sit, which finger owns them.

A US QWERTY layout, described once here so the drills and the on-screen
keyboard agree about geometry, fingering and which section a key belongs to.

Rows are physical, sections are pedagogical. `home` is where your fingers rest,
and every other section is described by how you reach out of it — which is how
touch typing is actually taught.
"""

from __future__ import annotations

from dataclasses import dataclass

# Finger ids. Left hand 1–4 is index→pinky, right hand the same, so a drill can
# say "this is a weak-finger key" without caring which hand.
LEFT_INDEX, LEFT_MIDDLE, LEFT_RING, LEFT_PINKY = "li", "lm", "lr", "lp"
RIGHT_INDEX, RIGHT_MIDDLE, RIGHT_RING, RIGHT_PINKY = "ri", "rm", "rr", "rp"
THUMB = "th"

FINGER_NAMES = {
    LEFT_INDEX: "left index",
    LEFT_MIDDLE: "left middle",
    LEFT_RING: "left ring",
    LEFT_PINKY: "left pinky",
    RIGHT_INDEX: "right index",
    RIGHT_MIDDLE: "right middle",
    RIGHT_RING: "right ring",
    RIGHT_PINKY: "right pinky",
    THUMB: "thumb",
}


@dataclass(frozen=True)
class Key:
    """One physical key.

    `char` is what an unshifted press produces; `shifted` what Shift produces.
    A drill targets a *character*, and the trainer works back to the key so it
    can tell you to hold Shift.
    """

    char: str
    shifted: str
    row: str  # number | top | home | bottom
    finger: str
    # How far from the finger's resting key, in keys. 0 is home position.
    reach: int = 0

    @property
    def is_letter(self) -> bool:
        return self.char.isalpha()


def _k(char: str, shifted: str, row: str, finger: str, reach: int = 0) -> Key:
    return Key(char, shifted, row, finger, reach)


# ── The layout ──────────────────────────────────────────────
# Left to right, row by row. Reach is measured from the finger's home key.

NUMBER_ROW: tuple[Key, ...] = (
    _k("`", "~", "number", LEFT_PINKY, 2),
    _k("1", "!", "number", LEFT_PINKY, 2),
    _k("2", "@", "number", LEFT_RING, 2),
    _k("3", "#", "number", LEFT_MIDDLE, 2),
    _k("4", "$", "number", LEFT_INDEX, 2),
    _k("5", "%", "number", LEFT_INDEX, 2),
    _k("6", "^", "number", RIGHT_INDEX, 2),
    _k("7", "&", "number", RIGHT_INDEX, 2),
    _k("8", "*", "number", RIGHT_MIDDLE, 2),
    _k("9", "(", "number", RIGHT_RING, 2),
    _k("0", ")", "number", RIGHT_PINKY, 2),
    _k("-", "_", "number", RIGHT_PINKY, 2),
    _k("=", "+", "number", RIGHT_PINKY, 3),
)

TOP_ROW: tuple[Key, ...] = (
    _k("q", "Q", "top", LEFT_PINKY, 1),
    _k("w", "W", "top", LEFT_RING, 1),
    _k("e", "E", "top", LEFT_MIDDLE, 1),
    _k("r", "R", "top", LEFT_INDEX, 1),
    _k("t", "T", "top", LEFT_INDEX, 1),
    _k("y", "Y", "top", RIGHT_INDEX, 1),
    _k("u", "U", "top", RIGHT_INDEX, 1),
    _k("i", "I", "top", RIGHT_MIDDLE, 1),
    _k("o", "O", "top", RIGHT_RING, 1),
    _k("p", "P", "top", RIGHT_PINKY, 1),
    _k("[", "{", "top", RIGHT_PINKY, 2),
    _k("]", "}", "top", RIGHT_PINKY, 3),
    _k("\\", "|", "top", RIGHT_PINKY, 4),
)

HOME_ROW: tuple[Key, ...] = (
    _k("a", "A", "home", LEFT_PINKY),
    _k("s", "S", "home", LEFT_RING),
    _k("d", "D", "home", LEFT_MIDDLE),
    _k("f", "F", "home", LEFT_INDEX),
    _k("g", "G", "home", LEFT_INDEX, 1),
    _k("h", "H", "home", RIGHT_INDEX, 1),
    _k("j", "J", "home", RIGHT_INDEX),
    _k("k", "K", "home", RIGHT_MIDDLE),
    _k("l", "L", "home", RIGHT_RING),
    _k(";", ":", "home", RIGHT_PINKY),
    _k("'", '"', "home", RIGHT_PINKY, 1),
)

BOTTOM_ROW: tuple[Key, ...] = (
    _k("z", "Z", "bottom", LEFT_PINKY, 1),
    _k("x", "X", "bottom", LEFT_RING, 1),
    _k("c", "C", "bottom", LEFT_MIDDLE, 1),
    _k("v", "V", "bottom", LEFT_INDEX, 1),
    _k("b", "B", "bottom", LEFT_INDEX, 2),
    _k("n", "N", "bottom", RIGHT_INDEX, 2),
    _k("m", "M", "bottom", RIGHT_INDEX, 1),
    _k(",", "<", "bottom", RIGHT_MIDDLE, 1),
    _k(".", ">", "bottom", RIGHT_RING, 1),
    _k("/", "?", "bottom", RIGHT_PINKY, 1),
)

ROWS: tuple[tuple[Key, ...], ...] = (NUMBER_ROW, TOP_ROW, HOME_ROW, BOTTOM_ROW)

ALL_KEYS: tuple[Key, ...] = NUMBER_ROW + TOP_ROW + HOME_ROW + BOTTOM_ROW

# char → the key that produces it, shifted or not.
BY_CHAR: dict[str, Key] = {}
for _key in ALL_KEYS:
    BY_CHAR[_key.char] = _key
    BY_CHAR[_key.shifted] = _key

SPACE = _k(" ", " ", "space", THUMB)
BY_CHAR[" "] = SPACE


def needs_shift(char: str) -> bool:
    """True when producing this character means holding Shift."""
    key = BY_CHAR.get(char)
    return key is not None and char == key.shifted and key.shifted != key.char


def finger_for(char: str) -> str:
    key = BY_CHAR.get(char)
    return key.finger if key else THUMB


# ── Names, so a drill can ask for a symbol by word ──────────
# Recalling where `|` lives is a different skill from copying it off a prompt,
# and naming it is what forces the recall.

SYMBOL_NAMES: dict[str, str] = {
    "`": "backtick",
    "~": "tilde",
    "!": "exclamation mark",
    "@": "at sign",
    "#": "hash",
    "$": "dollar sign",
    "%": "percent",
    "^": "caret",
    "&": "ampersand",
    "*": "asterisk",
    "(": "open paren",
    ")": "close paren",
    "-": "hyphen",
    "_": "underscore",
    "=": "equals",
    "+": "plus",
    "[": "open bracket",
    "]": "close bracket",
    "{": "open brace",
    "}": "close brace",
    "\\": "backslash",
    "|": "pipe",
    ";": "semicolon",
    ":": "colon",
    "'": "single quote",
    '"': "double quote",
    ",": "comma",
    ".": "period",
    "<": "less than",
    ">": "greater than",
    "/": "slash",
    "?": "question mark",
}


def name_for(char: str) -> str:
    """A speakable name, for prompts that test recall rather than copying."""
    if char == " ":
        return "space"
    if char in SYMBOL_NAMES:
        return SYMBOL_NAMES[char]
    if char.isupper():
        return f"capital {char}"
    return char


def keyboard_payload() -> list[dict]:
    """The layout, for drawing the on-screen keyboard."""
    return [
        [
            {
                "char": k.char,
                "shifted": k.shifted,
                "row": k.row,
                "finger": k.finger,
                "reach": k.reach,
            }
            for k in row
        ]
        for row in ROWS
    ]
