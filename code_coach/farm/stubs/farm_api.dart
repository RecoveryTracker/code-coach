// The farm's commands, for a Dart program.
//
// Your file is an ordinary Dart program with a main(). This library is
// imported on its first line - on the same line as your first, so the line
// numbers in an error are still yours - and runner.dart (which render.py
// writes) hands your main() to runFarmProgram() below.
//
// Run as:  dart run runner.dart
//
// Every command writes one line to the farm and waits for one line back (see
// code_coach/farm/protocol.py). The names are the game's, spelled the way
// Dart spells things: move(north), plant(Entities.bush), canHarvest(),
// numItems(Items.weirdSubstance). The game's named values are enums here,
// so a misspelt one is an error before your program even starts.
//
// Dart has no varargs, so two commands look a little different:
//   min(a, b) and max(a, b) take up to four values, or one list of any
//   length: min([3, 1, 2]).
//   print() is dart:core's own - one value - and quickPrint() matches it.
// And a tuple from the game is a record: getCompanion() gives
// (Entities.carrot, (3, 5)), which unpacks as
//   final (kind, (x, y)) = getCompanion()!;
//
// The block between the NAMES markers is filled in by render.py from
// code_coach/farm/data.py, so the names here can never drift from the farm.

import 'dart:async';
import 'dart:convert';
import 'dart:io';

const String _mark = '\x1eCC';

/// The farm said no: a command that is not unlocked, or used wrongly.
class FarmError implements Exception {
  FarmError(this.message);

  final String message;

  @override
  String toString() => 'FarmError: $message';
}

/// Every named value - a direction, Entities.bush, Items.hay - knows the
/// game's own name for it ("North", "Entities.Bush", "Items.Hay"), which is
/// what goes down the pipe.
abstract class _Wired {
  String get wire;
}

// NAMES-START
// render.py replaces this block with every name in code_coach/farm/data.py.
// These one-member stand-ins only keep the file whole on its own.
enum Direction implements _Wired { north('North'); const Direction(this.wire); @override final String wire; }
enum Entities implements _Wired { grass('Entities.Grass'); const Entities(this.wire); @override final String wire; }
enum Items implements _Wired { hay('Items.Hay'); const Items(this.wire); @override final String wire; }
enum Grounds implements _Wired { soil('Grounds.Soil'); const Grounds(this.wire); @override final String wire; }
enum Unlocks implements _Wired { loops('Unlocks.Loops'); const Unlocks(this.wire); @override final String wire; }
enum Hats implements _Wired { strawHat('Hats.Straw_Hat'); const Hats(this.wire); @override final String wire; }
const north = Direction.north;
const List<List<_Wired>> _groups = [Direction.values, Entities.values, Items.values, Grounds.values, Unlocks.values, Hats.values];
// NAMES-END

// ── The commands ────────────────────────────────────────────────────────

/// Harvest what is under the drone. Unripe plants are destroyed.
bool harvest() => _call('harvest') as bool;

/// True if what is under the drone is ripe.
bool canHarvest() => _call('can_harvest') as bool;

/// Plant an entity under the drone. False if it cannot.
bool plant(Entities entity) => _call('plant', [entity]) as bool;

/// Move one square: north, east, south or west. Wraps at the edges.
bool move(Direction direction) => _call('move', [direction]) as bool;

/// Turn grassland into soil, or soil back into grassland.
void till() => _call('till');

/// Swap what is under the drone with its neighbour.
bool swap(Direction direction) => _call('swap', [direction]) as bool;

/// Petals of a sunflower, size of a cactus, a pumpkin's id - a number - or
/// where the next treasure or apple is, as an (x, y) record. Null if there
/// is nothing to measure.
dynamic measure([Direction? direction]) {
  final result = _call('measure', [if (direction != null) direction]);
  if (result is List && result.length == 2) return (_int(result[0]), _int(result[1]));
  return result;
}

/// The drone's x: 0 at the West edge.
int getPosX() => _int(_call('get_pos_x'));

/// The drone's y: 0 at the South edge.
int getPosY() => _int(_call('get_pos_y'));

/// How many squares from South to North.
int getWorldSize() => _int(_call('get_world_size'));

/// What is under the drone, or null.
Entities? getEntityType() => _named<Entities>(_call('get_entity_type'));

/// Grassland or soil.
Grounds getGroundType() => _named<Grounds>(_call('get_ground_type'))!;

/// Seconds of game time since the farm began.
double getTime() => _double(_call('get_time'));

/// Ticks since this program started.
int getTickCount() => _int(_call('get_tick_count'));

/// Use water, fertilizer or weird substance here, n of them.
bool useItem(Items item, [int n = 1]) => _call('use_item', [item, n]) as bool;

/// The water level under the drone, 0 to 1.
double getWater() => _double(_call('get_water'));

/// The drone does a flip. Takes a second.
void doAFlip() => _call('do_a_flip');

/// Pets the piggy. Takes a second.
void petThePiggy() => _call('pet_the_piggy');

/// Write to the output only. Instant. (print() writes in smoke above the
/// drone, and takes a second.)
void quickPrint(Object? value) => _call('quick_print', ['$value']);

/// How many of an item you have.
num numItems(Items item) => _call('num_items', [item]) as num;

/// What planting an entity, or the next level of an unlock, costs: how many
/// of each item. Null when there is no next level to buy.
Map<Items, num>? getCost(Object thing) {
  final result = _call('get_cost', [thing]);
  if (result == null) return null;
  return {
    for (final entry in (result as Map).entries)
      _named<Items>(entry.key)!: entry.value as num,
  };
}

/// The whole farm back to grass; the drone back to (0, 0).
void clear() => _call('clear');

/// The companion the plant here wants, and where: (Entities.carrot, (3, 5)).
/// Null if it wants none.
(Entities, (int, int))? getCompanion() {
  final result = _call('get_companion');
  if (result == null) return null;
  final pair = result as List;
  final at = pair[1] as List;
  return (_named<Entities>(pair[0])!, (_int(at[0]), _int(at[1])));
}

/// Buy research, as the button would. True if it was bought.
bool unlock(Unlocks research) => _call('unlock', [research]) as bool;

/// Levels of an unlock bought; 1 or 0 for anything else.
int numUnlocked(Object thing) => _int(_call('num_unlocked', [thing]));

/// True if nothing blocks that way.
bool canMove(Direction direction) => _call('can_move', [direction]) as bool;

/// Wear a different hat.
void changeHat(Hats hat) => _call('change_hat', [hat]);

/// Slow the drone down to watch it: 1 is the speed with no upgrades.
void setExecutionSpeed(num speed) => _call('set_execution_speed', [speed]);

/// Shrink the farm (3 or more) for this run. Clears it.
void setWorldSize(int size) => _call('set_world_size', [size]);

/// A random number from 0 up to (not including) 1.
double random() => _double(_call('random'));

/// The smallest of up to four values, or of one list: min(a, b), min([a, b, c]).
num min(Object a, [Object? b, Object? c, Object? d]) => _extreme('min', a, b, c, d);

/// The largest of up to four values, or of one list: max(a, b), max([a, b, c]).
num max(Object a, [Object? b, Object? c, Object? d]) => _extreme('max', a, b, c, d);

/// The number without its sign.
num abs(num x) => _call('abs', [x]) as num;

/// Python's range, which the game's for loops are written with:
/// range(3) is [0, 1, 2], range(1, 7, 2) is [1, 3, 5], range(3, 0, -1) is
/// [3, 2, 1]. Worked out here, so it costs the drone nothing.
List<int> range(int a, [int? b, int step = 1]) {
  if (step == 0) throw ArgumentError.value(step, 'step', 'must not be zero');
  final start = b == null ? 0 : a;
  final end = b ?? a;
  final out = <int>[];
  for (var i = start; step > 0 ? i < end : i > end; i += step) {
    out.add(i);
  }
  return out;
}

num _extreme(String name, Object a, Object? b, Object? c, Object? d) {
  if (b == null && c == null && d == null && a is Iterable) {
    return _call(name, [a.toList()]) as num;
  }
  return _call(name, [a, if (b != null) b, if (c != null) c, if (d != null) d]) as num;
}

// ── The pipe ────────────────────────────────────────────────────────────

/// Every name the farm can answer with, back to its enum value.
final Map<String, _Wired> _byWire = {
  for (final group in _groups)
    for (final value in group) value.wire: value,
};

T? _named<T extends _Wired>(Object? wire) {
  if (wire == null) return null;
  final value = _byWire[wire];
  if (value is T) return value;
  throw StateError('The farm answered "$wire", which is not a name this library knows.');
}

// JSON numbers arrive as int or double depending on how they were written;
// these take either.
int _int(Object? value) => (value as num).toInt();
double _double(Object? value) => (value as num).toDouble();

/// A value as the farm reads it: an enum by its game name, a set or other
/// iterable as a list.
Object? _wire(Object? value) {
  if (value is _Wired) return value.wire;
  if (value is Map) {
    return {for (final entry in value.entries) '${_wire(entry.key)}': _wire(entry.value)};
  }
  if (value is Iterable) return [for (final item in value) _wire(item)];
  return value;
}

/// Python's json.dumps writes pure ASCII, and so does this: every character
/// past ASCII becomes a \uXXXX escape, so the line means the same whatever
/// encoding the pipe is read with - stdout's own encoding on Windows is the
/// system code page, not UTF-8.
String _ascii(String json) {
  final out = StringBuffer();
  for (final unit in json.codeUnits) {
    if (unit < 0x7f) {
      out.writeCharCode(unit);
    } else {
      out.write('\\u${unit.toRadixString(16).padLeft(4, '0')}');
    }
  }
  return out.toString();
}

/// One line to the farm, written in a single call. stdout passes each write
/// straight to the pipe, there and then, so the line is on its way before
/// the read below starts waiting for the answer.
void _send(String name, List<Object?> args) {
  final body = jsonEncode({'f': name, 'a': _wire(args)}, toEncodable: (value) => '$value');
  stdout.write('$_mark${_ascii(body)}\n');
}

/// One command: ask, wait, and hand back the answer.
Object? _call(String name, [List<Object?> args = const []]) {
  _send(name, args);
  final line = stdin.readLineSync(encoding: utf8);
  if (line == null) exit(0); // the farm has gone, and so do we, quietly
  final reply = jsonDecode(line) as Map<String, dynamic>;
  if (reply['stop'] == true) exit(0);
  if (reply.containsKey('e')) throw FarmError('${reply['e']}');
  return reply['r'];
}

// ── Running your program ────────────────────────────────────────────────

/// The first line of your file in a stack trace, which is where it went
/// wrong: a frame reads "main (file:///.../farm.dart:3:5)". The library's
/// own frames are in farm_api.dart, so they never match.
final RegExp _yourLine = RegExp(r'(?:^|[/\\\s(])farm\.dart:(\d+)', multiLine: true);

/// Tell the farm what went wrong and on which of your lines, then stop.
void _crash(Object error, StackTrace stack) {
  final found = _yourLine.firstMatch('$stack');
  final line = found == null ? 0 : int.parse(found.group(1)!);
  final message = error is FarmError ? error.message : '$error';
  try {
    _send('__error__', [message, line]);
  } catch (_) {
    // The farm has gone; there is no one left to tell.
  }
  exit(1);
}

/// Runs your main() - runner.dart calls this - inside a zone that does two
/// things: print() becomes the game's print, words in smoke above the drone,
/// and an error nobody caught, now or in something your program started, is
/// reported with the line of yours it happened on.
void runFarmProgram(Function main) {
  runZonedGuarded(
    () {
      if (main is dynamic Function()) {
        main();
      } else if (main is dynamic Function(List<String>)) {
        main(const <String>[]);
      } else {
        throw ArgumentError('main() should take no arguments, or a List<String>.');
      }
    },
    _crash,
    zoneSpecification: ZoneSpecification(
      print: (self, parent, zone, line) => _call('print', [line]),
    ),
  );
}
