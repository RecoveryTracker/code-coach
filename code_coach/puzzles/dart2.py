"""Dart answers for the puzzles in content3.py. Same shape as dart.py."""

from __future__ import annotations

from code_coach.puzzles.dart import DartPuzzle

DART_2: dict[str, DartPuzzle] = {
    "pz-traffic-light": DartPuzzle(
        types=("List<String>",),
        returns=("int", "int"),
        one="""
int partOne(List<String> log) {
  return log.where((colour) => colour == 'green').length;
}
""",
        two="""
int partTwo(List<String> log) {
  var best = 0;
  var run = 0;
  for (var i = 0; i < log.length; i++) {
    run = i > 0 && log[i - 1] == log[i] ? run + 1 : 1;
    if (run > best) best = run;
  }
  return best;
}
""",
    ),
    "pz-shopping-list": DartPuzzle(
        types=("List<String>",),
        returns=("int", "List<String>"),
        one="""
int partOne(List<String> lines) {
  var total = 0;
  for (final line in lines) {
    total += int.parse(line.split(' x')[1]);
  }
  return total;
}
""",
        two="""
List<String> partTwo(List<String> lines) {
  final totals = <String, int>{};
  for (final line in lines) {
    final parts = line.split(' x');
    totals.update(parts[0], (n) => n + int.parse(parts[1]),
        ifAbsent: () => int.parse(parts[1]));
  }
  final names = totals.keys.toList()..sort();
  return [for (final name in names) '$name x${totals[name]}'];
}
""",
    ),
    "pz-warming-up": DartPuzzle(
        types=("List<int>",),
        returns=("int", "int"),
        one="""
int partOne(List<int> readings) {
  var best = 0;
  for (var i = 1; i < readings.length; i++) {
    final rise = readings[i] - readings[i - 1];
    if (rise > best) best = rise;
  }
  return best;
}
""",
        two="""
int partTwo(List<int> readings) {
  var best = 0;
  var run = 0;
  for (var i = 0; i < readings.length; i++) {
    run = i > 0 && readings[i - 1] < readings[i] ? run + 1 : 1;
    if (run > best) best = run;
  }
  return best;
}
""",
    ),
}
