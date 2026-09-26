"""The questions.

Every snippet is a complete Dart library and the suite runs the
analyzer over each one. Where the answer is something a widget test can
observe — a count, a width, a colour, the order things were logged in —
`verify` holds the test body that checks it, and the suite runs it.

The wrong options are the guesses people actually make: the outermost
thing instead of the nearest, the whole screen rebuilding instead of
one State, a new State for every new widget.
"""

from __future__ import annotations

from code_coach.flutter import WidgetQuestion, _q


# -- The widget tree ------------------------------------------

TREE: tuple[WidgetQuestion, ...] = (
    _q(
        id="fl-tree-parent",
        level=1,
        name="Whose child is it",
        family="The widget tree",
        code="""\
import 'package:flutter/material.dart';

class Profile extends StatelessWidget {
  const Profile({super.key});

  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.all(8),
      child: Column(
        children: [
          Icon(Icons.person),
          Center(
            child: Text('Ada'),
          ),
        ],
      ),
    );
  }
}""",
        question="Which widget is the direct parent of Text('Ada')?",
        answer="Center",
        decoys=("Column", "Icon", "Padding"),
        why=(
            "A widget's parent is the one whose child: (or children:) it "
            "is written inside — the nearest enclosing constructor, not the "
            "outermost one. Text sits in Center's child:, Center sits in "
            "Column's children:, Column in Padding's child:. Icon is a "
            "sibling of Center, not an ancestor of anything. Reading a "
            "build method is mostly this: following the child: slots in."
        ),
        verify="""\
await tester.pumpWidget(const MaterialApp(home: Profile()));
Widget? parent;
tester.element(find.text('Ada')).visitAncestorElements((e) {
  parent = e.widget;
  return false;
});
expect(parent.runtimeType.toString(), answer);""",
    ),
    _q(
        id="fl-tree-count",
        level=1,
        name="Counting what a build makes",
        family="The widget tree",
        code="""\
import 'package:flutter/material.dart';

class Fruits extends StatelessWidget {
  const Fruits({super.key});

  static const fruits = ['apple', 'pear', 'plum'];

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const Text('Fruit'),
        for (final f in fruits) Text(f),
        if (fruits.length > 5) const Text('That is a lot'),
      ],
    );
  }
}""",
        question="How many Text widgets does this build create?",
        answer="4",
        decoys=("1", "3", "5"),
        why=(
            "The heading is one. The collection-for adds one Text per "
            "fruit, three more — it is a loop inside the list literal, "
            "not a single widget. The collection-if adds its Text only "
            "when the condition holds, and 3 > 5 is false, so it adds "
            "nothing at all: not an empty Text, no entry. 1 + 3 + 0 = 4."
        ),
        verify="""\
await tester.pumpWidget(const MaterialApp(home: Fruits()));
expect(find.byType(Text), findsNWidgets(int.parse(answer)));""",
    ),
    _q(
        id="fl-tree-theme-nearest",
        level=2,
        name="Theme.of finds the nearest one",
        family="The widget tree",
        code="""\
import 'package:flutter/material.dart';

class Swatch extends StatelessWidget {
  const Swatch({super.key});

  @override
  Widget build(BuildContext context) {
    final color = Theme.of(context).colorScheme.primary;
    return ColoredBox(color: color, child: const SizedBox(width: 20, height: 20));
  }
}

ThemeData tinted(Color c) =>
    ThemeData(colorScheme: ColorScheme.light(primary: c));

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      theme: tinted(Colors.blue),
      home: Theme(
        data: tinted(Colors.red),
        child: Theme(data: tinted(Colors.green), child: const Swatch()),
      ),
    );
  }
}""",
        question="What colour does Swatch paint?",
        answer="Green — the Theme closest above Swatch",
        decoys=(
            "Blue — MaterialApp's theme is the app-wide one",
            "Red — the outermost Theme you add wins",
            "The default purple — Theme.of ignores Theme widgets",
        ),
        why=(
            "Theme.of(context) walks up the tree from where context is "
            "and stops at the first Theme it meets. From Swatch the first "
            "one up is the green Theme; red and MaterialApp's blue are "
            "further up and never reached. That is the rule for every "
            "X.of(context) — MediaQuery, Navigator, DefaultTextStyle: the "
            "nearest ancestor, which is how you override something for "
            "one part of a screen by wrapping just that part."
        ),
        verify="""\
await tester.pumpWidget(const App());
final box = tester.widget<ColoredBox>(find.descendant(
    of: find.byType(Swatch), matching: find.byType(ColoredBox)));
expect(box.color.toARGB32(), Colors.green.toARGB32());
expect(answer, startsWith('Green'));""",
    ),
    _q(
        id="fl-tree-context-above",
        level=3,
        name="Your context is above what you return",
        family="The widget tree",
        code="""\
import 'package:flutter/material.dart';

class Tag extends StatelessWidget {
  const Tag({super.key});

  @override
  Widget build(BuildContext context) {
    return Theme(
      data: ThemeData(
        colorScheme: const ColorScheme.light(primary: Colors.green),
      ),
      child: ColoredBox(
        color: Theme.of(context).colorScheme.primary,
        child: const SizedBox(width: 20, height: 20),
      ),
    );
  }
}

// Shown as:
// MaterialApp(
//   theme: ThemeData(colorScheme: ColorScheme.light(primary: Colors.blue)),
//   home: Tag(),
// )""",
        question=(
            "Shown as in the comment, what colour does the ColoredBox "
            "paint?"
        ),
        answer="Blue — context is Tag's place, above the green Theme",
        decoys=(
            "Green — the Theme wraps the ColoredBox",
            "It throws — there is no Theme above context",
            "The default purple — a Theme cannot be read in the build that makes it",
        ),
        why=(
            "The context a build method gets is the widget's own place "
            "in the tree — Tag's. The Theme it returns goes below that "
            "place, so looking up from context never passes it and finds "
            "MaterialApp's blue instead. To read the green one you need a "
            "context that is below it: wrap the ColoredBox in a "
            "Builder(builder: (inner) => ...) and call Theme.of(inner), "
            "or split it into its own widget."
        ),
        verify="""\
await tester.pumpWidget(MaterialApp(
  theme: ThemeData(colorScheme: const ColorScheme.light(primary: Colors.blue)),
  home: const Tag(),
));
final box = tester.widget<ColoredBox>(find.descendant(
    of: find.byType(Tag), matching: find.byType(ColoredBox)));
expect(box.color.toARGB32(), Colors.blue.toARGB32());
expect(answer, startsWith('Blue'));""",
    ),
)


# -- Layout ---------------------------------------------------

LAYOUT: tuple[WidgetQuestion, ...] = (
    _q(
        id="fl-layout-space-between",
        level=1,
        name="Where spaceBetween puts the gaps",
        family="Layout",
        code="""\
import 'package:flutter/material.dart';

class Bar extends StatelessWidget {
  const Bar({super.key});

  @override
  Widget build(BuildContext context) {
    return const SizedBox(
      width: 300,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          SizedBox(key: Key('a'), width: 50, height: 50),
          SizedBox(key: Key('b'), width: 50, height: 50),
          SizedBox(key: Key('c'), width: 50, height: 50),
        ],
      ),
    );
  }
}""",
        question=(
            "The Row is 300 wide and the boxes take 150. Where does the "
            "other 150 go?"
        ),
        answer="75 between a and b, 75 between b and c, none at the ends",
        decoys=(
            "All 150 after c, at the end of the row",
            "25 at each end and 50 between each pair",
            "37.5 at each end and 37.5 between each pair",
        ),
        why=(
            "mainAxisAlignment only decides where a Row's leftover space "
            "goes. spaceBetween puts all of it between the children, in "
            "equal shares, so the first child touches the start and the "
            "last touches the end: two gaps of 75. The decoys are the "
            "other values — start (everything at the end), spaceAround "
            "(half a share at each end) and spaceEvenly (equal gaps "
            "everywhere, ends included)."
        ),
        verify="""\
await tester.pumpWidget(const MaterialApp(
    home: Align(alignment: Alignment.topLeft, child: Bar())));
double x(String k) => tester.getTopLeft(find.byKey(Key(k))).dx;
final left = tester.getTopLeft(find.byType(Bar)).dx;
final right = tester.getTopRight(find.byType(Bar)).dx;
final start = (x('a') - left).round();
final end = (right - x('c') - 50).round();
expect(start, end);
expect(
    '${(x('b') - x('a') - 50).round()} between a and b, '
    '${(x('c') - x('b') - 50).round()} between b and c, '
    '${start == 0 ? 'none' : start} at the ends',
    answer);""",
    ),
    _q(
        id="fl-layout-expanded",
        level=2,
        name="Expanded takes what is left",
        family="Layout",
        code="""\
import 'package:flutter/material.dart';

class Toolbar extends StatelessWidget {
  const Toolbar({super.key});

  @override
  Widget build(BuildContext context) {
    return const SizedBox(
      width: 300,
      child: Row(
        children: [
          SizedBox(width: 100, height: 40),
          Expanded(
            child: SizedBox(key: Key('middle'), height: 40),
          ),
          SizedBox(width: 50, height: 40),
        ],
      ),
    );
  }
}""",
        question="How wide is the SizedBox keyed 'middle'?",
        answer="150",
        decoys=("100", "300", "0 — it was given no width"),
        why=(
            "A Row lays out its fixed-size children first — 100 and 50 — "
            "and then shares whatever is left among the Expanded ones. "
            "300 - 100 - 50 = 150, and Expanded forces its child to be "
            "exactly that wide, so the missing width: does not matter. "
            "Expanded never takes the whole Row, only the remainder."
        ),
        verify="""\
await tester.pumpWidget(const MaterialApp(
    home: Align(alignment: Alignment.topLeft, child: Toolbar())));
expect(tester.getSize(find.byKey(const Key('middle'))).width.round().toString(),
    answer);""",
    ),
    _q(
        id="fl-layout-flex",
        level=3,
        name="Sharing by flex",
        family="Layout",
        code="""\
import 'package:flutter/material.dart';

class Shares extends StatelessWidget {
  const Shares({super.key});

  @override
  Widget build(BuildContext context) {
    return const SizedBox(
      width: 300,
      child: Row(
        children: [
          Expanded(flex: 2, child: SizedBox(key: Key('wide'), height: 40)),
          Expanded(child: SizedBox(key: Key('narrow'), height: 40)),
          SizedBox(width: 60, height: 40),
        ],
      ),
    );
  }
}""",
        question="How wide are 'wide' and 'narrow'?",
        answer="160 and 80",
        decoys=("120 and 120", "150 and 90", "200 and 100"),
        why=(
            "The fixed 60 comes off first, leaving 240. Flex values are "
            "shares of that: 2 + 1 = 3 shares, 80 each, so flex: 2 gets "
            "160 and the default flex: 1 gets 80. 200 and 100 is the "
            "split you get by forgetting the fixed child; 120 and 120 is "
            "forgetting the flex."
        ),
        verify="""\
await tester.pumpWidget(const MaterialApp(
    home: Align(alignment: Alignment.topLeft, child: Shares())));
int w(String k) => tester.getSize(find.byKey(Key(k))).width.round();
expect('${w('wide')} and ${w('narrow')}', answer);""",
    ),
    _q(
        id="fl-layout-flexible-loose",
        level=4,
        name="Flexible may leave its share unused",
        family="Layout",
        code="""\
import 'package:flutter/material.dart';

class Loose extends StatelessWidget {
  const Loose({super.key});

  @override
  Widget build(BuildContext context) {
    return const SizedBox(
      width: 300,
      child: Row(
        children: [
          Flexible(child: SizedBox(key: Key('a'), width: 40, height: 40)),
          Expanded(child: SizedBox(key: Key('b'), height: 40)),
        ],
      ),
    );
  }
}""",
        question="How wide are 'a' and 'b'?",
        answer="a is 40, b is 150",
        decoys=("a is 150, b is 150", "a is 40, b is 110", "a is 40, b is 260"),
        why=(
            "Both have flex 1, so the Row divides its 300 into two shares "
            "of 150 before either child is laid out. Expanded is Flexible "
            "with fit: FlexFit.tight — its child must fill the share, so "
            "b is 150. Plain Flexible is loose — its child may be up to "
            "150 and a asks for 40, so it is 40. The 110 a did not use is "
            "not handed on to b; it is just empty space at the end of the "
            "Row. That surprise is why Expanded exists."
        ),
        verify="""\
await tester.pumpWidget(const MaterialApp(
    home: Align(alignment: Alignment.topLeft, child: Loose())));
int w(String k) => tester.getSize(find.byKey(Key(k))).width.round();
expect('a is ${w('a')}, b is ${w('b')}', answer);""",
    ),
)


# -- State and rebuilds ---------------------------------------

STATE: tuple[WidgetQuestion, ...] = (
    _q(
        id="fl-state-no-setstate",
        level=1,
        name="Changing a field is not enough",
        family="State and rebuilds",
        code="""\
import 'package:flutter/material.dart';

class Counter extends StatefulWidget {
  const Counter({super.key});

  @override
  State<Counter> createState() => _CounterState();
}

class _CounterState extends State<Counter> {
  int count = 0;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('$count'),
        TextButton(
          onPressed: () {
            count++;
          },
          child: const Text('Add'),
        ),
      ],
    );
  }
}""",
        question="Add is tapped three times. What does the first Text show?",
        answer="0",
        decoys=("1", "3", "Nothing — it throws on the first tap"),
        why=(
            "count really is 3 afterwards — the field changed. But the "
            "screen is whatever build last returned, and nothing asked "
            "for build to run again. That is the whole job of setState: "
            "setState(() { count++; }) changes the field and marks this "
            "State as needing a rebuild in the next frame. Change a field "
            "without it and the screen goes on showing the old value."
        ),
        verify="""\
await tester.pumpWidget(const MaterialApp(home: Counter()));
for (var i = 0; i < 3; i++) {
  await tester.tap(find.text('Add'));
  await tester.pump();
}
expect(tester.widgetList<Text>(find.byType(Text)).first.data, answer);""",
    ),
    _q(
        id="fl-state-who-rebuilds",
        level=2,
        name="setState rebuilds its own State",
        family="State and rebuilds",
        code="""\
import 'package:flutter/material.dart';

var builds = <String>[];
Widget note(String who, Widget built) { builds.add(who); return built; }

class Screen extends StatelessWidget {
  const Screen({super.key});
  @override
  Widget build(BuildContext context) =>
      note('Screen', const Column(children: [Header(), Clicker()]));
}

class Header extends StatelessWidget {
  const Header({super.key});
  @override
  Widget build(BuildContext context) => note('Header', const Text('Title'));
}

class Clicker extends StatefulWidget {
  const Clicker({super.key});
  @override
  State<Clicker> createState() => _ClickerState();
}

class _ClickerState extends State<Clicker> {
  int taps = 0;
  @override
  Widget build(BuildContext context) => note('Clicker',
      TextButton(onPressed: () => setState(() => taps++), child: Text('$taps')));
}""",
        question=(
            "After the first frame, builds is emptied and the button is "
            "tapped once. What is in builds after the next frame?"
        ),
        answer="[Clicker]",
        decoys=(
            "[Clicker, Header]",
            "[Screen, Clicker]",
            "[Screen, Header, Clicker]",
        ),
        why=(
            "setState marks one thing dirty: the State it was called on. "
            "The next frame rebuilds that State's build and whatever it "
            "returns — here a TextButton and a Text — and nothing above "
            "or beside it. Screen is the parent and Header a sibling; "
            "neither was marked, so neither build runs. This is why "
            "moving state down into a small widget makes a screen cheaper "
            "to update."
        ),
        verify="""\
await tester.pumpWidget(const MaterialApp(home: Screen()));
builds = [];
await tester.tap(find.byType(TextButton));
await tester.pump();
expect('$builds', answer);""",
    ),
    _q(
        id="fl-state-const-child",
        level=3,
        name="A const child is left alone",
        family="State and rebuilds",
        code="""\
import 'package:flutter/material.dart';

final builds = <String, int>{};

class Label extends StatelessWidget {
  const Label(this.text, {super.key});
  final String text;
  @override
  Widget build(BuildContext context) {
    builds[text] = (builds[text] ?? 0) + 1;
    return Text(text);
  }
}

class Panel extends StatefulWidget {
  const Panel({super.key});
  @override
  State<Panel> createState() => _PanelState();
}

class _PanelState extends State<Panel> {
  int n = 0;
  @override
  Widget build(BuildContext context) => Column(children: [
        const Label('fixed'),
        Label('fresh'),
        TextButton(onPressed: () => setState(() => n++), child: Text('$n')),
      ]);
}""",
        question=(
            "The button is tapped once. Which Label's build runs a second "
            "time?"
        ),
        answer="Only Label('fresh')",
        decoys=(
            "Both — setState rebuilds everything below it",
            "Neither — a StatelessWidget only builds once",
            "Only Label('fixed')",
        ),
        why=(
            "_PanelState.build runs again and returns a new list. "
            "Label('fresh') is a new object each time, so Flutter updates "
            "that element with it and runs its build. const Label('fixed') "
            "is the very same object as last frame — const values are "
            "made once — and when the new widget is identical to the old "
            "one Flutter skips it and everything under it. That is the "
            "real reason the linter nags you to write const."
        ),
        verify="""\
await tester.pumpWidget(const MaterialApp(home: Panel()));
await tester.tap(find.byType(TextButton));
await tester.pump();
final again = [
  for (final e in builds.entries)
    if (e.value > 1) "Label('${e.key}')"
];
expect('Only ${again.single}', answer);""",
    ),
    _q(
        id="fl-state-keys-swap",
        level=4,
        name="State stays in its place",
        family="State and rebuilds",
        code="""\
import 'package:flutter/material.dart';

class Tile extends StatefulWidget {
  const Tile(this.label, {super.key});
  final String label;
  @override
  State<Tile> createState() => _TileState();
}

class _TileState extends State<Tile> {
  late final String born = widget.label;
  @override
  Widget build(BuildContext context) => Text('${widget.label}/$born');
}

class Pair extends StatefulWidget {
  const Pair({super.key});
  @override
  State<Pair> createState() => _PairState();
}

class _PairState extends State<Pair> {
  bool swapped = false;
  @override
  Widget build(BuildContext context) => Column(children: [
        TextButton(onPressed: () => setState(() => swapped = true),
            child: const Text('Swap')),
        ...(swapped ? const [Tile('B'), Tile('A')] : const [Tile('A'), Tile('B')]),
      ]);
}""",
        question=(
            "Each Tile shows its current label, then the label it had "
            "when its State was created. After Swap, what does the upper "
            "Tile show?"
        ),
        answer="B/A",
        decoys=("A/A", "A/B", "B/B"),
        why=(
            "Without keys, Flutter matches old and new children by "
            "position and type: first Tile to first Tile. The first State "
            "was created for 'A' and it is kept; it is just handed the new "
            "widget, Tile('B'). So widget.label is B while born is still "
            "A. The State did not move with its label — the label moved "
            "past the State. Give each Tile a key, like "
            "Tile('A', key: ValueKey('A')), and Flutter matches by key "
            "instead: the States swap places too and the top one shows B/B."
        ),
        verify="""\
await tester.pumpWidget(const MaterialApp(home: Pair()));
await tester.tap(find.text('Swap'));
await tester.pump();
final shown = tester
    .widgetList<Text>(find.descendant(
        of: find.byType(Tile), matching: find.byType(Text)))
    .map((t) => t.data)
    .toList();
expect(shown.first, answer);""",
    ),
)


# -- Lifecycle and async --------------------------------------

LIFECYCLE: tuple[WidgetQuestion, ...] = (
    _q(
        id="fl-life-order",
        level=1,
        name="Born, built, thrown away",
        family="Lifecycle and async",
        code="""\
import 'package:flutter/material.dart';

final log = <String>[];

class Blip extends StatefulWidget {
  const Blip({super.key});
  @override
  State<Blip> createState() {
    log.add('createState');
    return _BlipState();
  }
}

class _BlipState extends State<Blip> {
  @override
  void initState() {
    super.initState();
    log.add('initState');
  }
  @override
  Widget build(BuildContext context) {
    log.add('build');
    return const Text('blip');
  }
  @override
  void dispose() {
    log.add('dispose');
    super.dispose();
  }
}""",
        question=(
            "Blip is shown for one frame, then replaced by an empty "
            "SizedBox. What is in log?"
        ),
        answer="createState, initState, build, dispose",
        decoys=(
            "build, createState, initState, dispose",
            "createState, build, initState, dispose",
            "initState, createState, build, dispose",
        ),
        why=(
            "The State has to exist before anything can be called on it, "
            "so createState comes first. initState runs once, straight "
            "after, before the first build — which is why it is where "
            "you start things like controllers and subscriptions. Then "
            "build. When the widget leaves the tree for good, dispose is "
            "the last call, and it is where those things are stopped."
        ),
        verify="""\
await tester.pumpWidget(const MaterialApp(home: Blip()));
await tester.pumpWidget(const MaterialApp(home: SizedBox()));
expect(log.join(', '), answer);""",
    ),
    _q(
        id="fl-life-did-update",
        level=2,
        name="A new widget, the same State",
        family="Lifecycle and async",
        code="""\
import 'package:flutter/material.dart';

final log = <String>[];

class Echo extends StatefulWidget {
  const Echo(this.word, {super.key});
  final String word;

  @override
  State<Echo> createState() => _EchoState();
}

class _EchoState extends State<Echo> {
  @override
  void initState() {
    super.initState();
    log.add('initState ${widget.word}');
  }

  @override
  void didUpdateWidget(Echo oldWidget) {
    super.didUpdateWidget(oldWidget);
    log.add('didUpdateWidget ${oldWidget.word}->${widget.word}');
  }

  @override
  Widget build(BuildContext context) => Text(widget.word);
}""",
        question=(
            "The parent shows Echo('a'), then rebuilds and shows "
            "Echo('b') in the same place. What is in log?"
        ),
        answer="initState a, didUpdateWidget a->b",
        decoys=(
            "initState a",
            "initState a, dispose, initState b",
            "initState a, initState b",
        ),
        why=(
            "Echo('b') is a new widget object, but it is the same type in "
            "the same place with no key telling Flutter otherwise, so the "
            "existing State is kept and handed the new widget. initState "
            "does not run again — it only ever runs once per State — and "
            "didUpdateWidget runs instead, with the old widget passed in "
            "so you can compare. Anything you set up from widget.word in "
            "initState goes stale unless you redo it here."
        ),
        verify="""\
await tester.pumpWidget(const MaterialApp(home: Echo('a')));
await tester.pumpWidget(const MaterialApp(home: Echo('b')));
expect(log.join(', '), answer);""",
    ),
    _q(
        id="fl-life-future-builder",
        level=3,
        name="What FutureBuilder sees, in order",
        family="Lifecycle and async",
        code="""\
import 'package:flutter/material.dart';

final seen = <String>[];

class Loader extends StatelessWidget {
  const Loader({super.key, required this.future});
  final Future<String> future;

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<String>(
      future: future,
      builder: (context, snapshot) {
        seen.add('${snapshot.connectionState.name} ${snapshot.data}');
        return Text(snapshot.data ?? 'loading');
      },
    );
  }
}""",
        question=(
            "Loader is given a future that completes with 'hi' a second "
            "later. Once it has, what is in seen?"
        ),
        answer="waiting null, done hi",
        decoys=(
            "done hi",
            "none null, waiting null, done hi",
            "waiting null, active null, done hi",
        ),
        why=(
            "FutureBuilder starts in waiting when it is given a future, so "
            "the first build has no data — that is why the builder has to "
            "handle null and show something like a spinner. When the "
            "future completes it rebuilds once more with done and the "
            "value. none is only for a null future, and active is for "
            "streams (StreamBuilder), which can deliver more than once; a "
            "future delivers one value and is finished."
        ),
        verify="""\
await tester.pumpWidget(MaterialApp(
  home: Loader(
      future: Future.delayed(const Duration(seconds: 1), () => 'hi')),
));
await tester.pump(const Duration(seconds: 1));
await tester.pump();
expect(seen.join(', '), answer);""",
    ),
    _q(
        id="fl-life-navigator-stack",
        level=4,
        name="Counting the Navigator stack",
        family="Lifecycle and async",
        code="""\
import 'package:flutter/material.dart';

Route<void> page(String name) =>
    MaterialPageRoute<void>(builder: (_) => Text(name));

void runSequence(NavigatorState nav) {
  nav.push(page('A'));
  nav.push(page('B'));
  nav.pop();
  nav.pushReplacement(page('C'));
  nav.push(page('D'));
}

class Start extends StatelessWidget {
  const Start({super.key});

  @override
  Widget build(BuildContext context) => TextButton(
        onPressed: () => runSequence(Navigator.of(context)),
        child: const Text('home'),
      );
}""",
        question=(
            "The app starts with Start as its only route and the button "
            "is tapped. What is on the stack afterwards, bottom to top?"
        ),
        answer="home, C, D",
        decoys=("C, D", "home, A, C, D", "home, A, B, C, D"),
        why=(
            "Follow it as a list. push A: [home, A]. push B: [home, A, B]. "
            "pop takes the top off: [home, A]. pushReplacement swaps the "
            "top route for the new one, so A goes and C takes its place: "
            "[home, C]. push D: [home, C, D]. pushReplacement only "
            "replaces the top one, never the whole stack — that is "
            "pushAndRemoveUntil — so home is still at the bottom and Back "
            "from D goes to C, then home."
        ),
        verify="""\
await tester.pumpWidget(const MaterialApp(home: Start()));
await tester.tap(find.text('home'));
await tester.pumpAndSettle();
// Read the stack by popping it: the only Text on stage is the top route's.
final nav = tester.state<NavigatorState>(find.byType(Navigator));
final stack = <String>[];
while (true) {
  stack.insert(0, tester.widget<Text>(find.byType(Text)).data!);
  if (!nav.canPop()) break;
  nav.pop();
  await tester.pumpAndSettle();
}
expect(stack.join(', '), answer);""",
    ),
)
