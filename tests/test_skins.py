"""Skins: the rules that keep them honest after today.

The skins were built by turning every hardcoded colour into a variable
whose default is itself, then routing those variables to a handful of
role colours per skin. That works on the day it is done. What goes
wrong afterwards is quieter:

* somebody writes a new colour straight into a stylesheet, and it simply
  does not change with the skin - a dark box in the Light skin that
  nobody notices until a person clicks on that screen;
* a token gets used without a default, and Original - the look that is
  promised never to move - loses that colour;
* a skin forgets one role, and whatever uses it falls back to nothing;
* somebody tunes a skin and pushes some text below readable contrast.

Each of those is a rule, so each is a test. They read the stylesheets
as text, which is the right level: the question is what the CSS says,
not what one browser happened to render on one screen.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

STYLES = Path(__file__).resolve().parent.parent / "web" / "src" / "styles"

#: The stylesheets that are converted. simple.css is not imported by the
#: app, so it is left as it was rather than churned for nothing.
CONVERTED = ("iae.css", "workspace.css", "typing.css", "lessons.css",
             "reference.css", "markup.css")

def _skins_from_app() -> tuple[str, ...]:
    """The skins the app offers, read from skins.ts itself.

    It was a hand-written tuple of four names. A fifth skin added to the
    app would then have been skipped by every test here - contrast,
    completeness, colour-scheme - with nothing failing to say so, which
    is exactly the kind of list this project keeps getting bitten by.
    Original is left out because it has no role colours of its own: it
    is the absence of a skin, checked by the round-trip instead.
    """
    text = (STYLES.parent / "skins.ts").read_text(encoding="utf-8")
    block = text.split("export const SKINS", 1)[1].split("];", 1)[0]
    ids = tuple(re.findall(r'id:\s*"([\w-]+)"', block))
    return tuple(i for i in ids if i != "original")


SKINS = _skins_from_app()

LITERAL = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|rgba?\([^)]*\)")

#: Colours that stay fixed in every skin, on purpose. Each has a reason
#: in skins.css; adding to this list should need one too.
ALLOWED_FIXED = {
    # The white page behind the HTML & CSS previews: it shows what a
    # browser draws, and would be lying on any other colour.
    "#fff",
    # The window-control dots on the terminal.
    "#ff5f57", "#febc2e", "#28c840",
}


def _read(name: str) -> str:
    return (STYLES / name).read_text(encoding="utf-8")


def _strip_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def _rule_bodies(css: str, selector: str) -> str:
    """Every declaration block whose selector is exactly this one."""
    out = []
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        if m.group(1).strip() == selector:
            out.append(m.group(2))
    return "\n".join(out)


def _vars(block: str) -> dict[str, str]:
    return {k: v.strip() for k, v in re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", block)}


class NoStrayColourTests(unittest.TestCase):

    def test_no_hardcoded_colour_escapes_the_skins(self) -> None:
        """A colour written straight into a stylesheet does not change
        with the skin. The only ones allowed are the finger colours,
        which are a code rather than decoration, shadows, and the short
        list above - everything else has to be a token."""
        for name in CONVERTED:
            css = _strip_comments(_read(name))
            if name == "iae.css":
                # The original palette lives here and is overridden by
                # the skins as a whole, so its literals are the point.
                css = re.sub(r":root\s*\{[^}]*\}", "", css, count=1)
            for block in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
                selector, body = block.group(1), block.group(2)
                if ".tk-finger-" in selector:
                    continue
                for line in body.split(";"):
                    for m in LITERAL.finditer(line):
                        lit = re.sub(r"\s+", " ", m.group(0).lower())
                        before = line[: m.start()]
                        if re.search(r"var\(--[\w-]+,\s*$", before):
                            continue            # a fallback, never shown
                        if lit.startswith("rgb") and re.match(
                            r"rgba?\(\s*0\s*,\s*0\s*,\s*0\s*,", lit
                        ):
                            continue            # a shadow
                        with self.subTest(file=name, selector=selector.strip()[:50]):
                            self.assertIn(
                                lit, ALLOWED_FIXED,
                                f"{name}: {lit} in '{selector.strip()[:50]}' is "
                                f"hardcoded, so it will not follow the skin",
                            )


class TokenTests(unittest.TestCase):

    def setUp(self) -> None:
        tokens = _strip_comments(_read("skin-tokens.css"))
        self.defaults = _vars(_rule_bodies(tokens, ":root"))
        self.routed = _vars(_rule_bodies(tokens, ":root[data-skin]"))

    def test_every_token_used_has_a_default(self) -> None:
        """Without one, Original - the look promised never to move -
        silently loses that colour."""
        for name in CONVERTED:
            for tok in set(re.findall(r"var\((--c-[\w-]+)\)", _read(name))):
                with self.subTest(file=name, token=tok):
                    self.assertIn(tok, self.defaults)

    def test_every_token_is_routed_for_skins(self) -> None:
        """A token with a default but no route keeps Original's colour
        in every skin - a dark patch in Light, for example."""
        for tok in self.defaults:
            with self.subTest(token=tok):
                self.assertIn(tok, self.routed)

    def test_a_token_defaults_to_the_colour_its_name_says(self) -> None:
        """The name ends in the literal it replaced. If the two ever
        disagree, somebody edited a default by hand and Original moved."""
        for tok, value in self.defaults.items():
            digits = re.sub(r"[^0-9a-f]", "", value.lower().replace("rgba", "").replace("rgb", ""))
            tail = re.sub(r"[^0-9a-f]", "", tok.split("-")[-1].lower())
            with self.subTest(token=tok):
                self.assertTrue(
                    digits.endswith(tail) or tail in digits,
                    f"{tok} defaults to {value}",
                )


class SkinCompletenessTests(unittest.TestCase):

    def setUp(self) -> None:
        css = _strip_comments(_read("skins.css"))
        tokens = _strip_comments(_read("skin-tokens.css"))
        self.roles_needed = set(
            re.findall(r"var\(--r-([\w-]+)\)",
                       _rule_bodies(tokens, ":root[data-skin]")
                       + _rule_bodies(css, ":root[data-skin]"))
        )
        self.skins = {
            s: _vars(_rule_bodies(css, f'[data-skin="{s}"]')) for s in SKINS
        }

    def test_every_skin_defines_every_role_it_is_asked_for(self) -> None:
        self.assertTrue(self.roles_needed)
        for skin, values in self.skins.items():
            for role in self.roles_needed:
                with self.subTest(skin=skin, role=role):
                    self.assertIn(f"--r-{role}", values)

    def test_every_skin_says_whether_it_is_light_or_dark(self) -> None:
        """Scrollbars and form controls follow color-scheme. Without it
        a Light skin gets dark scrollbars."""
        css = _strip_comments(_read("skins.css"))
        for skin in SKINS:
            body = _rule_bodies(css, f'[data-skin="{skin}"]')
            with self.subTest(skin=skin):
                self.assertRegex(body, r"color-scheme:\s*(light|dark)")


def _luminance(hex_colour: str) -> float:
    n = int(hex_colour.lstrip("#"), 16)
    out = []
    for v in ((n >> 16) & 255, (n >> 8) & 255, n & 255):
        c = v / 255
        out.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = out
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _contrast(a: str, b: str) -> float:
    la, lb = _luminance(a), _luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


class ContrastTests(unittest.TestCase):
    """Readable, measured rather than eyeballed.

    Three pairings failed on the first pass - white on Dark's blue
    buttons, and Arcade's green and yellow text on white - and all three
    looked fine at a glance. That is the case for measuring.

    Thresholds are WCAG: 7 for body text, 4.5 for smaller or secondary
    text and for text on fills, 3 for the dimmest labels.
    """

    PAIRS = (
        ("text", "bg", 7),
        ("text", "bg-panel", 7),
        ("text", "bg-elevated", 4.5),
        ("text-muted", "bg-panel", 4.5),
        ("text-dim", "bg-panel", 3),
        ("accent", "bg-panel", 4.5),
        ("on-accent", "accent", 4.5),
        ("on-strong", "accent-strong", 4.5),
        ("success", "bg-panel", 4.5),
        ("danger", "bg-panel", 4.5),
        ("warning", "bg-panel", 4.5),
        ("text-strong", "accent-soft", 7),
    )

    def test_every_skin_is_readable(self) -> None:
        css = _strip_comments(_read("skins.css"))
        for skin in SKINS:
            values = _vars(_rule_bodies(css, f'[data-skin="{skin}"]'))
            for fg, bg, minimum in self.PAIRS:
                a, b = values[f"--r-{fg}"], values[f"--r-{bg}"]
                with self.subTest(skin=skin, pair=f"{fg} on {bg}"):
                    self.assertGreaterEqual(
                        round(_contrast(a, b), 2), minimum,
                        f"{skin}: {fg} {a} on {bg} {b}",
                    )


if __name__ == "__main__":
    unittest.main()
