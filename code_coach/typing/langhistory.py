"""Where Python and JavaScript came from, and what is built out of them.

The rest of the lore is about syntax: what a language makes you write and
why. This file is about the other half of knowing a language, which is
knowing what it is actually used for. A line saying Instagram runs the
largest Django deployment anywhere is worth typing because it answers the
question a beginner is really asking, which is whether this thing is a
toy.

The standard for a line in here
-------------------------------
Every claim about a company, a date or a person was checked against a
public source before it was written down, not recalled. That rule is the
same one the rest of the project runs on: the answer has to come from
somewhere other than the thing being checked, and for prose that means a
source rather than my own memory of one.

Two consequences, both deliberate:

* Numbers that drift are pinned to the year they were true. npm's package
  count is a different number every week, so the line says it passed a
  million in 2019 and stops there. A line that goes stale is worse than a
  line that says less.
* Anything that could not be confirmed was left out rather than softened.
  There is no "reportedly" in here. Where a company is missing, it is
  usually because the story about it turned out to be folklore.

The sources are ones a reader can check for themselves: the projects' own
documentation, company engineering blogs, NumPy's published case study of
the Event Horizon Telescope image, and Dropbox's own post about Guido van
Rossum.
"""

from __future__ import annotations

from code_coach.typing.langlore2 import Passage, _p

# -- Python: the history -------------------------------------

PYTHON_STORY: tuple[Passage, ...] = (
    _p("Guido van Rossum started Python over the Christmas holiday of 1989, "
       "at a research institute in Amsterdam, as something to do with a week "
       "the office was closed.", "Python history"),
    _p("The first public release, version 0.9.0, was posted to a Usenet "
       "newsgroup in February 1991. It already had functions, exceptions, "
       "and the list and dict types.", "Python history"),
    _p("It is named after Monty Python's Flying Circus, not the snake. The "
       "documentation says so outright, and the snake arrived later because "
       "publishers needed something for the cover.", "Python history"),
    _p("The community's title for Guido was Benevolent Dictator For Life. He "
       "resigned it in July 2018, after the argument over the walrus "
       "operator wore him out.", "Python history"),
    _p("Python 2 was supported until the first day of 2020. The move to "
       "Python 3 took eleven years, which is the cautionary tale every "
       "language designer now knows by heart.", "Python history"),
    _p("A change to the language is proposed as a PEP, a Python Enhancement "
       "Proposal, in public. PEP 8 is the style guide and PEP 20 is the Zen, "
       "which is why people cite numbers at each other.", "Python process"),
    _p("CPython is the reference implementation, written in C. PyPy runs the "
       "same language with a just-in-time compiler, and MicroPython runs it "
       "on a microcontroller.", "Python implementations"),
    _p("The global interpreter lock lets one thread run Python bytecode at a "
       "time. Python 3.13 shipped an experimental build without it, after "
       "roughly thirty years of the lock being the answer.",
       "Python internals"),
    _p("f-strings arrived in Python 3.6. Before them, formatting went "
       "through percent signs or str.format, and both are still in code you "
       "will be asked to read.", "Python history"),
    _p("Type hints were added in Python 3.5 and the interpreter ignores "
       "them. They exist for the reader and for tools like mypy, which was "
       "built at Dropbox with Guido on the team.", "Python tooling"),
    _p("Django was written at a newspaper in Lawrence, Kansas, to build news "
       "sites on deadline, and is named after the guitarist Django "
       "Reinhardt.", "Python ecosystem"),
    _p("Flask started as an April Fool's joke in 2010. Armin Ronacher "
       "packaged a whole web framework into a single file to make a point, "
       "and people wanted to use it.", "Python ecosystem"),
    _p("The requests library exists because the standard library's HTTP "
       "client was unpleasant. Its slogan, HTTP for Humans, is a complaint "
       "about the thing it replaced.", "Python ecosystem"),
    _p("Typing import this into the interpreter prints the Zen of Python. It "
       "is an Easter egg that has shipped inside the language for over "
       "twenty years.", "Python trivia"),
)

# -- Python: what is built with it ---------------------------

PYTHON_IN_USE: tuple[Passage, ...] = (
    _p("Dropbox was written almost entirely in Python, both the servers and "
       "the desktop client, which is why Guido van Rossum worked there from "
       "2013 until he retired in 2019.", "Dropbox engineering"),
    _p("Guido's reason for joining Dropbox, in his own words: here was a "
       "company where everything they did was Python.", "Dropbox blog"),
    _p("Instagram runs the largest deployment of the Django web framework in "
       "the world, and has said so in public for years.",
       "Instagram engineering"),
    _p("Instagram ships its Python backend to production dozens of times a "
       "day. The interesting part is not the language, it is that nothing "
       "about the language stopped them.", "Instagram engineering"),
    _p("Instagram's stated rule for writing Python is to do the simple thing "
       "first. That is a rule about engineering, and it is most of why their "
       "code survived the growth.", "Instagram engineering"),
    _p("YouTube began life as PHP and moved its services to Python. Plenty "
       "of the internet's biggest sites are second drafts.",
       "Python in industry"),
    _p("Reddit was written in Common Lisp and rewritten in Python in 2005. "
       "The reason the founders gave was libraries: there were more of them, "
       "and they worked.", "Python in industry"),
    _p("The first direct image of a black hole, released in April 2019, was "
       "assembled by a Python package called eht-imaging.",
       "NumPy case study"),
    _p("That image was produced with NumPy, SciPy, matplotlib and Astropy. "
       "The plotting library on your laptop is the one that drew the black "
       "hole.", "NumPy case study"),
    _p("NumPy is fast because the loop is not in Python. An array operation "
       "hands the whole array to compiled C and gets it back, so the "
       "interpreter runs once instead of a million times.", "NumPy design"),
    _p("PyTorch and TensorFlow are both C++ underneath with a Python face. "
       "Python is the language people write the experiment in, not the one "
       "doing the arithmetic.", "Python in industry"),
    _p("pip installs from PyPI, the Python Package Index, which anyone at "
       "all can publish to. That is the strength and the entire "
       "supply-chain risk in one sentence.", "Python ecosystem"),
    _p("Batteries included is the old description of the standard library: "
       "json, csv, sqlite3, http, unittest and datetime are all there before "
       "you install anything.", "Python design"),
    _p("Python reached first place on the TIOBE index in 2021, the first "
       "time in that index's twenty years that neither C nor Java held the "
       "top spot.", "Python in industry"),
)

# -- JavaScript: the history ---------------------------------

JAVASCRIPT_STORY: tuple[Passage, ...] = (
    _p("Brendan Eich wrote the first JavaScript in ten days in May 1995, at "
       "Netscape, for a browser that shipped later that year.",
       "JavaScript history"),
    _p("It was called Mocha, then LiveScript, then JavaScript. The last "
       "rename was a marketing arrangement, and the language has been "
       "explaining itself ever since.", "JavaScript history"),
    _p("The language was standardised as ECMAScript in 1997 because the "
       "JavaScript name was a trademark. That is why the versions are called "
       "ES5 and ES2015 and nobody says it out loud.", "JavaScript history"),
    _p("ECMAScript 4 was designed and then abandoned. ES5 landed in 2009, "
       "ES2015 was the enormous one, and there has been a small release "
       "every year since.", "JavaScript history"),
    _p("Don't break the web is a real design constraint. A browser that "
       "rejects twenty-year-old pages loses, which is why double equals "
       "still behaves the way it did in 1995.", "JavaScript design"),
    _p("Strict mode arrived in ES5 as a way to fix old mistakes without "
       "breaking old pages: the file opts in, and the engine turns silent "
       "failures into errors.", "JavaScript history"),
    _p("V8 shipped with Chrome in 2008 and compiled JavaScript to machine "
       "code. Everything that happened next, servers included, needed that "
       "to be true first.", "JavaScript history"),
    _p("Ryan Dahl wrote Node.js in 2009 and introduced it at JSConf EU in "
       "Berlin: V8, an event loop, and the argument that blocking on I/O is "
       "the mistake.", "Node.js history"),
    _p("Dahl later gave a talk on ten things he regretted about Node.js, and "
       "then wrote a second runtime, Deno, to do them differently.",
       "Node.js history"),
    _p("npm passed one million published packages in 2019. No other language "
       "has a registry that size, and that is both the reason to use it and "
       "the reason to read what you install.", "JavaScript ecosystem"),
    _p("jQuery arrived in 2006 to paper over browsers that disagreed with "
       "each other. Most of what it added is now in the language itself, "
       "which is the nicest way for a library to die.",
       "JavaScript ecosystem"),
    _p("AJAX got its name in 2005, after Gmail and Google Maps showed a page "
       "could fetch data without reloading. The technique already existed; "
       "the name is what spread.", "JavaScript history"),
    _p("JSON is a subset of JavaScript's object literal syntax, written down "
       "by Douglas Crockford. He has said it was discovered rather than "
       "invented, which is why it is so small.", "JavaScript history"),
    _p("TypeScript came out of Microsoft in 2012, designed by Anders "
       "Hejlsberg. It compiles to JavaScript and erases every type on the "
       "way out, so none of it survives to run time.", "TypeScript history"),
    _p("WebAssembly shipped in every major browser in 2017. It does not "
       "replace "
       "JavaScript; it gives JavaScript something fast to call for the parts "
       "that need it.", "JavaScript ecosystem"),
)

# -- JavaScript: what is built with it -----------------------

JAVASCRIPT_IN_USE: tuple[Passage, ...] = (
    _p("PayPal rebuilt its account page in Node.js in 2013. A two-person "
       "Node team caught up with a five-person Java team in two months, and "
       "the page answered about a third faster.", "PayPal engineering"),
    _p("Netflix moved its user interface layer to Node.js and reported "
       "startup time falling by roughly seventy per cent.",
       "Netflix engineering"),
    _p("React was written by Jordan Walke at Facebook and was running the "
       "news feed in 2011 and Instagram's feed in 2012 before anyone outside "
       "the company had seen it.", "React history"),
    _p("React was shown to the public at JSConf US in May 2013 and the room "
       "did not like it. JSX, putting markup inside JavaScript, was the part "
       "they objected to.", "React history"),
    _p("Electron is Chromium and Node.js in one runtime, so a desktop "
       "application is a web page with a file system. Visual Studio Code, "
       "Slack, Discord and Signal are all built that way.",
       "Electron documentation"),
    _p("Visual Studio Code is written in TypeScript. The editor a great many "
       "people write C++ in is itself JavaScript with types on top.",
       "VS Code engineering"),
    _p("Every number in JavaScript is a double. That is why 0.1 plus 0.2 is "
       "not 0.3, and why BigInt had to be added later for integers past "
       "sixteen digits.", "JavaScript internals"),
    _p("One thread runs your code, and the event loop decides what runs "
       "next. Nothing is interrupted halfway, so a slow function freezes the "
       "page because there is nobody else to take over.",
       "JavaScript internals"),
    _p("Promises were standardised in ES2015 after years of libraries doing "
       "it their own way. async and await arrived in ES2017 and are those "
       "same promises with the ceremony removed.", "JavaScript history"),
    _p("typeof null returns object. It is a bug from the first ten days, and "
       "it was left in because fixing it would break pages that depend on "
       "it.", "JavaScript trivia"),
    _p("Array sort compares items as text unless you give it a function. "
       "That is why ten sorts before nine, and it has caught everyone at "
       "least once.", "JavaScript gotchas"),
    _p("The DOM is not part of JavaScript. document and window come from the "
       "browser, which is why the same language on a server has neither of "
       "them.", "JavaScript design"),
    _p("Modules took two goes. Node invented require to fill the gap, ES2015 "
       "standardised import and export, and the overlap between the two is "
       "still the fiddliest part of a build.", "JavaScript ecosystem"),
)
