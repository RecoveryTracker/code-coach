"""Where Dart came from, and what is built out of it.

The companion to `langhistory`, which does the same for Python and
JavaScript. The syntax lore for Dart lives in `langlore.DART`; this is the
other half: why the language exists, how it changed shape, and what a
Flutter app actually is once you are writing one.

The same standard as the sibling file: dates and names are only here when
they are well established, drifting numbers are left out, and anything
that could not be stated plainly was dropped rather than hedged.
"""

from __future__ import annotations

from code_coach.typing.langlore2 import Passage, _p

# -- Dart: the history ---------------------------------------

DART_STORY: tuple[Passage, ...] = (
    _p("Dart was announced by Google in October 2011, at the GOTO conference "
       "in Aarhus. Lars Bak and Kasper Lund designed it, and Bak had led the "
       "team behind V8.", "Dart history"),
    _p("The first pitch was a structured language for large web apps, with "
       "its own virtual machine meant to ship inside Chrome. That plan was "
       "dropped in 2015, and dart2js carried the web.",
       "Dart history"),
    _p("Dart 1.0 shipped in November 2013. Its types were optional: they "
       "helped the tools, but a production run ignored them, so a wrong "
       "annotation could sit there quietly for years.", "Dart history"),
    _p("Dart 2 arrived in 2018 with a sound type system. A variable declared "
       "as a String really holds a String at run time, and the compiler is "
       "allowed to rely on that.", "Dart history"),
    _p("Dart 2 also made the new keyword optional. Widget trees are built "
       "out of constructor calls, and dropping new from every one of them "
       "made Flutter code read like a description.", "Dart history"),
    _p("Flutter was first shown in 2015 under the name Sky, and 1.0 shipped "
       "in December 2018. Most people who learn Dart today learn it because "
       "of Flutter.", "Flutter history"),
    _p("Flutter chose Dart because it compiles both ways: just in time while "
       "you work, for hot reload, and ahead of time when you ship, for fast "
       "startup.", "Flutter history"),
    _p("Sound null safety landed in Dart 2.12 in March 2021, alongside "
       "Flutter 2. Packages migrated one at a time, and Dart 3 made null "
       "safety the only mode there is.", "Dart history"),
    _p("Dart 3 came out in May 2023 with records, patterns and class "
       "modifiers. A sealed class lets a switch check that every subtype is "
       "handled, and the compiler says so if one is missing.",
       "Dart history"),
    _p("Hot reload injects new code into the running app and rebuilds, "
       "keeping state. Hot restart throws the state away and runs main "
       "again, which is what a change to initState needs.", "Flutter history"),
    _p("dart run uses the JIT compiler, which starts quickly and can reload "
       "code. dart compile exe builds a native executable ahead of time that "
       "runs without the Dart SDK installed.", "Dart tooling"),
    _p("dart2js turns Dart into optimised JavaScript for release builds. "
       "dart2wasm targets WebAssembly with garbage collection, and Flutter "
       "web gained stable Wasm builds in 2024.", "Dart tooling"),
    _p("Dart was standardised by Ecma International in 2014. The language "
       "has moved much faster than the standard since, and the Dart team's "
       "own specification is the one to read.", "Dart history"),
)

# -- Dart: what it is used for -------------------------------

DART_IN_USE: tuple[Passage, ...] = (
    _p("A Flutter app is one Dart codebase that builds for Android, iOS, the "
       "web, Windows, macOS and Linux. Flutter draws every pixel itself "
       "rather than borrowing the platform's own buttons.", "Flutter in use"),
    _p("A widget is an immutable description of part of the interface. It "
       "is cheap to make and cheap to throw away, which is why Flutter can "
       "rebuild them on every frame without worrying.", "Flutter in use"),
    _p("A StatelessWidget is a function of its fields. A StatefulWidget "
       "keeps its changing data in a separate State object, and that object "
       "survives when the widget itself is rebuilt.", "Flutter in use"),
    _p("setState tells Flutter that something the build method reads has "
       "changed. Change the value inside the callback, and the framework "
       "schedules a rebuild for the next frame.", "Flutter in use"),
    _p("The widget tree is the one you write. Behind it sit the element "
       "tree, which tracks what is on screen, and the render tree, which "
       "does the layout and the painting.", "Flutter internals"),
    _p("BuildContext is a widget's place in the tree. Theme.of(context) and "
       "Navigator.of(context) work by looking up from that place for the "
       "nearest ancestor that provides one.", "Flutter in use"),
    _p("Keys tell Flutter which widget is which when a list is reordered. "
       "Without one, state follows the position in the list rather than the "
       "item, and a checkbox ends up on the wrong row.",
       "Flutter gotchas"),
    _p("pub.dev is where Dart and Flutter packages live. Dependencies go in "
       "pubspec.yaml, and dart pub get or flutter pub get fetches them and "
       "writes the exact versions to pubspec.lock.", "Dart ecosystem"),
    _p("Anything slow in a Flutter app, a network call or a file read, "
       "returns a Future. await it in an async function, and FutureBuilder "
       "shows a spinner until the value arrives.", "Dart in use"),
    _p("A Stream is how a value that keeps changing reaches the screen. "
       "listen returns a subscription you must cancel in dispose, or "
       "StreamBuilder can rebuild from each new event for you.",
       "Dart in use"),
    _p("At sixty frames a second a frame has about sixteen milliseconds. "
       "Heavy work like parsing a large JSON file belongs in another "
       "isolate, and Isolate.run is the short way to put it there.",
       "Dart in use"),
    _p("Model classes usually carry a fromJson factory and a toJson method. "
       "jsonDecode gives you maps of dynamic values, and the model is where "
       "they become typed fields.", "Dart in use"),
)
