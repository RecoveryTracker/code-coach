"""The Flutter Layout Pack: eight Dart-only activities about how Flutter lays widgets out - flex, padding, alignment,
constraints, Stack, Wrap and overflow.

Flex Share, Padding Math, Main Axis, Cross Axis, Tight or Loose, Stack Spot, Wrap Lines, Overflow Or Fine. Each shows a
short widget tree and asks a number (a width, a left edge, a count of rows) or "fine / overflow" that REAL Flutter
computes. They are Dart-only (`make_dart`), so they are played under the Dart language of the Brain Drills switch.

How an item is made: the templates (`_flutterlayout_flex.py`, `_flutterlayout_box.py`, `_flutterlayout_place.py`) build
a small tree out of the nodes of `_flutter_model.py`, which prints it as Dart AND lays it out by Flutter's own rules
(written out by hand: constraints go down, sizes go up, the parent sets the position). tests/test_brain_packs.py then
builds every item in a real Flutter test (`oracle="flutter"`, tests/flutter_oracle.py) and compares what Flutter
measured with the answer, so a wrong rule is a failing test.

THE FLUTTER ITEM CONVENTION (a new Flutter pack may follow it with only new files): `Item.prompt` is the widget
expression, led by a `// width of b` comment saying what to measure; `Item.check` is the measurement (`w('b')`);
the host is a 400 x 300 screen whose root widget is forced to that size; `Box('a', w: 100, h: 40)` is a SizedBox of
50 x 50 unless it says otherwise, measured by its id. See tests/flutter_oracle.py for everything a check may use.

Answers are plain integers when the real value is whole (`120`), else Dart's own text (`96.5`); these templates keep to
whole numbers. The pools are smaller than the 40-70 of the other packs because each template is richer: every one is a
different layout rule with its own random sizes, flex factors and alignments.
"""

from __future__ import annotations

from . import _flutterlayout_box as box
from . import _flutterlayout_flex as flexes
from . import _flutterlayout_place as place
from ._model import Pool
from .items import Activity

GROUP = "Flutter layout"

#: What every blurb says first (the host is not shown in the code).
HOST = "Every example is the whole 400 x 300 screen; Box('a') is a 50 x 50 square (w: and h: change it)."

ACTIVITIES: tuple[Activity, ...] = (
    Activity("fl_flex", "Flex Share", f"{HOST} How big is the Expanded or Flexible child? Answers are plain numbers.",
             "What number does the comment ask for?", 10, "type", 7.0, 28.0, make_dart=Pool(flexes.FLEX_TEMPLATES),
             group=GROUP, concepts=("layout", "flex", "division", "sum"), oracle="flutter"),
    Activity("fl_padding", "Padding Math", f"{HOST} Padding, margin and Container: where does the Box end up, and how big is it?",
             "What number does the comment ask for?", 10, "type", 6.0, 24.0, make_dart=Pool(box.PADDING_TEMPLATES),
             group=GROUP, concepts=("padding", "layout", "sum", "nesting"), oracle="flutter"),
    Activity("fl_main", "Main Axis", f"{HOST} MainAxisAlignment: where along the Row or Column does the Box start?",
             "What number does the comment ask for?", 10, "type", 8.0, 30.0, make_dart=Pool(flexes.MAIN_TEMPLATES),
             group=GROUP, concepts=("layout", "alignment", "division", "index"), oracle="flutter"),
    Activity("fl_cross", "Cross Axis", f"{HOST} CrossAxisAlignment: where does the Box sit across the Row or Column, and how big is it?",
             "What number does the comment ask for?", 10, "type", 7.0, 26.0, make_dart=Pool(flexes.CROSS_TEMPLATES),
             group=GROUP, concepts=("layout", "alignment", "comparison", "nesting"), oracle="flutter"),
    Activity("fl_tight", "Tight or Loose", f"{HOST} Constraints pass down: how big does the Box really get?",
             "What number does the comment ask for?", 10, "type", 7.0, 26.0, make_dart=Pool(box.TIGHT_TEMPLATES),
             group=GROUP, concepts=("constraints", "layout", "nesting", "comparison"), oracle="flutter"),
    Activity("fl_stack", "Stack Spot", f"{HOST} Stack, Positioned and Alignment: where is the Box?",
             "What number does the comment ask for?", 10, "type", 7.0, 26.0, make_dart=Pool(place.STACK_TEMPLATES),
             group=GROUP, concepts=("stack", "layout", "position", "index"), oracle="flutter"),
    Activity("fl_wrap", "Wrap Lines", f"{HOST} A Wrap breaks into rows when the next box does not fit: count them, or find a box.",
             "What number does the comment ask for?", 8, "type", 9.0, 32.0, make_dart=Pool(place.WRAP_TEMPLATES),
             group=GROUP, concepts=("layout", "loop", "division", "count"), oracle="flutter"),
    Activity("fl_overflow", "Overflow Or Fine", f"{HOST} Does it fit? Left for fine, right for the yellow-black overflow stripes.",
             "Fine, or does a RenderFlex overflow?", 14, "pick", 5.0, 20.0, make_dart=Pool(place.OVERFLOW_TEMPLATES),
             choices=("fine", "overflow"), group=GROUP, concepts=("overflow", "layout", "condition", "comparison", "sum"),
             oracle="flutter"),
)
