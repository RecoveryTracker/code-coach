"""Dart answers for the puzzles in content4.py. Same shape as dart.py."""

from __future__ import annotations

from code_coach.puzzles.dart import DartPuzzle

DART_3: dict[str, DartPuzzle] = {
    "pz-step-counter": DartPuzzle(
        types=("List<int>",),
        returns=("int", "int"),
        one="""
int partOne(List<int> days) {
  return days.fold(0, (a, b) => a + b);
}
""",
        two="""
int partTwo(List<int> days) {
  var stars = 0;
  for (var i = 1; i < days.length; i++) {
    if (days[i] > days[i - 1]) stars++;
  }
  return stars;
}
""",
    ),
    "pz-car-park": DartPuzzle(
        types=("List<String>",),
        returns=("int", "int"),
        one="""
int partOne(List<String> log) {
  return log.where((e) => e == 'in').length;
}
""",
        two="""
int partTwo(List<String> log) {
  var now = 0;
  var best = 0;
  for (final e in log) {
    now += e == 'in' ? 1 : -1;
    if (now > best) best = now;
  }
  return best;
}
""",
    ),
    "pz-temperatures": DartPuzzle(
        types=("List<int>",),
        returns=("int", "int"),
        one="""
int partOne(List<int> readings) {
  return readings.reduce((a, b) => a > b ? a : b);
}
""",
        two="""
int partTwo(List<int> readings) {
  var best = 0;
  for (var i = 1; i < readings.length; i++) {
    final rise = readings[i] - readings[i - 1];
    if (rise > best) best = rise;
  }
  return best;
}
""",
    ),
    "pz-receipts": DartPuzzle(
        types=("List<String>",),
        returns=("int", "String"),
        one="""
int partOne(List<String> lines) {
  return lines.fold(0, (sum, line) => sum + int.parse(line.split(':')[1]));
}
""",
        two="""
String partTwo(List<String> lines) {
  var bestName = '';
  var best = -1;
  for (final line in lines) {
    final parts = line.split(':');
    final price = int.parse(parts[1]);
    if (price > best) {
      bestName = parts[0];
      best = price;
    }
  }
  return bestName;
}
""",
    ),
    "pz-digit-string": DartPuzzle(
        types=("String",),
        returns=("int", "int"),
        one="""
int partOne(String text) {
  return text.split('').fold(0, (sum, ch) => sum + int.parse(ch));
}
""",
        two="""
int partTwo(String text) {
  var total = 0;
  for (var i = 1; i < text.length; i++) {
    if (text.codeUnitAt(i) > text.codeUnitAt(i - 1)) total += int.parse(text[i]);
  }
  return total;
}
""",
    ),
    "pz-stock-room": DartPuzzle(
        types=("List<String>",),
        returns=("int", "List<String>"),
        one="""
int partOne(List<String> log) {
  var total = 0;
  for (final line in log) {
    final parts = line.split(' ');
    final count = int.parse(parts[2]);
    total += parts[0] == 'add' ? count : -count;
  }
  return total;
}
""",
        two="""
List<String> partTwo(List<String> log) {
  final stock = <String, int>{};
  for (final line in log) {
    final parts = line.split(' ');
    final count = int.parse(parts[2]);
    final change = parts[0] == 'add' ? count : -count;
    stock[parts[1]] = (stock[parts[1]] ?? 0) + change;
  }
  final names = stock.keys.where((name) => stock[name]! > 0).toList()..sort();
  return names;
}
""",
    ),
}
