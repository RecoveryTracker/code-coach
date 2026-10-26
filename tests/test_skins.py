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


INDUSTRIAL = ("foundry", "blueprint")

#: Roles only the industrial pair reads (skins-industrial.css and the editor
#: theme in skins.ts). Without one, a bevel, the focus ring or a syntax colour
#: silently falls back to nothing.
EXTRA_ROLES = (
    "info", "bevel-hi", "bevel-lo", "focus", "hazard", "hazard-dark",
    "editor-bg",
    "syn-keyword", "syn-string", "syn-number", "syn-comment",
    "syn-function", "syn-type", "syn-punct", "syn-const",
)


def _industrial(skin: str) -> dict[str, str]:
    css = _strip_comments(_read("skins.css"))
    return _vars(_rule_bodies(css, f'[data-skin="{skin}"]'))


def _gq_tokens(skin: str) -> dict[str, str]:
    """The Gotchas card tokens this skin gives the card (skins-industrial.css)."""
    css = _strip_comments(_read("skins-industrial.css"))
    m = re.search(
        r':root\[data-skin="%s"\]\s+\.gq-wrap\s*\{([^{}]*)\}' % skin, css)
    assert m, f"{skin} has no .gq-wrap tokens"
    return {k[2:]: v for k, v in _vars(m.group(1)).items()}


def _split_selectors(selector: str) -> list[str]:
    """Split a selector list on the commas that are not inside brackets."""
    parts, depth, cur = [], 0, ""
    for ch in selector:
        depth += {"(": 1, ")": -1, "[": 1, "]": -1}.get(ch, 0)
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p for p in parts if p.strip()]


def _media_blocks(css: str, header: str) -> list[str]:
    """The bodies of every `@media <header> { ... }` block (braces matched)."""
    out = []
    for m in re.finditer(r"@media\s*\(%s\)\s*\{" % re.escape(header), css):
        depth, i = 1, m.end()
        while depth and i < len(css):
            depth += {"{": 1, "}": -1}.get(css[i], 0)
            i += 1
        out.append(css[m.end(): i - 1])
    return out


class IndustrialSkinTests(unittest.TestCase):
    """Foundry and Blueprint: held to a stricter bar than the older skins.

    The brief was "all text/background pairs at 4.5:1" - so these skins are
    tested on the dimmest label as well, on every surface a label can sit on
    (panel, raised, sunken), on the text of every filled button, on the
    focus ring and on the editor's syntax colours. Each of those is read
    from the stylesheet, so tuning a colour below the line fails here.
    """

    PAIRS = (
        # body text and labels, on every surface
        ("text", "bg", 7), ("text", "bg-panel", 7),
        ("text", "bg-elevated", 7), ("text", "bg-sunken", 7),
        ("text-strong", "accent-soft", 7),
        ("text-muted", "bg", 4.5), ("text-muted", "bg-panel", 4.5),
        ("text-muted", "bg-elevated", 4.5), ("text-muted", "bg-sunken", 4.5),
        ("text-dim", "bg", 4.5), ("text-dim", "bg-panel", 4.5),
        ("text-dim", "bg-elevated", 4.5), ("text-dim", "bg-sunken", 4.5),
        # the colours that carry meaning, as text
        ("accent", "bg-panel", 4.5), ("accent", "bg-elevated", 4.5),
        ("accent", "bg-sunken", 4.5),
        ("success", "bg-panel", 4.5), ("success", "bg-elevated", 4.5),
        ("success", "bg-sunken", 4.5),
        ("danger", "bg-panel", 4.5), ("danger", "bg-elevated", 4.5),
        ("danger", "bg-sunken", 4.5),
        ("warning", "bg-panel", 4.5), ("warning", "bg-elevated", 4.5),
        ("warning", "bg-sunken", 4.5),
        ("info", "bg-panel", 4.5), ("info", "bg-elevated", 4.5),
        # text on the filled buttons (primary / confirm, danger, strong)
        ("on-accent", "accent", 4.5), ("on-accent", "danger", 4.5),
        ("on-accent", "success", 4.5), ("on-accent", "warning", 4.5),
        ("on-strong", "accent-strong", 4.5),
        # the focus ring is a non-text mark: 3:1 on every surface
        ("focus", "bg", 3), ("focus", "bg-panel", 3),
        ("focus", "bg-elevated", 3), ("focus", "bg-sunken", 3),
        # the editor's syntax colours on its own background
        ("syn-keyword", "editor-bg", 4.5), ("syn-string", "editor-bg", 4.5),
        ("syn-number", "editor-bg", 4.5), ("syn-comment", "editor-bg", 4.5),
        ("syn-function", "editor-bg", 4.5), ("syn-type", "editor-bg", 4.5),
        ("syn-punct", "editor-bg", 4.5), ("syn-const", "editor-bg", 4.5),
        ("text", "editor-bg", 7),
    )

    def test_both_skins_are_registered_in_the_app(self) -> None:
        for skin in INDUSTRIAL:
            self.assertIn(skin, SKINS)

    def test_every_extra_role_is_defined_as_a_hex_colour(self) -> None:
        for skin in INDUSTRIAL:
            values = _industrial(skin)
            for role in EXTRA_ROLES:
                with self.subTest(skin=skin, role=role):
                    self.assertRegex(values.get(f"--r-{role}", ""),
                                     r"^#[0-9a-fA-F]{6}$")

    def test_every_pair_meets_its_contrast(self) -> None:
        for skin in INDUSTRIAL:
            values = _industrial(skin)
            for fg, bg, minimum in self.PAIRS:
                a, b = values[f"--r-{fg}"], values[f"--r-{bg}"]
                with self.subTest(skin=skin, pair=f"{fg} on {bg}"):
                    self.assertGreaterEqual(
                        round(_contrast(a, b), 2), minimum,
                        f"{skin}: {fg} {a} on {bg} {b}",
                    )

    def test_the_gotchas_card_tokens_stay_readable(self) -> None:
        """The card has its own colours (gotchas.css) and these two skins
        replace them; the same 4.5:1 rule the card is held to everywhere."""
        names = ("gq-text", "gq-dim", "gq-ok", "gq-bad", "tk-keyword",
                 "tk-string", "tk-number", "tk-comment", "tk-fn", "tk-const",
                 "tk-punct", "tk-type", "tk-preproc")
        for skin in INDUSTRIAL:
            t = _gq_tokens(skin)
            for surface in ("gq-bg", "gq-panel"):
                for name in names:
                    with self.subTest(skin=skin, token=name, on=surface):
                        self.assertGreaterEqual(
                            round(_contrast(t[name], t[surface]), 2), 4.5,
                            f"{skin}: {name} {t[name]} on {surface} {t[surface]}",
                        )

    def test_every_rule_is_scoped_to_its_own_skin(self) -> None:
        """No other skin, and not Original (which has no data-skin at all),
        can move: every selector in the file starts with one of the two."""
        css = _strip_comments(_read("skins-industrial.css"))
        # at-rules are checked separately; look only at plain rules
        flat = re.sub(r"@media[^{]*\{", "", css)
        flat = re.sub(r"@keyframes[^{]*\{[^{}]*(\{[^{}]*\}[^{}]*)*\}", "", flat)
        count = 0
        for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", flat):
            selector = m.group(1).strip()
            if not selector:
                continue
            for part in _split_selectors(selector):
                count += 1
                with self.subTest(selector=part.strip()[:70]):
                    self.assertRegex(
                        part.strip(),
                        r'^:root\[data-skin="(foundry|blueprint)"\]',
                    )
        self.assertGreater(count, 40)

    def test_no_gradient_wash_on_the_bars_or_the_page(self) -> None:
        """The brief: no faded colour washes along the top bar or page.
        A gradient may only sit on a progress fill, a hazard mark or
        Blueprint's grid on the question screen."""
        css = _strip_comments(_read("skins-industrial.css"))
        allowed = ("-fill", "danger-warn", "gq-badge", "gq-error", "wb-stderr",
                   "brain-run-err", "ticket-report", "brain-stage")
        for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
            selector, body = m.group(1), m.group(2)
            if "gradient" not in body:
                continue
            with self.subTest(selector=" ".join(selector.split())[:80]):
                self.assertTrue(
                    any(a in selector for a in allowed),
                    f"a gradient on '{selector.strip()[:60]}'",
                )
        for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
            selector, body = m.group(1), m.group(2)
            if re.search(r"mode-bar|ws-top|iae-topbar|\bbody\b|:root\[[^\]]*\]\s*\{", selector + "{"):
                with self.subTest(bar=" ".join(selector.split())[:60]):
                    self.assertNotIn("gradient", body)

    def test_animation_only_for_people_who_have_not_asked_for_less(self) -> None:
        css = _strip_comments(_read("skins-industrial.css"))
        allowed = "\n".join(_media_blocks(css, "prefers-reduced-motion: no-preference"))
        self.assertIn("animation", allowed)
        outside = css
        for block in _media_blocks(css, "prefers-reduced-motion: no-preference"):
            outside = outside.replace(block, "")
        self.assertNotRegex(outside, r"animation\s*:")
        self.assertNotRegex(outside, r"transition\s*:")

    def test_bevels_do_not_change_layout_size(self) -> None:
        """Bevels are shadows and colours. A border width (or a margin, or an
        explicit size) on a Foundry plate would shift the page by a pixel
        and so move everything under it."""
        css = _strip_comments(_read("skins-industrial.css"))
        for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
            selector, body = m.group(1), m.group(2)
            if "hazard" in body or "danger-warn" in selector:
                continue        # the hazard edge widens a note's left padding
            for prop in ("border-width", "margin", "width", "height",
                         "min-width", "min-height", "font-size"):
                with self.subTest(selector=" ".join(selector.split())[:60], prop=prop):
                    self.assertNotRegex(body, r"(^|[;\s])%s\s*:" % prop)


if __name__ == "__main__":
    unittest.main()
