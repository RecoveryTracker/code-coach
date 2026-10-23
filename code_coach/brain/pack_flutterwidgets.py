"""The Flutter Widgets Pack: eight Dart-only activities about the widget TREE and what a running app does with it.

Widget Count, Text Shown, List Build, Type It, Tap Target, Navigate, Theme Says, Form Check. Each shows a small widget
expression (or a few tiny classes) with a `// question` line, and the answer is a small whole number that REAL Flutter
produces: a finder's match count, a number a Text shows, how many list items get built, the length of what a text field
holds after `enterText`, a counter after a tap, the page on top after some Navigator calls, a size that an inherited
Theme / IconTheme / DefaultTextStyle sets, the number of error texts a Form shows.

Like the layout pack (`pack_flutterlayout.py`, the model) the activities are Dart-only (`make_dart`), `oracle="flutter"`,
ids start with `fw_`, and tests/test_brain_packs.py builds every template in a real `flutter test` (tests/flutter_oracle.py)
and compares what Flutter says with the answer worked out here, by hand, from Flutter's rules. The host is the 400 x 300
test screen at devicePixelRatio 1.0 under `Directionality(ltr)`; its root widget gets exactly that size. Anything that needs
Material (text fields, forms, a Navigator) sits in a `MaterialApp(home: Material(child: ...))`, written out in the code.

The shared helpers are in `_flutterwidgets_kit.py`; the templates in `_flutterwidgets_<activity>.py`. The answers are
whole numbers because the shape tests for Flutter activities want a typed answer to be a number (or a pick).
"""

from __future__ import annotations

from . import _flutterwidgets_count as counting
from . import _flutterwidgets_form as forms
from . import _flutterwidgets_input as inputs
from . import _flutterwidgets_list as lists
from . import _flutterwidgets_nav as navs
from . import _flutterwidgets_tap as taps
from . import _flutterwidgets_theme as themes
from . import _flutterwidgets_text as texts
from ._model import Pool
from .items import Activity

GROUP = "Flutter widgets"

#: What every blurb says first (the host is not shown in the code).
HOST = ("Every example runs on a 400 x 300 test screen (Box('a') would be a 50 x 50 square), and the answer is "
        "what real Flutter reports.")

ACTIVITIES: tuple[Activity, ...] = (
    Activity("fw_count", "Widget Count", f"{HOST} How many widgets does the finder in the comment match? Remember what "
             "Container, Scaffold and Visibility build, and that find.byType skips offstage widgets.",
             "What number does the comment ask for?", 10, "type", 9.0, 34.0, make_dart=Pool(counting.TEMPLATES),
             group=GROUP, concepts=("count", "nesting", "list", "condition"), oracle="flutter"),
    Activity("fw_text", "Text Shown", f"{HOST} Which number ends up on the screen? A Text can be built from Dart code, or "
             "hide behind a widget that decides what is on stage.",
             "What number does the comment ask for?", 10, "type", 9.0, 36.0, make_dart=Pool(texts.TEMPLATES),
             group=GROUP, concepts=("text", "ternary", "condition", "string"), oracle="flutter"),
    Activity("fw_list", "List Build", f"{HOST} A scrolling list builds only what it needs plus a cache area. How many items "
             "does the finder match, or which one is first or last?",
             "What number does the comment ask for?", 10, "type", 12.0, 45.0, make_dart=Pool(lists.TEMPLATES),
             group=GROUP, concepts=("list", "lazy", "index", "count"), oracle="flutter"),
    Activity("fw_input", "Type It", f"{HOST} A test types into text fields with enterText (it replaces the whole text). What does "
             "the field hold, how often does a callback run, or which field got the text?",
             "What number does the comment ask for?", 10, "type", 10.0, 40.0, make_dart=Pool(inputs.TEMPLATES),
             group=GROUP, concepts=("string", "length", "callback", "text"), oracle="flutter"),
    Activity("fw_tap", "Tap Target", f"{HOST} The test taps, long-presses or drags at a place. Which handlers run? Every handler "
             "adds to a counter n (1, 10, 100 tell them apart); n at the end is the answer.",
             "What number does the comment ask for?", 10, "type", 12.0, 45.0, make_dart=Pool(taps.TEMPLATES),
             group=GROUP, concepts=("callback", "handler", "counter", "nesting"), oracle="flutter"),
    Activity("fw_nav", "Navigate", f"{HOST} A MaterialApp shows Text('1'); go(n) makes Navigator calls. What is on top, how many "
             "pages are left in the tree, or what do the pages say together?",
             "What number does the comment ask for?", 10, "type", 14.0, 50.0, make_dart=Pool(navs.TEMPLATES),
             group=GROUP, concepts=("stack", "order", "count", "return"), oracle="flutter"),
    Activity("fw_theme", "Theme Says", f"{HOST} A widget reads a value from the widgets above it: the nearest ancestor of its kind "
             "wins (DefaultTextStyle, IconTheme, Theme, Directionality, MediaQuery). What does it end up with?",
             "What number does the comment ask for?", 10, "type", 12.0, 45.0, make_dart=Pool(themes.TEMPLATES),
             group=GROUP, concepts=("scope", "nesting", "inheritance", "default"), oracle="flutter"),
    Activity("fw_form", "Form Check", f"{HOST} A Form of TextFormFields: the test types, validates, saves or resets. How many error texts "
             "are showing, did validate() pass, or what did onSaved collect?",
             "What number does the comment ask for?", 10, "type", 12.0, 45.0, make_dart=Pool(forms.TEMPLATES),
             group=GROUP, concepts=("null", "condition", "return", "validation"), oracle="flutter"),
)
