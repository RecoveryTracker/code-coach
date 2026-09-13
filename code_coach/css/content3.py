"""HTML: what the parser built, and what the browser already does.

The two halves of HTML that are worth drilling and that reading the
spec does not fix.

The first is that the tree you get is not the tags you typed. HTML has
no syntax errors - every document parses, and the parser closes, moves
and invents elements to make that true. A div inside a p is not a div
inside a p. A tr with no tbody has one. A table with a stray div puts
the div outside the table. You cannot style, query or debug a tree you
have the wrong shape of in your head, and the shape is never announced:
the page just does something slightly wrong for ever.

The second is the user-agent stylesheet, which is a real stylesheet with
real declarations that beat nothing and are beaten by everything, and
which people spend years half-knowing. A button does not inherit your
font. A ul has forty pixels of padding you did not ask for. body has a
margin. Every reset stylesheet ever written is a list of these, and
knowing which is which is the difference between resetting on purpose
and resetting by superstition.

Measured the same way as the rest: tools/verify_css.py renders each one
in Chromium and the answers are copied out of what it said.
"""

from __future__ import annotations

from code_coach.css import StyleQuiz, _q


# -- What the parser built ------------------------------------

PARSER: tuple[StyleQuiz, ...] = (
    _q(
        id="html-li-autocloses",
        level=1,
        name="List items that were never closed",
        family="What the parser built",
        html='<ul id="t"><li>one<li>two<li>three</ul>',
        css="",
        target="#t",
        prop="dom.childCount",
        expect="3",
        distractors=("1", "2"),
        why=(
            "An li closes the previous li automatically, so these are "
            "three siblings rather than a nest three deep. This is one "
            "of the few places the old habit of leaving tags open is "
            "actually safe, and knowing it is safe here is what tells "
            "you it is not safe everywhere - the same omission inside a "
            "div builds a completely different tree."
        ),
    ),
    _q(
        id="html-p-cannot-hold-a-div",
        level=2,
        name="A div inside a paragraph",
        family="What the parser built",
        html='<p>one<div id="t">two</div></p>',
        css="",
        target="#t",
        prop="dom.parentTag",
        expect="body",
        distractors=("p", "div"),
        why=(
            "A p can only hold text-level content, so the opening div "
            "closes the paragraph before it. The div is the "
            "paragraph's next sibling, not its child, and the stray "
            "</p> at the end becomes an empty paragraph of its own. "
            "`p > div` in your stylesheet will never match anything, "
            "and nothing anywhere tells you why."
        ),
    ),
    _q(
        id="html-implicit-tbody",
        level=2,
        name="A row with no section around it",
        family="What the parser built",
        html='<table><tr id="t"><td>a</td></tr></table>',
        css="",
        target="#t",
        prop="dom.parentTag",
        expect="tbody",
        distractors=("table", "thead", "tr"),
        why=(
            "The parser inserts a tbody that you did not write. This is "
            "why `table > tr` matches nothing and `table tr` matches "
            "everything, which is the single most common wasted hour in "
            "styling a table. It is also why walking "
            "table.children expecting rows gets you one tbody."
        ),
    ),
    _q(
        id="html-foster-parenting",
        level=4,
        name="Something that does not belong in a table",
        family="What the parser built",
        html='<table><div id="t">stray</div><tr><td>a</td></tr></table>',
        css="",
        target="#t",
        prop="dom.parentTag",
        expect="body",
        distractors=("table", "tbody", "td"),
        why=(
            "Content that cannot live in a table is moved out and "
            "placed immediately before it - the parser calls this "
            "foster parenting. So the div ends up a sibling of the "
            "table rather than inside it, and it renders above the "
            "table rather than where you wrote it. A stray template "
            "loop that emits anything but rows hits this and looks like "
            "a CSS bug."
        ),
    ),
    _q(
        id="html-span-is-not-self-closing",
        level=5,
        name="A slash on a tag that is not void",
        family="What the parser built",
        html='<div><span/><em id="t">text</em></div>',
        css="",
        target="#t",
        prop="dom.parentTag",
        expect="span",
        distractors=("div", "body", "em"),
        why=(
            "The trailing slash does nothing in HTML. Only void "
            "elements - br, img, input and the rest of a fixed list - "
            "are self-closing, and span is not one of them, so "
            "<span/> is simply an opening tag and everything after it "
            "goes inside. The em is a child of the span. This one is "
            "brutal for people arriving from JSX or XML, where the "
            "slash is what closes it."
        ),
    ),
    _q(
        id="html-nested-anchor",
        level=3,
        name="A link inside a link",
        family="What the parser built",
        html='<a href="#">one<a id="t" href="#">two</a></a>',
        css="",
        target="#t",
        prop="dom.parentTag",
        expect="body",
        distractors=("a", "div"),
        why=(
            "An a closes any open a, because a link inside a link has "
            "no sensible meaning - which click would it be? So these "
            "are two siblings. The same rule is why wrapping a card in "
            "an anchor breaks the moment the card contains a button or "
            "a link of its own."
        ),
    ),
    _q(
        id="html-tag-case",
        level=1,
        name="Tags shouted in capitals",
        family="What the parser built",
        html='<DIV id="t">text</DIV>',
        css="",
        target="#t",
        prop="dom.tag",
        expect="div",
        distractors=("DIV", "Div"),
        why=(
            "HTML tag names are case-insensitive and tagName comes back "
            "upper case for HTML elements, which is why comparing it "
            "needs a toLowerCase and why localName is usually the one "
            "you want. Attribute names normalise too. Attribute "
            "*values* do not: class=\"Card\" and class=\"card\" are two "
            "different classes."
        ),
    ),
    _q(
        id="html-entities-are-text",
        level=2,
        name="Entities in the text",
        family="What the parser built",
        html='<span id="t">5 &lt; 6 &amp;&amp; 7 &gt; 6</span>',
        css="",
        target="#t",
        prop="dom.text",
        expect="5 < 6 && 7 > 6",
        distractors=(
            "5 &lt; 6 &amp;&amp; 7 &gt; 6",
            "5 < 6 & 7 > 6",
        ),
        why=(
            "Entities are decoded by the parser, so the text content is "
            "the characters, not the escapes. That is the whole reason "
            "escaping works: you write &lt; and the reader sees <, and "
            "nothing you wrote was ever a tag. It is also why escaping "
            "twice shows &lt; on the page - the first pass turned < "
            "into &lt;, the second turned the & into &amp;."
        ),
    ),
)


# -- What the browser already does ----------------------------

DEFAULTS: tuple[StyleQuiz, ...] = (
    _q(
        id="html-ul-padding",
        level=1,
        name="The indent nobody asked for",
        family="What the browser already does",
        html='<ul id="t"><li>one</li></ul>',
        css="",
        target="#t",
        prop="padding-left",
        expect="40px",
        distractors=("0px", "20px", "16px"),
        why=(
            "The user-agent stylesheet gives a list forty pixels of "
            "padding on the start side - padding, not margin, which is "
            "why setting margin: 0 on a nav list leaves it indented and "
            "people conclude the margin is winning. It is not there at "
            "all. This single declaration is the reason "
            "`list-style: none; padding: 0` is in every reset ever "
            "written."
        ),
    ),
    _q(
        id="html-button-font",
        level=3,
        name="A button in a page with a font",
        family="What the browser already does",
        html='<div style="font-size: 30px;"><button id="t">Go</button></div>',
        css="",
        target="#t",
        prop="font-size",
        expect="13.3333px",
        distractors=("30px", "16px", "13px"),
        why=(
            "Form controls do not inherit the page's font. The "
            "user-agent stylesheet sets one on them directly, and a "
            "declaration that matches the element beats anything "
            "inherited however large the inherited thing is. The odd "
            "fraction is the browser's own default. This is why "
            "`font: inherit` on button, input, select and textarea is "
            "in every reset - it is the only way to get the "
            "inheritance back."
        ),
    ),
    _q(
        id="html-bold-weight",
        level=2,
        name="What bold actually is",
        family="What the browser already does",
        html="<b id=\"t\">bold</b>",
        css="",
        target="#t",
        prop="font-weight",
        expect="700",
        distractors=("bold", "400", "900"),
        why=(
            "font-weight computes to a number, and bold is 700 rather "
            "than the maximum. That matters the moment you load a "
            "variable font or a family with a 600 and an 800 in it: "
            "asking for bold gets you 700 if it exists and the closest "
            "match by a set of rules if it does not, which is how text "
            "ends up looking almost right and not quite."
        ),
    ),
    _q(
        id="html-pre-whitespace",
        level=1,
        name="Spaces inside a pre",
        family="What the browser already does",
        html='<pre id="t">a    b</pre>',
        css="",
        target="#t",
        prop="white-space",
        expect="pre",
        distractors=("normal", "pre-wrap", "nowrap"),
        why=(
            "pre is not magic - it is one declaration in the "
            "user-agent stylesheet, white-space: pre, plus a monospace "
            "font. You can put that declaration on anything, and you "
            "can take it off a pre. Knowing it is a normal declaration "
            "is what tells you pre-wrap exists for the case where you "
            "want the spaces kept but the lines wrapped."
        ),
    ),
    _q(
        id="html-body-margin",
        level=2,
        name="How wide a plain div is",
        family="What the browser already does",
        html='<div id="t">text</div>',
        css="",
        target="#t",
        prop="rect.width",
        expect="784px",
        distractors=("800px", "792px", "768px"),
        why=(
            "The frame is 800px across and the div is 784, because "
            "body has eight pixels of margin on every side from the "
            "user-agent stylesheet. Nothing in the document asks for "
            "it. This is the white gutter round every page anyone has "
            "ever written before adding a reset, and it is why a "
            "full-bleed header needs margin: 0 on body rather than "
            "width: 100vw - which would be 800 and overflow by sixteen."
        ),
    ),
    _q(
        id="html-h1-in-section",
        level=4,
        name="A heading nested in a section",
        family="What the browser already does",
        html='<section><section><h1 id="t">Title</h1></section></section>',
        css="",
        target="#t",
        prop="font-size",
        expect="32px",
        distractors=("18.72px", "24px", "16px"),
        why=(
            "Browsers used to shrink an h1 as it nested inside "
            "sectioning elements, on the theory that the outline "
            "algorithm would work out the real heading level. The "
            "outline algorithm was never implemented by anyone and the "
            "shrinking has now been removed, so an h1 is an h1 "
            "wherever it sits. The lesson that survives is the one the "
            "whole saga was about: choose the heading level yourself, "
            "h1 through h6, rather than expecting nesting to mean "
            "anything."
        ),
    ),
)
