// The farm's commands, for a Dart program.
//
// Your program is one or more files - main.dart, utils.dart ... - and the
// one that runs is an ordinary Dart program with a main(). Your files
// import each other the way Dart files do: import 'utils.dart'; (with as,
// show and hide if you like). This library is imported on the first line of
// every one of them - on the same line as your first, so the line numbers
// in an error are still yours - and runner.dart (which render.py writes)
// hands the main() of the file you run to runFarmProgram() below.
//
// Run as:  dart run runner.dart
//
// Every command writes one line to the farm and waits for one line back (see
// code_coach/farm/protocol.py). The names are the game's, spelled the way
// Dart spells things: move(north), plant(Entities.bush), canHarvest(),
// numItems(Items.weirdSubstance). The game's named values are enums here,
// so a misspelt one is an error before your program even starts.
//
// Dart has no varargs, so three commands look a little different:
//   min(a, b) and max(a, b) take up to four values, or one list of any
//   length: min([3, 1, 2]).
//   print() is dart:core's own - one value - and quickPrint() matches it.
//   spawnDrone() takes the function's arguments as one list:
//   spawnDrone(plantColumn, [3, Entities.carrot]).
// And a tuple from the game is a record: getCompanion() gives
// (Entities.carrot, (3, 5)), which unpacks as
//   final (kind, (x, y)) = getCompanion()!;
//
// More drones: spawnDrone(f) starts a new run of this same program in drone
// mode (FARM_DRONE holds the job). That run does not call your main(): it
// calls f, and sends back what f returned. runner.dart lists the top-level
// functions of all your files by name, which is how the new run finds f.
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

/// Start another drone here, running function with args - spawnDrone(work),
/// or spawnDrone(plantColumn, [3, Entities.carrot]) for plantColumn(3,
/// Entities.carrot). Its handle, or null if every drone is already out.
///
/// The new drone is a new run of your program that runs only that function,
/// so it is sent by name - which is why it has to be one declared at the top
/// level, where the new run will find it again. Its globals start from their
/// declarations: nothing of yours is copied across but the arguments.
int? spawnDrone(Function function, [List<Object?> args = const []]) {
  final name = _droneName(function);
  final handle = _call('spawn_drone', [name, args, const <String, Object?>{}]);
  return handle == null ? null : _int(handle);
}

/// How many drones are on the farm now.
int numDrones() => _int(_call('num_drones'));

/// How many drones you may have at once.
int maxDrones() => _int(_call('max_drones'));

/// True once that drone's function has returned.
bool hasFinished(int drone) => _call('has_finished', [drone]) as bool;

/// Wait for a drone to finish, and what its function returned: a number, a
/// string, an enum value, or a list or map of those. (A record comes back
/// as a list.)
dynamic waitFor(int drone) => _unwire(_call('wait_for', [drone]));

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
/// iterable as a list, and a record - (3, 5) - as a list too, the way the
/// game's tuples travel.
Object? _wire(Object? value) => switch (value) {
      _Wired named => named.wire,
      Map map => {for (final entry in map.entries) '${_wire(entry.key)}': _wire(entry.value)},
      Iterable items => [for (final item in items) _wire(item)],
      (var a,) => [_wire(a)],
      (var a, var b) => [_wire(a), _wire(b)],
      (var a, var b, var c) => [_wire(a), _wire(b), _wire(c)],
      (var a, var b, var c, var d) => [_wire(a), _wire(b), _wire(c), _wire(d)],
      _ => value,
    };

/// A value from the pipe as your program's own: a game name back to its
/// enum value, and a list typed by what is in it, so that it fits a
/// parameter declared that way.
Object? _unwire(Object? value) {
  if (value is String) return _byWire[value] ?? value;
  if (value is List) return _narrow([for (final item in value) _unwire(item)]);
  if (value is Map) {
    return {for (final entry in value.entries) _unwire(entry.key): _unwire(entry.value)};
  }
  return value;
}

/// A list as a List<int>, List<String>, List<Entities> ... when every item
/// is one: JSON's lists are List<dynamic>, which a parameter declared
/// List<int> would turn away. Mixed, or empty, it stays as it is.
List<Object?> _narrow(List<Object?> items) {
  if (items.isEmpty) return items;
  if (items.every((item) => item is int)) return List<int>.from(items);
  if (items.every((item) => item is double)) return List<double>.from(items);
  if (items.every((item) => item is num)) return List<num>.from(items);
  if (items.every((item) => item is String)) return List<String>.from(items);
  if (items.every((item) => item is bool)) return List<bool>.from(items);
  for (final group in _groups) {
    if (items.every(group.contains)) {
      // A copy of the enum's own list, emptied: a List<Entities>, say.
      final typed = group.toList()..clear();
      for (final item in items) {
        typed.add(item as _Wired);
      }
      return typed;
    }
  }
  return items;
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

/// A frame of a stack trace in a file in the folder your program runs in -
/// "main (file:///C:/.../main.dart:3:5)", "tend (file:///C:/.../utils.dart:2:3)"
/// - with the file's name and the line. Dart's own frames are dart: URIs,
/// so they never match.
final RegExp _frame = RegExp(
    '${RegExp.escape(Platform.script.resolve('.').toString())}([a-z_][a-z0-9_]*)\\.dart:(\\d+)');

/// The farm's own files, beside yours.
const Set<String> _farmFiles = {'farm_api', 'runner'};

/// Tell the farm what went wrong, in which file of yours and on which line,
/// then stop. The place is the deepest frame of the stack that is in one of
/// your files - the first one in it.
void _crash(Object error, StackTrace stack) {
  var line = 0;
  var file = '';
  for (final found in _frame.allMatches('$stack')) {
    if (_farmFiles.contains(found.group(1))) continue;
    file = found.group(1)!;
    line = int.parse(found.group(2)!);
    break;
  }
  final message = error is FarmError ? error.message : '$error';
  try {
    _send('__error__', [message, line, file]);
  } catch (_) {
    // The farm has gone; there is no one left to tell.
  }
  exit(1);
}

// ── More drones ─────────────────────────────────────────────────────────

/// The top-level functions of all your files, by name - runner.dart lists
/// them: the file you run first, so its name wins, and a name taken twice
/// as utils.harvestColumn - which are the functions a drone can be sent to
/// run.
Map<String, Function> _drones = const {};

/// Which of your functions this is: the name runner.dart listed this very
/// function under. Dart tells a function's name only in its toString -
/// "Closure: () => void from Function 'harvestColumn': static." - and a
/// static method, or a function from another library, reads just the same;
/// so that is only read to say why a function is not one of yours.
String _droneName(Function function) {
  for (final listed in _drones.entries) {
    if (listed.value == function) return listed.key;
  }
  final said = RegExp(r"from Function '([^']*)': static\.$").firstMatch('$function');
  final name = said?.group(1) ?? '';
  if (name.startsWith('_')) {
    throw FarmError('spawnDrone needs a function whose name does not start with _: in Dart '
        'that keeps it private to your file, where a new drone cannot reach it.');
  }
  throw FarmError('spawnDrone needs a function declared at the top level of your program, '
      'like void harvestColumn() { ... }');
}

/// Drone mode: FARM_DRONE names one of your functions and the arguments to
/// give it. Your main() does not run - only that function - and what it
/// returns goes back for waitFor().
void _runDrone(String job) {
  final order = jsonDecode(job) as Map<String, dynamic>;
  final name = '${order['fn']}';
  final function = _drones[name];
  if (function == null) {
    throw FarmError('This drone was to run $name(), but your program declares no function '
        'of that name at its top level.');
  }
  final args = [for (final arg in order['args'] as List? ?? const []) _unwire(arg)];
  final value = Function.apply(function, args);
  // An async function hands back a Future: what it completes with is the answer.
  if (value is Future) {
    value.then(_returned);
  } else {
    _returned(value);
  }
}

/// The drone's function has returned: say what with, and stop. The farm
/// sends no answer to this one.
void _returned(Object? value) {
  _send('__return__', [value]);
  exit(0);
}

/// Runs your program - runner.dart calls this, with your main() and your
/// top-level functions - inside a zone that does two things: print()
/// becomes the game's print, words in smoke above the drone, and an error
/// nobody caught, now or in something your program started, is reported
/// with the line of yours it happened on. A drone runs in the same zone,
/// calling its one function instead of main().
void runFarmProgram(Function main, {Map<String, Function> drones = const {}}) {
  _drones = drones;
  final job = Platform.environment['FARM_DRONE'] ?? '';
  runZonedGuarded(
    () {
      if (job.isNotEmpty) {
        _runDrone(job);
      } else if (main is dynamic Function()) {
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
