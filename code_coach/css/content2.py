"""Inheritance and layout.

Split from content.py for the same reason the kata files are split:
one screenful of related questions is easier to argue with than four.
"""

from __future__ import annotations

from code_coach.css import StyleQuiz, _q
from code_coach.css.content import GREEN

BLACK = "rgb(0, 0, 0)"


# -- What is inherited ----------------------------------------

INHERIT: tuple[StyleQuiz, ...] = (
    _q(
        id="css-color-inherits",
        level=1,
        name="Through a div that says nothing",
        family="What is inherited",
        html='<div class="wrap"><div><p id="t">Text</p></div></div>',
        css=".wrap { color: green; }",
        target="#t",
        prop="color",
        expect=GREEN,
        distractors=(BLACK,),
        why=(
            "Colour is an inherited property, and inheritance goes all "
            "the way down until something stops it. The div in between "
            "having no colour of its own does not interrupt anything: it "
            "inherits green too, and passes it on. This is the whole "
            "reason you can set a typeface once on body."
        ),
    ),
    _q(
        id="css-border-does-not-inherit",
        level=2,
        name="A border on the parent",
        family="What is inherited",
        html='<div class="wrap"><p id="t">Text</p></div>',
        css=".wrap { border: 3px solid red; }",
        target="#t",
        prop="border-top-style",
        expect="none",
        distractors=("solid",),
        why=(
            "Borders, backgrounds, padding, margins and every other "
            "box-drawing property are not inherited. Roughly, what is "
            "inherited is what concerns text - colour, font, "
            "line-height, letter-spacing - and what is not is anything "
            "that would look absurd repeated on every descendant. A "
            "border that inherited would draw one around every word."
        ),
    ),
    _q(
        id="css-em-compounds",
        level=3,
        name="An em inside an em",
        family="What is inherited",
        html=(
            '<div style="font-size: 20px;">'
            '<div style="font-size: 1.5em;">'
            '<span id="t">Text</span></div></div>'
        ),
        css="#t { font-size: 1.5em; }",
        target="#t",
        prop="font-size",
        expect="45px",
        distractors=("30px", "24px", "1.5em"),
        why=(
            "An em is relative to the font size of the element's parent, "
            "which has already been resolved - so they compound. Twenty "
            "becomes thirty becomes forty-five. Nest three lists that "
            "each set font-size in em and the innermost one is "
            "unreadable, which is the bug rem was invented to end."
        ),
    ),
    _q(
        id="css-rem-ignores-the-parent",
        level=3,
        name="A rem inside the same nesting",
        family="What is inherited",
        html=(
            '<div style="font-size: 20px;">'
            '<div style="font-size: 1.5em;">'
            '<span id="t">Text</span></div></div>'
        ),
        css="#t { font-size: 1.5rem; }",
        target="#t",
        prop="font-size",
        expect="24px",
        distractors=("45px", "30px", "1.5rem"),
        why=(
            "A rem is relative to the root element's font size, which is "
            "16px unless something changed it, so this is 24px however "
            "deeply it is nested. Same document, same nesting, same "
            "number written - and a different answer from the em above, "
            "which is the comparison worth holding on to."
        ),
    ),
    _q(
        id="css-unitless-line-height",
        level=5,
        name="Line-height with a unit and without",
        family="What is inherited",
        html=(
            '<div style="font-size: 10px; line-height: 2em;">'
            '<p id="t" style="font-size: 30px;">Text</p></div>'
        ),
        css="",
        target="#t",
        prop="line-height",
        expect="20px",
        distractors=("60px", "2em", "normal"),
        why=(
            "line-height: 2em is resolved where it is written - two "
            "times ten, so 20px - and that computed 20px is what gets "
            "inherited, even by a child whose own text is 30px and now "
            "overlaps. A unitless line-height: 2 inherits the factor "
            "instead, and each element multiplies by its own size, "
            "giving 60px here. That is why the advice is always "
            "unitless."
        ),
    ),
)


# -- Laying it out --------------------------------------------

LAYOUT: tuple[StyleQuiz, ...] = (
    _q(
        id="css-flex-one-splits",
        level=2,
        name="Two children sharing a row",
        family="Laying it out",
        html=(
            '<div class="row"><div id="t">A</div><div>B</div></div>'
        ),
        css=(
            ".row { display: flex; width: 300px; }\n"
            ".row > div { flex: 1; }"
        ),
        target="#t",
        prop="width",
        expect="150px",
        distractors=("300px", "0px", "auto"),
        why=(
            "flex: 1 is shorthand for grow 1, shrink 1, basis 0 - and "
            "the basis of zero is the part that matters. With no basis "
            "to start from, the whole 300px is free space and gets "
            "divided by the grow factors, so equal factors give equal "
            "widths regardless of content. flex: auto keeps the content "
            "width as the basis and divides only what is left, which is "
            "why two columns with different amounts of text come out "
            "uneven under one and even under the other."
        ),
    ),
    _q(
        id="css-align-items-stretch",
        level=3,
        name="A short child in a tall row",
        family="Laying it out",
        html='<div class="row"><div id="t">A</div></div>',
        css=".row { display: flex; height: 100px; }",
        target="#t",
        prop="height",
        expect="100px",
        distractors=("0px", "18px", "auto"),
        why=(
            "The default align-items is stretch, so a flex child with no "
            "height of its own fills the cross axis. People reach for "
            "height: 100% to get this and then wonder why it works "
            "without it. The corollary is the other way round: a child "
            "that looks mysteriously too tall in a flex row is usually "
            "being stretched, and align-items: flex-start stops it."
        ),
    ),
    _q(
        id="css-absolute-needs-a-positioned-ancestor",
        level=4,
        name="Absolute inside a plain div",
        family="Laying it out",
        html=(
            '<div style="width: 400px;">'
            '<div style="width: 200px;">'
            '<div id="t">A</div></div></div>'
        ),
        css="#t { position: absolute; width: 50%; }",
        target="#t",
        prop="width",
        expect="400px",
        distractors=("200px", "100px", "50%"),
        why=(
            "An absolutely positioned box is sized and placed against "
            "its nearest positioned ancestor, and neither div here is "
            "positioned, so it goes up to the initial containing block - "
            "the viewport, 800px wide in the frame these run in. Half of "
            "that is 400. Adding position: relative to the 200px div is "
            "the whole fix, and forgetting it is why an absolute element "
            "so often appears in the top-left corner of the page instead "
            "of where it was wanted."
        ),
    ),
    _q(
        id="css-z-index-needs-position",
        level=4,
        name="z-index on a static element",
        family="Laying it out",
        html='<div id="t">A</div>',
        css="#t { z-index: 5; }",
        target="#t",
        prop="z-index",
        expect="5",
        distractors=("auto", "0", "none"),
        why=(
            "Two things are true at once here and the second is the "
            "lesson. z-index does nothing on a statically positioned "
            "element: the div takes part in no stacking context and "
            "sits exactly where it would have without the declaration. "
            "And the computed value is 5 anyway - the property computes "
            "to what you wrote whether or not anything uses it. So the "
            "devtools panel shows 5, in black text, next to an element "
            "the 5 has no effect on. A value being in the computed "
            "styles is not evidence that it applied. The fix is "
            "position: relative with no offsets, which changes no "
            "layout and makes the same 5 start counting."
        ),
    ),
    _q(
        id="css-inline-ignores-width",
        level=3,
        name="A width on a span",
        family="Laying it out",
        html='<div style="width: 500px;"><span id="t"></span></div>',
        css="#t { width: 300px; }",
        target="#t",
        prop="rect.width",
        expect="0px",
        distractors=("300px", "500px"),
        why=(
            "Width and height do not apply to non-replaced inline "
            "boxes. The span is as wide as its contents, which here is "
            "nothing, so it takes up no width at all and the 300px is "
            "dropped on the floor. Worth knowing: computed style still "
            "reports 300px - the declaration is kept, it just governs "
            "nothing - so devtools will show you the number while the "
            "page ignores it. Vertical padding is the other half of the "
            "trap: not ignored, but it pushes nothing away and simply "
            "overlaps the lines above and below. display: inline-block "
            "ends both."
        ),
    ),
    _q(
        id="css-transform-percent-is-self",
        level=5,
        name="Per cent in a translate",
        family="Laying it out",
        html=(
            '<div style="width: 400px;">'
            '<div id="t" style="width: 80px; height: 40px;">A</div></div>'
        ),
        css="#t { transform: translateX(50%); }",
        target="#t",
        prop="transform",
        expect="matrix(1, 0, 0, 1, 40, 0)",
        distractors=(
            "matrix(1, 0, 0, 1, 200, 0)",
            "matrix(1, 0, 0, 1, 50, 0)",
            "none",
        ),
        why=(
            "A percentage in a transform is a percentage of the element "
            "itself, not of its container - unlike almost every other "
            "percentage in CSS, which measures the containing block. "
            "Half of the element's own 80px is 40. That is what makes "
            "the translate(-50%, -50%) centring trick work: it can shift "
            "a box by exactly half its own size without anything knowing "
            "what that size is."
        ),
    ),
)
