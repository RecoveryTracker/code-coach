"""The questions themselves.

Every expected value in this file was copied out of Chromium by
tools/verify_css.py rather than typed from memory. Several of them
surprised the person writing them, which is the point of the mode and
also the reason the verifier exists.
"""

from __future__ import annotations

from code_coach.css import StyleQuiz, _q

RED, GREEN, BLUE = "rgb(255, 0, 0)", "rgb(0, 128, 0)", "rgb(0, 0, 255)"
PURPLE, ORANGE = "rgb(128, 0, 128)", "rgb(255, 165, 0)"


# -- Which rule wins ------------------------------------------

CASCADE: tuple[StyleQuiz, ...] = (
    _q(
        id="css-source-order",
        level=1,
        name="Two classes, one element",
        family="Which rule wins",
        html='<p class="b a" id="t">Text</p>',
        css=".a { color: red; }\n.b { color: green; }",
        target="#t",
        prop="color",
        expect=GREEN,
        distractors=(RED,),
        why=(
            "The two rules have the same specificity, so the one written "
            "later in the stylesheet wins. The order the classes are "
            "listed in the attribute has nothing to do with it: "
            'class="b a" and class="a b" give the same result. Believing '
            "otherwise is the usual reason a class 'does not work' until "
            "it is moved in the HTML, which changes nothing."
        ),
    ),
    _q(
        id="css-id-beats-classes",
        level=2,
        name="One id against three classes",
        family="Which rule wins",
        html='<p class="x y z" id="t">Text</p>',
        css="#t { color: red; }\n.x.y.z { color: green; }",
        target="#t",
        prop="color",
        expect=RED,
        distractors=(GREEN,),
        why=(
            "Specificity is not a total that can be added up across "
            "columns. It is compared column by column: ids first, then "
            "classes, then elements. One id beats any number of classes, "
            "because the id column is looked at first and 1 is more than "
            "0. A hundred classes would still lose."
        ),
    ),
    _q(
        id="css-class-beats-two-elements",
        level=2,
        name="A class against a descendant chain",
        family="Which rule wins",
        html='<div><section><p class="note" id="t">Text</p></section></div>',
        css="div section p { color: red; }\np.note { color: green; }",
        target="#t",
        prop="color",
        expect=GREEN,
        distractors=(RED,),
        why=(
            "Three tag names look more specific than one class and are "
            "not: 0-0-3 against 0-1-1, and the class column is compared "
            "before the element column. Long descendant chains feel "
            "precise while carrying almost no weight, which is why they "
            "keep losing to a single class added later."
        ),
    ),
    _q(
        id="css-important-beats-inline",
        level=4,
        name="Important against a style attribute",
        family="Which rule wins",
        html='<p class="x" id="t" style="color: blue;">Text</p>',
        css=".x { color: green !important; }",
        target="#t",
        prop="color",
        expect=GREEN,
        distractors=(BLUE,),
        why=(
            "A style attribute beats any selector in the stylesheet, and "
            "!important is not a selector. It moves the declaration into "
            "an earlier stage of the cascade, resolved before "
            "specificity is ever consulted. So a class with !important "
            "beats an inline style, and only an inline style that is "
            "itself !important would win it back."
        ),
    ),
    _q(
        id="css-universal-beats-inheritance",
        level=4,
        name="The universal selector against an inherited colour",
        family="Which rule wins",
        html='<div><p id="t">Text</p></div>',
        css="* { color: red; }\nbody { color: green; }",
        target="#t",
        prop="color",
        expect=RED,
        distractors=(GREEN,),
        why=(
            "The universal selector has zero specificity, which makes "
            "this look like the body rule should win. It does not, "
            "because the two are not competing. Body's colour reaches "
            "the paragraph only by inheritance, and any declaration that "
            "matches the element directly - however weak - beats "
            "anything inherited. Inheritance is the last resort, not a "
            "weak competitor."
        ),
    ),
    _q(
        id="css-attribute-is-a-class",
        level=3,
        name="An attribute selector's weight",
        family="Which rule wins",
        html='<input type="text" id="t" class="field">',
        css='.field { color: green; }\ninput[type="text"] { color: red; }',
        target="#t",
        prop="color",
        expect=RED,
        distractors=(GREEN,),
        why=(
            "An attribute selector counts in the class column, so "
            'input[type="text"] is 0-1-1 against .field at 0-1-0. The '
            "class columns tie at one each, so the comparison moves to "
            "the element column, where one beats none. An attribute "
            "selector is worth exactly a class, no more - the tag name "
            "in front of it is what settled this."
        ),
    ),
    _q(
        id="css-where-costs-nothing",
        level=5,
        name="Inside :where()",
        family="Which rule wins",
        html='<p class="x" id="t">Text</p>',
        css=":where(#t) { color: red; }\np { color: green; }",
        target="#t",
        prop="color",
        expect=GREEN,
        distractors=(RED,),
        why=(
            "Everything inside :where() has its specificity zeroed, id "
            "included. So :where(#t) is 0-0-0 and loses to a bare tag "
            "name. That is what :where() is for - offering defaults that "
            "anything at all can override - and it is the one place a "
            "selector containing an id can lose to one that does not."
        ),
    ),
)


# -- The box --------------------------------------------------

BOX: tuple[StyleQuiz, ...] = (
    _q(
        id="css-content-box-width",
        level=3,
        name="Width with padding and a border",
        family="The box",
        html='<div id="t">Box</div>',
        css=(
            "#t {\n"
            "  width: 200px;\n"
            "  padding: 20px;\n"
            "  border: 5px solid black;\n"
            "}"
        ),
        target="#t",
        prop="width",
        expect="200px",
        distractors=("250px", "240px", "210px"),
        why=(
            "By default width sets the content box, and the padding and "
            "border are added outside it, so this div occupies 250px of "
            "the page. The computed width is still 200px, because that "
            "is what width means. The 250 is what offsetWidth reports, "
            "and the gap between those two numbers is the most common "
            "surprise in CSS layout."
        ),
    ),
    _q(
        id="css-border-box-width",
        level=3,
        name="The same box, border-box",
        family="The box",
        html='<div id="t">Box</div>',
        css=(
            "#t {\n"
            "  box-sizing: border-box;\n"
            "  width: 200px;\n"
            "  padding: 20px;\n"
            "  border: 5px solid black;\n"
            "}"
        ),
        target="#t",
        prop="width",
        expect="200px",
        distractors=("150px", "250px", "160px"),
        why=(
            "With border-box the padding and border come out of the 200, "
            "leaving 150px of content, so the div occupies 200px of the "
            "page rather than 250. Computed width reports the used value "
            "of the width property, which now means the border box, so "
            "it is 200px either way. This is why border-box is the "
            "setting almost every project turns on everywhere: the "
            "number you write is the space it takes."
        ),
    ),
    _q(
        id="css-content-box-on-the-page",
        level=2,
        name="How much room that same box takes",
        family="The box",
        html='<div id="t">Box</div>',
        css=(
            "#t {\n"
            "  width: 200px;\n"
            "  padding: 20px;\n"
            "  border: 5px solid black;\n"
            "}"
        ),
        target="#t",
        prop="rect.width",
        expect="250px",
        distractors=("200px", "240px", "210px"),
        why=(
            "The same div as the question before, measured the other "
            "way. Its width is 200px and the room it takes is 250px: "
            "20px of padding and 5px of border on each side, added "
            "outside the width. Two true numbers for one box, and "
            "getting them mixed up is what makes a three-column layout "
            "of three 33.3% boxes with padding wrap onto four rows."
        ),
    ),
    _q(
        id="css-percentage-padding",
        level=4,
        name="Padding in per cent",
        family="The box",
        html=(
            '<div style="width: 400px; height: 100px;">'
            '<div id="t"></div></div>'
        ),
        target="#t",
        css="#t { padding-top: 10%; }",
        prop="padding-top",
        expect="40px",
        distractors=("10px", "10%", "0px"),
        why=(
            "A percentage padding resolves against the containing "
            "block's width - even padding-top, which you would expect to "
            "use the height. Ten per cent of 400 is 40, and the parent "
            "being 100 tall does not enter into it. This is not a quirk "
            "to work around: it is the trick behind fixed aspect ratios, "
            "where padding-top: 56.25% gives you sixteen by nine."
        ),
    ),
    _q(
        id="css-margin-collapse",
        level=5,
        name="The child's margin and the parent's height",
        family="The box",
        html='<div id="t"><p>Text</p></div>',
        css="#t { background: #eee; }\np { margin: 40px 0; height: 20px; }",
        target="#t",
        prop="height",
        expect="20px",
        distractors=("100px", "60px", "0px"),
        why=(
            "The paragraph's top and bottom margins collapse straight "
            "out through the parent, because nothing separates them from "
            "its edges - no border, no padding, no overflow other than "
            "visible. So the parent is exactly as tall as the paragraph "
            "and the 80px of margin is now outside it. One pixel of "
            "parent padding stops it dead, which is why the fix for 'my "
            "background does not cover the gap' is usually padding."
        ),
    ),
    _q(
        id="css-height-percent-auto-parent",
        level=4,
        name="A percentage height with nothing to measure",
        family="The box",
        html=(
            '<div style="height: 400px;"><div>'
            '<div id="t"></div></div></div>'
        ),
        css="#t { height: 50%; }",
        target="#t",
        prop="height",
        expect="0px",
        distractors=("200px", "50%", "auto"),
        why=(
            "There is a 400px height in this markup, and the answer is "
            "not half of it. A percentage height resolves against the "
            "*parent*, and the parent here is the middle div, whose own "
            "height is auto - sized by its contents. A percentage of an "
            "auto height cannot be worked out, so the declaration falls "
            "back to auto too, and an empty box that is auto tall is "
            "nothing tall. The height has to be definite at every step "
            "down the chain, which is why the old advice was to put "
            "height: 100% on html and body and everything in between."
        ),
    ),
)
