"""The drills.

Every one of these is code somebody will type a dozen times and then
reach for from memory afterwards, which sets the bar: no shortcuts that
work, no habits that need unlearning later. So labels are wired to
their inputs, images have alt text, the buttons say what kind of button
they are, and the CSS is the version you would be pleased to find in a
codebase rather than the version that is shortest to type.
"""

from __future__ import annotations

from code_coach.markup import Drill, _d

# The page a piece is dropped into, for the families that practise a
# piece. Shown beside the box so it is visible rather than assumed.
PAGE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Drill</title>
    <style>
      body { font: 16px system-ui, sans-serif; margin: 24px; }
    </style>
  </head>
  <body>
{{drill}}
  </body>
</html>"""

# And one with a style block, for the drills that are CSS.
STYLED = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Drill</title>
    <style>
{{drill}}
    </style>
  </head>
  <body>
    <header class="bar">
      <h1>Title</h1>
      <nav><a href="#one">One</a> <a href="#two">Two</a></nav>
    </header>
    <main class="grid">
      <article class="card"><h2>First</h2><p>Some words.</p></article>
      <article class="card"><h2>Second</h2><p>Some words.</p></article>
      <article class="card"><h2>Third</h2><p>Some words.</p></article>
    </main>
  </body>
</html>"""


# -- The shape of a page --------------------------------------

STRUCTURE: tuple[Drill, ...] = (
    _d(
        id="drill-skeleton",
        level=1,
        name="The whole page, from nothing",
        family="The shape of a page",
        note=(
            "The five lines every page starts with. lang is what tells a "
            "screen reader which language to pronounce, and the viewport "
            "meta is the difference between a phone showing your page and "
            "a phone showing a zoomed-out desktop page."
        ),
        code=(
            "<!doctype html>\n"
            '<html lang="en">\n'
            "  <head>\n"
            '    <meta charset="utf-8">\n'
            '    <meta name="viewport" content="width=device-width, '
            'initial-scale=1">\n'
            "    <title>My page</title>\n"
            "  </head>\n"
            "  <body>\n"
            "    <h1>My page</h1>\n"
            "  </body>\n"
            "</html>"
        ),
    ),
    _d(
        id="drill-headings",
        level=2,
        name="Headings in order",
        family="The shape of a page",
        wrapper=PAGE,
        note=(
            "One h1 per page, then h2 for each section under it. Heading "
            "level is the document's outline, not a size — if an h2 looks "
            "too big, change the CSS rather than reaching for an h3."
        ),
        code=(
            "    <h1>Making bread</h1>\n"
            "    <p>Four ingredients and a lot of waiting.</p>\n"
            "\n"
            "    <h2>What you need</h2>\n"
            "    <p>Flour, water, salt, time.</p>\n"
            "\n"
            "    <h2>What to do</h2>\n"
            "    <p>Mix it, wait, fold it, wait again.</p>"
        ),
    ),
    _d(
        id="drill-list-and-links",
        level=2,
        name="A list of links",
        family="The shape of a page",
        wrapper=PAGE,
        note=(
            "Navigation is a list of links, and marking it up as one is "
            "what lets a screen reader say 'list, three items'. The link "
            "text has to make sense read on its own — 'click here' in a "
            "list of links is three items all called click here."
        ),
        code=(
            "    <nav>\n"
            "      <ul>\n"
            '        <li><a href="/bread">Bread</a></li>\n'
            '        <li><a href="/soup">Soup</a></li>\n'
            '        <li><a href="/pie">Pie</a></li>\n'
            "      </ul>\n"
            "    </nav>"
        ),
    ),
    _d(
        id="drill-figure",
        level=3,
        name="An image with something to say",
        family="The shape of a page",
        wrapper=PAGE,
        note=(
            "alt describes the picture to someone who cannot see it, so "
            "it says what the picture shows rather than that it is a "
            "picture. An image that is purely decorative takes alt=\"\" — "
            "empty on purpose, which tells a screen reader to skip it."
        ),
        code=(
            "    <figure>\n"
            '      <img src="loaf.jpg" alt="A round loaf, split down the '
            'middle" width="400" height="300">\n'
            "      <figcaption>The second attempt.</figcaption>\n"
            "    </figure>"
        ),
    ),
    _d(
        id="drill-table",
        level=4,
        name="A table with headers that mean something",
        family="The shape of a page",
        wrapper=PAGE,
        note=(
            "thead and tbody are the sections, th is a header cell, and "
            "scope says whether it heads its column or its row. Without "
            "scope a screen reader reads the numbers without saying what "
            "they are of. The tbody the parser invents for you is the "
            "one you did not write — write it."
        ),
        code=(
            "    <table>\n"
            "      <thead>\n"
            "        <tr>\n"
            '          <th scope="col">Loaf</th>\n'
            '          <th scope="col">Minutes</th>\n'
            "        </tr>\n"
            "      </thead>\n"
            "      <tbody>\n"
            "        <tr>\n"
            '          <th scope="row">White</th>\n'
            "          <td>35</td>\n"
            "        </tr>\n"
            "      </tbody>\n"
            "    </table>"
        ),
    ),
)


# -- Forms ----------------------------------------------------

FORMS: tuple[Drill, ...] = (
    _d(
        id="drill-label-input",
        level=1,
        name="A label wired to its box",
        family="Forms",
        wrapper=PAGE,
        note=(
            "for on the label matches id on the input, and that pairing "
            "is what makes clicking the word focus the box and what tells "
            "a screen reader which box it is describing. A label sitting "
            "next to an input without it is just text."
        ),
        code=(
            "    <form>\n"
            '      <label for="email">Email</label>\n'
            '      <input id="email" name="email" type="email" required>\n'
            '      <button type="submit">Sign up</button>\n'
            "    </form>"
        ),
    ),
    _d(
        id="drill-radios",
        level=3,
        name="Radios that know they are a group",
        family="Forms",
        wrapper=PAGE,
        note=(
            "The shared name is what makes them one choice rather than "
            "three switches — get it wrong and all three can be on at "
            "once. fieldset and legend are what say out loud that the "
            "question is 'Size', which is otherwise only visible."
        ),
        code=(
            "    <fieldset>\n"
            "      <legend>Size</legend>\n"
            '      <input id="s" name="size" type="radio" value="small">\n'
            '      <label for="s">Small</label>\n'
            '      <input id="m" name="size" type="radio" value="medium" '
            "checked>\n"
            '      <label for="m">Medium</label>\n'
            "    </fieldset>"
        ),
    ),
    _d(
        id="drill-select",
        level=2,
        name="A menu of choices",
        family="Forms",
        wrapper=PAGE,
        note=(
            "value is what gets sent, the text between the tags is what "
            "gets seen, and they are allowed to differ. selected picks "
            "the one it opens on."
        ),
        code=(
            '    <label for="flour">Flour</label>\n'
            '    <select id="flour" name="flour">\n'
            '      <option value="white">White</option>\n'
            '      <option value="whole" selected>Wholemeal</option>\n'
            '      <option value="rye">Rye</option>\n'
            "    </select>"
        ),
    ),
    _d(
        id="drill-textarea",
        level=2,
        name="A box for more than a line",
        family="Forms",
        wrapper=PAGE,
        note=(
            "A textarea has no value attribute — what it starts with is "
            "the text between its tags, including any whitespace, which "
            "is why its closing tag goes hard against the content. "
            "type=\"submit\" is spelled out because a button inside a "
            "form submits whether you meant it to or not."
        ),
        code=(
            "    <form>\n"
            '      <label for="notes">Notes</label>\n'
            '      <textarea id="notes" name="notes" rows="4"></textarea>\n'
            '      <button type="submit">Save</button>\n'
            "    </form>"
        ),
    ),
    _d(
        id="drill-checkbox-hint",
        level=4,
        name="A checkbox with help text attached",
        family="Forms",
        wrapper=PAGE,
        note=(
            "aria-describedby points at the id of the hint, so the hint "
            "is read out along with the field instead of being noticed "
            "only by people who can see it sitting underneath."
        ),
        code=(
            "    <input id=\"news\" name=\"news\" type=\"checkbox\"\n"
            '           aria-describedby="news-hint">\n'
            '    <label for="news">Email me new recipes</label>\n'
            '    <p id="news-hint">About once a month. Unsubscribe any '
            "time.</p>"
        ),
    ),
)


# -- Laying it out --------------------------------------------

LAYOUT: tuple[Drill, ...] = (
    _d(
        id="drill-flex-row",
        level=1,
        name="A row with space between",
        family="Laying it out",
        wrapper=STYLED,
        note=(
            "The three declarations that do most of the headers on the "
            "web. gap is the modern answer to spacing — it puts space "
            "between the items and not outside them, which is what "
            "margins on children never quite managed."
        ),
        code=(
            "      .bar {\n"
            "        display: flex;\n"
            "        justify-content: space-between;\n"
            "        align-items: center;\n"
            "        gap: 16px;\n"
            "      }"
        ),
    ),
    _d(
        id="drill-grid-columns",
        level=2,
        name="Three columns that share the room",
        family="Laying it out",
        wrapper=STYLED,
        note=(
            "repeat(3, 1fr) is three equal columns. The fr unit is a "
            "share of what is left over, which is why it does what "
            "percentages only pretend to do once there is a gap in the "
            "way."
        ),
        code=(
            "      .grid {\n"
            "        display: grid;\n"
            "        grid-template-columns: repeat(3, 1fr);\n"
            "        gap: 16px;\n"
            "      }"
        ),
    ),
    _d(
        id="drill-grid-responsive",
        level=4,
        name="Columns that fit themselves",
        family="Laying it out",
        wrapper=STYLED,
        note=(
            "One line that lays out a gallery at every width without a "
            "media query: as many columns as fit at 200px or wider, each "
            "sharing the leftovers. auto-fit collapses the empty tracks; "
            "auto-fill would keep them."
        ),
        code=(
            "      .grid {\n"
            "        display: grid;\n"
            "        grid-template-columns: repeat(auto-fit, "
            "minmax(200px, 1fr));\n"
            "        gap: 16px;\n"
            "      }"
        ),
    ),
    _d(
        id="drill-sticky",
        level=3,
        name="A header that stays",
        family="Laying it out",
        wrapper=STYLED,
        note=(
            "sticky needs an offset to stick to — position: sticky with "
            "no top does nothing at all, silently, which is the usual "
            "reason it 'does not work'."
        ),
        code=(
            "      .bar {\n"
            "        position: sticky;\n"
            "        top: 0;\n"
            "        background: white;\n"
            "        padding: 8px 0;\n"
            "      }"
        ),
    ),
    _d(
        id="drill-media-query",
        level=4,
        name="One column on a narrow screen",
        family="Laying it out",
        wrapper=STYLED,
        note=(
            "Written the way round that costs least: the narrow layout is "
            "the plain rule, and the media query adds columns when there "
            "is room. Starting wide and undoing it for phones means every "
            "phone downloads a layout it will not use."
        ),
        code=(
            "      .grid {\n"
            "        display: grid;\n"
            "        gap: 16px;\n"
            "      }\n"
            "\n"
            "      @media (min-width: 600px) {\n"
            "        .grid {\n"
            "          grid-template-columns: repeat(3, 1fr);\n"
            "        }\n"
            "      }"
        ),
    ),
)


# -- Styling it -----------------------------------------------

STYLING: tuple[Drill, ...] = (
    _d(
        id="drill-reset",
        level=1,
        name="The three lines every stylesheet starts with",
        family="Styling it",
        wrapper=STYLED,
        note=(
            "border-box makes width mean the width, padding and border "
            "included. The margin on body is the browser's, not yours, "
            "and the unitless line-height is the one that inherits as a "
            "factor rather than as a fixed number of pixels."
        ),
        code=(
            "      *, *::before, *::after {\n"
            "        box-sizing: border-box;\n"
            "      }\n"
            "\n"
            "      body {\n"
            "        margin: 0;\n"
            "        line-height: 1.5;\n"
            "      }"
        ),
    ),
    _d(
        id="drill-custom-properties",
        level=2,
        name="Colours with names",
        family="Styling it",
        wrapper=STYLED,
        note=(
            "Custom properties are declared on :root and inherit "
            "everywhere, so the colour lives in one place. The second "
            "argument to var() is the fallback, used if the property was "
            "never set."
        ),
        code=(
            "      :root {\n"
            "        --ink: #222;\n"
            "        --paper: #fdfdfb;\n"
            "        --accent: #2f6f4f;\n"
            "      }\n"
            "\n"
            "      body {\n"
            "        color: var(--ink);\n"
            "        background: var(--paper, white);\n"
            "      }"
        ),
    ),
    _d(
        id="drill-card",
        level=2,
        name="A card",
        family="Styling it",
        wrapper=STYLED,
        note=(
            "The shape you will write more than any other. Padding "
            "inside, a quiet border, a radius, and a shadow soft enough "
            "that you notice the card rather than the shadow."
        ),
        code=(
            "      .card {\n"
            "        padding: 16px;\n"
            "        border: 1px solid #e3e3e0;\n"
            "        border-radius: 8px;\n"
            "        box-shadow: 0 1px 3px rgb(0 0 0 / 0.08);\n"
            "      }"
        ),
    ),
    _d(
        id="drill-focus-visible",
        level=3,
        name="Hover, and the one people delete",
        family="Styling it",
        wrapper=STYLED,
        note=(
            "Hover is for mice; focus is for keyboards, and the outline "
            "is how somebody tabbing through knows where they are. "
            "`outline: none` with nothing put back is the single most "
            "common accessibility mistake on the web — focus-visible "
            "shows it to keyboard users and keeps it off mouse clicks."
        ),
        code=(
            "      a:hover {\n"
            "        color: var(--accent);\n"
            "      }\n"
            "\n"
            "      a:focus-visible {\n"
            "        outline: 2px solid var(--accent);\n"
            "        outline-offset: 2px;\n"
            "      }"
        ),
    ),
    _d(
        id="drill-centered-column",
        level=3,
        name="A column down the middle",
        family="Styling it",
        wrapper=STYLED,
        note=(
            "How a page of text gets centred and kept readable. The ch "
            "unit is roughly the width of a character, so a max-width in "
            "ch sets the line length directly — around 60 to 70 is the "
            "range that is comfortable to read."
        ),
        code=(
            "      main {\n"
            "        max-width: 65ch;\n"
            "        margin-inline: auto;\n"
            "        padding-inline: 16px;\n"
            "      }"
        ),
    ),
)
