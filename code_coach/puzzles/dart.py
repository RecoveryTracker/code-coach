"""Every puzzle in Dart - the language Flutter apps are written in.

Kept apart from the Python and JavaScript answers because Dart needs two
things they do not: the type of each parameter, so the harness can turn
the JSON test inputs into a List<String> rather than a List<dynamic>,
and the return type, so the box can open on a signature that compiles.
The suite runs every answer here through `dart run`, the same as the
other two languages.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DartPuzzle:
    #: One Dart type per parameter, in order.
    types: tuple[str, ...]
    #: Return types of part one and part two.
    returns: tuple[str, str]
    one: str
    two: str

    def answer(self, n: int) -> str:
        return (self.one if n == 1 else self.two).strip() + "\n"


DART: dict[str, DartPuzzle] = {
    "pz-night-shift": DartPuzzle(
        types=("List<String>",),
        returns=("int", "int"),
        one="""
int partOne(List<String> log) {
  var inside = 0;
  for (final line in log) {
    final parts = line.split(' ');
    final count = int.parse(parts[1]);
    inside += parts[0] == 'IN' ? count : -count;
  }
  return inside;
}
""",
        two="""
int partTwo(List<String> log) {
  var inside = 0;
  var most = 0;
  for (final line in log) {
    final parts = line.split(' ');
    final count = int.parse(parts[1]);
    inside += parts[0] == 'IN' ? count : -count;
    if (inside > most) most = inside;
  }
  return most;
}
""",
    ),
    "pz-sorting-station": DartPuzzle(
        types=("List<String>",),
        returns=("int", "String"),
        one="""
int partOne(List<String> parcels) {
  return parcels.where((p) => int.parse(p.substring(1)) > 10).length;
}
""",
        two="""
String partTwo(List<String> parcels) {
  final totals = <String, int>{};
  for (final p in parcels) {
    totals[p[0]] = (totals[p[0]] ?? 0) + int.parse(p.substring(1));
  }
  var best = '';
  for (final zone in totals.keys.toList()..sort()) {
    if (best == '' || totals[zone]! > totals[best]!) best = zone;
  }
  return best;
}
""",
    ),
    "pz-the-lift": DartPuzzle(
        types=("List<String>",),
        returns=("int", "int"),
        one="""
int partOne(List<String> moves) {
  var floor = 0;
  for (final move in moves) {
    final amount = int.parse(move.substring(1));
    floor += move[0] == 'U' ? amount : -amount;
  }
  return floor;
}
""",
        two="""
int partTwo(List<String> moves) {
  var floor = 0;
  for (var i = 0; i < moves.length; i++) {
    final amount = int.parse(moves[i].substring(1));
    floor += moves[i][0] == 'U' ? amount : -amount;
    if (floor < 0) return i + 1;
  }
  return 0;
}
""",
    ),
    "pz-class-vote": DartPuzzle(
        types=("List<String>",),
        returns=("int", "String"),
        one="""
int partOne(List<String> votes) {
  final counts = <String, int>{};
  for (final name in votes) {
    counts[name] = (counts[name] ?? 0) + 1;
  }
  var most = 0;
  for (final count in counts.values) {
    if (count > most) most = count;
  }
  return most;
}
""",
        two="""
String partTwo(List<String> votes) {
  final counts = <String, int>{};
  for (final name in votes) {
    counts[name] = (counts[name] ?? 0) + 1;
  }
  var most = 0;
  for (final count in counts.values) {
    if (count > most) most = count;
  }
  final seen = <String, int>{};
  for (final name in votes) {
    seen[name] = (seen[name] ?? 0) + 1;
    if (seen[name] == most) return name;
  }
  return '';
}
""",
    ),
    "pz-password-rules": DartPuzzle(
        types=("List<String>",),
        returns=("int", "int"),
        one="""
int partOne(List<String> passwords) {
  return passwords
      .where((p) => p.length >= 8 && RegExp(r'\\d').hasMatch(p))
      .length;
}
""",
        two="""
int partTwo(List<String> passwords) {
  return passwords
      .where((p) =>
          p.length >= 8 &&
          RegExp(r'\\d').hasMatch(p) &&
          !RegExp(r'(.)\\1\\1').hasMatch(p))
      .length;
}
""",
    ),
    "pz-garden-grid": DartPuzzle(
        types=("List<String>",),
        returns=("int", "int"),
        one="""
int partOne(List<String> grid) {
  var count = 0;
  for (final row in grid) {
    for (final cell in row.split('')) {
      if (cell == '#') count++;
    }
  }
  return count;
}
""",
        two="""
int partTwo(List<String> grid) {
  const steps = [[1, 0], [-1, 0], [0, 1], [0, -1]];
  var count = 0;
  for (var r = 0; r < grid.length; r++) {
    for (var c = 0; c < grid[r].length; c++) {
      if (grid[r][c] != '#') continue;
      final shaded = steps.any((step) {
        final rr = r + step[0];
        final cc = c + step[1];
        return rr >= 0 &&
            rr < grid.length &&
            cc >= 0 &&
            cc < grid[rr].length &&
            grid[rr][cc] == '#';
      });
      if (shaded) count++;
    }
  }
  return count;
}
""",
    ),
    "pz-brackets": DartPuzzle(
        types=("String",),
        returns=("bool", "String"),
        one="""
bool partOne(String text) {
  const pairs = {')': '(', ']': '[', '}': '{'};
  final stack = <String>[];
  for (final ch in text.split('')) {
    if ('([{'.contains(ch)) {
      stack.add(ch);
    } else if (stack.isEmpty || stack.removeLast() != pairs[ch]) {
      return false;
    }
  }
  return stack.isEmpty;
}
""",
        two="""
String partTwo(String text) {
  const pairs = {')': '(', ']': '[', '}': '{'};
  final stack = <String>[];
  for (final ch in text.split('')) {
    if ('([{'.contains(ch)) {
      stack.add(ch);
    } else if (stack.isEmpty || stack.removeLast() != pairs[ch]) {
      return ch;
    }
  }
  return '';
}
""",
    ),
    "pz-seat-map": DartPuzzle(
        types=("List<String>",),
        returns=("int", "int"),
        one="""
int partOne(List<String> rows) {
  var free = 0;
  for (final row in rows) {
    for (final seat in row.split('')) {
      if (seat == '.') free++;
    }
  }
  return free;
}
""",
        two="""
int partTwo(List<String> rows) {
  var total = 0;
  for (final row in rows) {
    for (var i = 0; i < row.length; i++) {
      final left = i > 0 ? row[i - 1] : '.';
      final right = i + 1 < row.length ? row[i + 1] : '.';
      if (row[i] == '.' && left == '.' && right == '.') total++;
    }
  }
  return total;
}
""",
    ),
    "pz-last-bus": DartPuzzle(
        types=("List<String>", "String"),
        returns=("int", "int"),
        one="""
int minutes(String clock) {
  final parts = clock.split(':');
  return int.parse(parts[0]) * 60 + int.parse(parts[1]);
}

int partOne(List<String> departures, String now) {
  final later = departures
      .map((d) => minutes(d) - minutes(now))
      .where((wait) => wait >= 0)
      .toList();
  if (later.isEmpty) return -1;
  return later.reduce((a, b) => a < b ? a : b);
}
""",
        two="""
int minutes(String clock) {
  final parts = clock.split(':');
  return int.parse(parts[0]) * 60 + int.parse(parts[1]);
}

int partTwo(List<String> departures, String now) {
  if (departures.isEmpty) return -1;
  const day = 24 * 60;
  // Dart's % never gives a negative answer for a positive day, so a bus
  // that left an hour ago comes out as 23 hours from now.
  return departures
      .map((d) => (minutes(d) - minutes(now)) % day)
      .reduce((a, b) => a < b ? a : b);
}
""",
    ),
    "pz-word-chain": DartPuzzle(
        types=("List<String>",),
        returns=("bool", "int"),
        one="""
bool partOne(List<String> words) {
  for (var i = 1; i < words.length; i++) {
    final before = words[i - 1];
    if (before[before.length - 1] != words[i][0]) return false;
  }
  return true;
}
""",
        two="""
int partTwo(List<String> words) {
  if (words.isEmpty) return 0;
  var best = 1;
  var run = 1;
  for (var i = 1; i < words.length; i++) {
    final before = words[i - 1];
    run = before[before.length - 1] == words[i][0] ? run + 1 : 1;
    if (run > best) best = run;
  }
  return best;
}
""",
    ),
    "pz-meeting-rooms": DartPuzzle(
        types=("List<String>",),
        returns=("int", "int"),
        one="""
int partOne(List<String> meetings) {
  var total = 0;
  for (final slot in meetings) {
    final parts = slot.split('-');
    total += int.parse(parts[1]) - int.parse(parts[0]);
  }
  return total;
}
""",
        two="""
int partTwo(List<String> meetings) {
  final slots =
      meetings.map((slot) => slot.split('-').map(int.parse).toList()).toList();
  var most = 0;
  for (var hour = 0; hour < 24; hour++) {
    final busy = slots.where((s) => s[0] <= hour && hour < s[1]).length;
    if (busy > most) most = busy;
  }
  return most;
}
""",
    ),
    "pz-walking-robot": DartPuzzle(
        types=("String",),
        returns=("int", "int"),
        one="""
int partOne(String commands) {
  const steps = [[0, 1], [1, 0], [0, -1], [-1, 0]];
  var x = 0, y = 0, facing = 0;
  for (final c in commands.split('')) {
    if (c == 'R') {
      facing = (facing + 1) % 4;
    } else if (c == 'L') {
      facing = (facing + 3) % 4;
    } else {
      x += steps[facing][0];
      y += steps[facing][1];
    }
  }
  return x.abs() + y.abs();
}
""",
        two="""
int partTwo(String commands) {
  const steps = [[0, 1], [1, 0], [0, -1], [-1, 0]];
  var x = 0, y = 0, facing = 0;
  // A record like (0, 0) compares by value, so a Set of them works. A
  // list [0, 0] would not: two lists are only equal if they are the
  // same list.
  final seen = <(int, int)>{(0, 0)};
  for (final c in commands.split('')) {
    if (c == 'R') {
      facing = (facing + 1) % 4;
    } else if (c == 'L') {
      facing = (facing + 3) % 4;
    } else {
      x += steps[facing][0];
      y += steps[facing][1];
      if (!seen.add((x, y))) return x.abs() + y.abs();
    }
  }
  return -1;
}
""",
    ),
}
