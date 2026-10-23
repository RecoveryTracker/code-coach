"""The Flutter State Pack: eight Dart-only activities about state and rebuilds - the part of Flutter that trips people most.

Tap Count, Build Count, Lifecycle Order, Key Keeps, State Survives, Notifier Says, Inherited Value, Async Setter. Each
shows a tiny widget snippet (classes included) and a `// question` line, and asks a small number, a string of digits or
"kept / reset" that REAL Flutter produces: the check taps, pumps, rebuilds the parent or removes the widget, then reads
the Text on screen (or a counter). Answers are modelled by hand in Python from Flutter's rules (setState marks dirty and
the NEXT frame builds, an identical widget instance is not rebuilt, a State follows type and key, a dependency makes an
inherited change rebuild its readers, microtasks finish before timers...), and tests/test_brain_packs.py then holds
every answer to a real `flutter test` (tests/flutter_oracle.py, `oracle="flutter"`).

The snippets are held to 220 characters and 10 lines, so they are terse on purpose: the members of a State are
one-liners, types the compiler can infer are left out, and a `() { var n = 0; return StatefulBuilder(...); }()` closure
stands in for a class when only setState matters. Where an example needs a parent that rebuilds, the check sets the
global flag `f` to true and pumps the root again - exactly what a setState higher up the tree would cause.

Every typed answer is a plain integer or a string of digits (the lifecycle hooks write their own digit into a log),
so the shape tests of the Flutter packs hold for it.
"""

from __future__ import annotations

from . import _flutterstate_async as asyncs
from . import _flutterstate_builds as builds
from . import _flutterstate_inherited as inherited
from . import _flutterstate_keys as keys
from . import _flutterstate_notifier as notifier
from . import _flutterstate_order as order
from . import _flutterstate_taps as taps
from ._model import Pool
from .items import Activity

GROUP = "Flutter state"

#: What every blurb says first (the screen is not shown in the code).
HOST = "Every example runs on a 400 x 300 test screen (Box('a') is the layout pack's 50 x 50 square; these drills do not need one)."

ACTIVITIES: tuple[Activity, ...] = (
    Activity("fs_taps", "Tap Count", f"{HOST} Tap the widget and read the Text: what does setState rebuild, and what does it leave alone?",
             "What number does the Text show?", 10, "type", 9.0, 30.0, make_dart=Pool(taps.TEMPLATES),
             group=GROUP, concepts=("state", "setstate", "rebuild", "closure"), oracle="flutter"),
    Activity("fs_builds", "Build Count", f"{HOST} The Text counts how many times its builder ran (the parent rebuilds, a tap calls setState): "
             "which widgets are built again, and which are skipped?",
             "What number does the Text show?", 10, "type", 10.0, 34.0, make_dart=Pool(builds.TEMPLATES),
             group=GROUP, concepts=("build", "rebuild", "const", "identical"), oracle="flutter"),
    Activity("fs_order", "Lifecycle Order", f"{HOST} Each hook of the State writes its own digit into the log s. After the scene in the comment, "
             "what is s? Type the digits in the order Flutter runs the hooks.",
             "What is s? Type the digits.", 10, "type", 12.0, 40.0, make_dart=Pool(order.TEMPLATES),
             group=GROUP, concepts=("lifecycle", "state", "order", "dispose"), oracle="flutter"),
    Activity("fs_keys", "Key Keeps", f"{HOST} A list of stateful children changes when f becomes true. Each child shows its own State's number: "
             "which number is in the position the comment asks about?",
             "What number does that Text show?", 10, "type", 10.0, 34.0, make_dart=Pool(keys.KEY_TEMPLATES),
             group=GROUP, concepts=("key", "state", "list", "index"), oracle="flutter"),
    Activity("fs_survive", "State Survives", f"{HOST} A FormField keeps its State (it copies initialValue once). After the rebuild in the comment, "
             "is that State kept, or is a new one made? Left for kept, right for reset.",
             "Is the State kept, or reset?", 14, "pick", 8.0, 28.0, make_dart=Pool(keys.SURVIVE_TEMPLATES),
             choices=("kept", "reset"), group=GROUP, concepts=("key", "state", "element", "tree"), oracle="flutter"),
    Activity("fs_notifier", "Notifier Says", f"{HOST} A ValueNotifier or ChangeNotifier and the builder that listens: "
             "what is on screen (or how many times did the builder run) after the taps?",
             "What number does the Text show?", 10, "type", 10.0, 34.0, make_dart=Pool(notifier.TEMPLATES),
             group=GROUP, concepts=("notifier", "listener", "observer", "value"), oracle="flutter"),
    Activity("fs_inherited", "Inherited Value", f"{HOST} An inherited widget (DefaultTextStyle, IconTheme, MediaQuery...) changes when f becomes true: "
             "what does the descendant show, and was it rebuilt?",
             "What number does the Text show?", 10, "type", 11.0, 38.0, make_dart=Pool(inherited.TEMPLATES),
             group=GROUP, concepts=("inherited", "context", "scope", "rebuild"), oracle="flutter"),
    Activity("fs_async", "Async Setter", f"{HOST} A handler awaits something and then calls setState. Time in a Flutter test only moves when you pump: "
             "what does the Text show at the moment in the comment?",
             "What number does the Text show?", 10, "type", 11.0, 38.0, make_dart=Pool(asyncs.TEMPLATES),
             group=GROUP, concepts=("async", "await", "future", "microtask"), oracle="flutter"),
)
