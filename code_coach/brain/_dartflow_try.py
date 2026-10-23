"""Dart flow pack, part 1: Try Order - which letters print, in order, through try / on / catch / finally.

Every template is the BODY of main (no `main(`) unless it declares a class; the printed lines are glued together
(oracle `lines`). The model is the exception family tree of `_dartflow_model` (`catches`, `first_clause`) plus these
rules: a thrown value goes to the FIRST `on` clause whose type it is; `catch (e)` takes anything; the exception then
flows OUT to the enclosing try if no clause matches; `finally` always runs, whatever happened (a `return`, `break`,
`continue` or a throw in the try or catch included); a throw inside a catch is not caught by its own siblings.
"""

from __future__ import annotations

from ._dartflow_model import L, catches, first_clause, pick_throw
from ._model import Maker

CLAUSES = ["FormatException", "Exception", "StateError", "ArgumentError", "RangeError", "String", "Error"]
#: Real operations that throw (code, class); used as statements (`$r;`).
REAL = [
    ("int.parse('$m')", "FormatException"),
    ("[$a][$n]", "RangeError"),
    ("<int>[].first", "StateError"),
    ("'$m'.substring($n)", "RangeError"),
    ("[$a, $b].single", "StateError"),
    ("double.parse('$m')", "FormatException"),
]
#: (general, specific, a thrown value that is the general one but NOT the specific one, its class)
PAIRS = [
    ("Exception", "FormatException", "Exception('$m')", "Exception"),
    ("ArgumentError", "RangeError", "ArgumentError('$m')", "ArgumentError"),
    ("Error", "StateError", "UnsupportedError('$m')", "UnsupportedError"),
    ("Error", "RangeError", "StateError('$m')", "StateError"),
]


def pre_t(p, rng):
    pick_throw(p, rng)


def pre_c1(p, rng):
    pick_throw(p, rng)
    p["c1"] = rng.choice(CLAUSES)


def pre_c12(p, rng):
    pick_throw(p, rng)
    p["c1"], p["c2"] = rng.sample(CLAUSES, 2)


def pre_c12_fit(p, rng):
    """Two clauses of which at least one always fits (the thrown class and a random other, in random order)."""
    pick_throw(p, rng)
    other = rng.choice([c for c in CLAUSES if c != p["tc"]])
    p["c1"], p["c2"] = rng.sample([p["tc"], other], 2)


def pre_order(p, rng):
    """A general and a specific clause in random order; the thrown value is the specific class or only the general."""
    gen, spec, other, other_cls = rng.choice(PAIRS)
    if rng.random() < 0.5:
        p["t"], p["tc"] = f"throw {spec}('{p['w']}')", spec
    else:
        p["t"], p["tc"] = "throw " + other.replace("$m", p["w"]), other_cls
    p["g"], p["sp"] = (gen, spec) if rng.random() < 0.5 else (spec, gen)


def pre_k(p, rng):
    p["k"] = rng.randint(2, 3)


def pre_k24(p, rng):
    p["k"] = rng.randint(2, 4)


def pre_real(p, rng):
    pick_throw(p, rng, "r", REAL)
    p["c1"] = rng.choice(CLAUSES)


def pre_real_maybe(p, rng):
    """A real operation that throws, or (30%) a harmless parse; rc is the class thrown ("" when nothing is)."""
    pre_real(p, rng)
    if rng.random() < 0.3:
        p["r"], p["rc"] = f"int.parse('{p['n']}')", ""


def hit(p) -> bool:
    return catches(p["tc"], p["c1"])


def rhit(p) -> bool:
    return bool(p["rc"]) and catches(p["rc"], p["c1"])


S_THEN = "The statements after the failing one are skipped; the catch runs; execution goes on after the whole try."
CLAUSE_RULE = "The clauses are tried from the top: the first one that fits takes it; the plain catch is the last resort."

TRY: list[Maker] = [
    L("try {\n  print('$s1');\n} catch (e) {\n  print('$s2');\n} finally {\n  print('$s3');\n}",
      [1, 3], "Nothing is thrown, so the catch is skipped; the finally always runs."),
    L("try {\n  print('$s1');\n  $t;\n  print('$s2');\n} catch (e) {\n  print('$s3');\n}\nprint('$s4');",
      [1, 3, 4], S_THEN, pre_t),
    L("try {\n  print('$s1');\n  $t;\n} on $c1 {\n  print('$s2');\n} catch (e) {\n  print('$s3');\n} finally {\n  print('$s4');\n}",
      lambda p: [1, 2, 4] if hit(p) else [1, 3, 4],
      lambda p: "The exception goes to the first clause whose type it is: "
      + ("the on clause." if hit(p) else "not the on clause, so the catch.") + " The finally runs last.",
      pre_c1),
    L("try {\n  $t;\n} on $c1 {\n  print('$s1');\n} on $c2 {\n  print('$s2');\n} catch (e) {\n  print('$s3');\n}",
      lambda p: [1] if catches(p["tc"], p["c1"]) else ([2] if catches(p["tc"], p["c2"]) else [3]),
      CLAUSE_RULE, pre_c12),
    L("try {\n  $t;\n} on $c1 {\n  print('$s1');\n} on $c2 {\n  print('$s2');\n}\nprint('$s3');",
      lambda p: [1, 3] if catches(p["tc"], p["c1"]) else [2, 3],
      "Only one clause runs, then the code after the try. (One of the two always fits here.)", pre_c12_fit),
    L("try {\n  $t;\n} on $g {\n  print('$s1');\n} on $sp {\n  print('$s2');\n}",
      lambda p: [1] if first_clause(p["tc"], [p["g"], p["sp"]]) == 0 else [2],
      "A general type before a specific one catches everything the specific one would: the first match wins.", pre_order),
    L("try {\n  try {\n    print('$s1');\n    $t;\n  } on $c1 {\n    print('$s2');\n  }\n} catch (e) {\n  print('$s3');\n}\nprint('$s4');",
      lambda p: [1, 2, 4] if hit(p) else [1, 3, 4],
      lambda p: "The inner clause " + ("fits, so the outer catch never sees it." if hit(p)
                                      else "does not fit, so the exception goes out to the outer catch."),
      pre_c1),
    L("try {\n  try {\n    $t;\n  } finally {\n    print('$s1');\n  }\n} catch (e) {\n  print('$s2');\n}",
      [1, 2], "finally runs while the exception is on its way out; the outer catch comes after it.", pre_t),
    L("try {\n  try {\n    try {\n      $t;\n    } finally {\n      print('$s1');\n    }\n  } finally {\n    print('$s2');\n  }\n} catch (e) {\n  print('$s3');\n}",
      [1, 2, 3], "Each finally runs as the exception passes through, innermost first; the catch is last.", pre_t),
    L("try {\n  try {\n    $t;\n  } catch (e) {\n    print('$s1');\n    rethrow;\n  }\n} catch (e) {\n  print('$s2');\n}\nprint('$s3');",
      [1, 2, 3], "rethrow passes the same exception on to the outer catch.", pre_t),
    L("try {\n  try {\n    $t;\n  } catch (e) {\n    print('$s1');\n    throw 'again';\n  } finally {\n    print('$s2');\n  }\n} catch (e) {\n  print('$s3');\n}",
      [1, 2, 3], "The new throw leaves the catch, but the finally still runs before the outer catch.", pre_t),
    L("try {\n  try {\n    print('$s1');\n  } finally {\n    print('$s2');\n    throw 'x';\n  }\n} catch (e) {\n  print('$s3');\n}",
      [1, 2, 3], "A throw inside finally is a new exception: the outer catch gets it, even though the try was fine."),
    L("try {\n  try {\n    $t;\n  } on $c1 {\n    print('$s1');\n    throw 'x';\n  } catch (e) {\n    print('$s2');\n  }\n} catch (e) {\n  print('$s3');\n}",
      lambda p: [1, 3] if hit(p) else [2],
      lambda p: "A throw inside a catch is NOT caught by its sibling clauses - it goes to the outer try." if hit(p)
      else "The on clause does not fit, so the sibling catch takes it, and nothing is thrown again.", pre_c1),
    L("int f() {\n  try {\n    return 1;\n  } finally {\n    print('$s1');\n  }\n}\nprint(f());",
      [1, "1"], "The finally runs before the function really returns, so its print comes first."),
    L("int f() {\n  try {\n    return $a;\n  } finally {\n    return $b;\n  }\n}\nprint(f());",
      lambda p: [str(p["b"])], "A return in finally wins over the return in the try."),
    L("int f() {\n  var x = $a;\n  try {\n    return x;\n  } finally {\n    x = $b;\n  }\n}\nprint(f());",
      lambda p: [str(p["a"])], "The value is taken at the return; changing x in finally later does not change it."),
    L("String f(bool bad) {\n  try {\n    if (bad) throw 'x';\n    return '$s1';\n  } catch (e) {\n    return '$s2';\n  } finally {\n    print('$s3');\n  }\n}\nprint(f(true));",
      [3, 2], "The catch returns, but the finally runs first, then the value is printed."),
    L("String f(bool bad) {\n  try {\n    if (bad) throw 'x';\n    return '$s1';\n  } catch (e) {\n    return '$s2';\n  } finally {\n    print('$s3');\n  }\n}\nprint(f(false));",
      [3, 1], "No throw, so the try returns its value; the finally still runs first."),
    L("for (var i = 1; i <= 3; i++) {\n  try {\n    if (i == $k) continue;\n    print(i);\n  } finally {\n    print('$s1');\n  }\n}",
      lambda p: [x for i in (1, 2, 3) for x in ([] if i == p["k"] else [str(i)]) + [1]],
      "continue still runs the finally, so the letter prints on every turn.", pre_k),
    L("for (var i = 1; i <= 3; i++) {\n  try {\n    if (i == $k) break;\n    print(i);\n  } finally {\n    print('$s1');\n  }\n}",
      lambda p: [x for i in range(1, p["k"] + 1) for x in ([] if i == p["k"] else [str(i)]) + [1]],
      "break still runs the finally once more on the way out.", pre_k),
    L("var n = 0;\nwhile (true) {\n  try {\n    n++;\n    if (n < $k) throw 'x';\n    print('$s1');\n    break;\n  } catch (e) {\n    print(n);\n  }\n}",
      lambda p: [str(i) for i in range(1, p["k"])] + [1],
      "Each failed turn prints n from the catch; the first turn that does not throw prints the letter and breaks.",
      pre_k24),
    L("try {\n  for (var i = 1; i <= 3; i++) {\n    if (i == $k) throw 'x';\n    print(i);\n  }\n} catch (e) {\n  print('$s1');\n}",
      lambda p: [str(i) for i in range(1, p["k"])] + [1],
      "The throw ends the whole loop, because the try is outside it.", pre_k),
    L("for (var i = 1; i <= 3; i++) {\n  try {\n    if (i == $k) throw 'x';\n    print(i);\n  } catch (e) {\n    print('$s1');\n  }\n}",
      lambda p: [str(i) if i != p["k"] else 1 for i in (1, 2, 3)],
      "The try is inside the loop, so only that turn is cut short; the loop goes on.", pre_k),
    L("[1, 2, 3].forEach((x) {\n  try {\n    if (x == $k) return;\n    print(x);\n  } finally {\n    print('$s1');\n  }\n});",
      lambda p: [y for x in (1, 2, 3) for y in ([] if x == p["k"] else [str(x)]) + [1]],
      "return only leaves this call of the closure; the finally still runs, and forEach moves on.", pre_k),
    L("void g() => throw '$w';\nvoid f() {\n  try {\n    g();\n  } catch (e) {\n    print('$s1');\n    rethrow;\n  }\n}\ntry {\n  f();\n} catch (e) {\n  print('$s2');\n}",
      [1, 2], "g throws, f's catch prints and rethrows, the outer catch prints."),
    L("void f() {\n  try {\n    print('$s1');\n    throw 'x';\n  } finally {\n    print('$s2');\n  }\n}\ntry {\n  f();\n  print('$s3');\n} catch (e) {\n  print('$s4');\n}",
      [1, 2, 4], "f's finally runs, then the exception leaves f and skips the print after the call."),
    L("try {\n  print('$s1');\n  throw '$w';\n} catch (e) {\n  print(e);\n  print('$s2');\n}",
      lambda p: [1, p["w"], 2], "print(e) shows the thrown value, here the text."),
    L("class MyError implements Exception {}\nclass BigError extends MyError {}\nvoid main() {\n  try {\n    throw BigError();\n  } on MyError {\n    print('$s1');\n  } catch (e) {\n    print('$s2');\n  }\n}",
      [1], "BigError is a MyError, so the on MyError clause catches it."),
    L("class MyError implements Exception {}\nclass BigError extends MyError {}\nvoid main() {\n  try {\n    throw MyError();\n  } on BigError {\n    print('$s1');\n  } on MyError {\n    print('$s2');\n  }\n}",
      [2], "A MyError is not a BigError (the child), so the second clause takes it."),
    L("class MyError implements Exception {}\nclass BigError extends MyError {}\nvoid main() {\n  try {\n    throw BigError();\n  } on MyError {\n    print('$s1');\n  } on BigError {\n    print('$s2');\n  }\n}",
      [1], "The parent clause comes first and fits, so the child clause is never reached."),
    L("class MyError implements Exception {}\nvoid main() {\n  try {\n    throw MyError();\n  } on Exception {\n    print('$s1');\n  } catch (e) {\n    print('$s2');\n  }\n}",
      [1], "A class that implements Exception is an Exception."),
    L("try {\n  try {\n    throw StateError('$w');\n  } on Exception {\n    print('$s1');\n  }\n} on Error {\n  print('$s2');\n}",
      [2], "A StateError is an Error, not an Exception, so the inner clause misses and the outer one catches it."),
    L("try {\n  try {\n    $t;\n  } on ArgumentError {\n    print('$s1');\n  }\n} catch (e) {\n  print('$s2');\n}",
      lambda p: [1] if catches(p["tc"], "ArgumentError") else [2],
      "RangeError is an ArgumentError, so on ArgumentError catches it too; the other types go on to the outer catch.", pre_t),
    L("try {\n  $t;\n} on Exception {\n  print('$s1');\n} on Error {\n  print('$s2');\n} catch (e) {\n  print('$s3');\n}",
      lambda p: [1] if catches(p["tc"], "Exception") else ([2] if catches(p["tc"], "Error") else [3]),
      "Exception and Error are the two families; a thrown String or int is neither, so only the plain catch takes it.", pre_t),
    L("try {\n  $t;\n} on String {\n  print('$s1');\n} on int {\n  print('$s2');\n} catch (e) {\n  print('$s3');\n}",
      lambda p: [1] if p["tc"] == "String" else ([2] if p["tc"] == "int" else [3]),
      "You can throw any value in Dart, and on String or on int catches by that type.", pre_t),
    L("try {\n  print('$s1');\n  $t;\n} catch (e) {\n  print('$s2');\n} finally {\n  print('$s3');\n}\nprint('$s4');",
      [1, 2, 3, 4], "Whatever is thrown, the catch handles it, the finally runs, and the program goes on.", pre_t),
    L("int f() {\n  try {\n    return int.parse('$w');\n  } on FormatException {\n    return -1;\n  }\n}\nprint(f());",
      ["-1"], "The word is not a number, so parse throws a FormatException and the clause returns -1."),
    L("int f() {\n  try {\n    return int.parse('$n');\n  } on FormatException {\n    return -1;\n  }\n}\nprint(f());",
      lambda p: [str(p["n"])], "The text is a number, so parse works and the clause is skipped."),
    L("int f() {\n  for (var i = 1; i < 5; i++) {\n    try {\n      if (i == $k) return i;\n    } finally {\n      print(i);\n    }\n  }\n  return 0;\n}\nprint(f());",
      lambda p: [str(i) for i in range(1, p["k"] + 1)] + [str(p["k"])],
      "The finally prints on every turn, including the turn that returns; the returned value prints last.", pre_k),
    L("try {\n  $r;\n  print('$s1');\n} on $c1 {\n  print('$s2');\n} catch (e) {\n  print('$s4');\n} finally {\n  print('$s3');\n}",
      lambda p: ([2, 3] if rhit(p) else [4, 3]) if p["rc"] else [1, 3],
      lambda p: "The operation " + ("throws, and its type fits the clause." if rhit(p) else
                                    "throws a type the clause does not fit, so the catch takes it." if p["rc"]
                                    else "works, so the try finishes and the clauses are skipped.") + " The finally runs last.",
      pre_real_maybe),
    L("try {\n  print('$s1');\n  $r;\n  print('$s2');\n} catch (e) {\n  print('$s3');\n}",
      [1, 3], "The operation throws; the print after it is skipped and the catch runs.", pre_real),
    L("try {\n  try {\n    $r;\n  } on $c1 {\n    print('$s1');\n  }\n} catch (e) {\n  print('$s2');\n}",
      lambda p: [1] if rhit(p) else [2],
      "A clause whose type does not fit lets the exception go on to the outer catch.", pre_real),
    L("try {\n  try {\n    $t;\n  } finally {\n    print('$s1');\n  }\n} on $c1 {\n  print('$s2');\n} catch (e) {\n  print('$s3');\n}",
      lambda p: [1, 2] if hit(p) else [1, 3],
      "The inner finally runs first on the way out; then the outer clauses choose.", pre_c1),
    L("try {\n  print('$s1');\n} finally {\n  print('$s2');\n}\nprint('$s3');",
      [1, 2, 3], "No exception: try, then finally, then the rest."),
    L("var s = '';\nfor (var i = 1; i <= 3; i++) {\n  try {\n    if (i.isOdd) throw i;\n    s += 'a';\n  } catch (e) {\n    s += 'b';\n  } finally {\n    s += 'c';\n  }\n}\nprint(s);",
      ["bcacbc"], "Odd turns throw: b then c; the even turn goes a then c."),
    L("for (var i = 1; i <= $k; i++) {\n  try {\n    if (i == 2) throw i;\n    print('$s1');\n  } catch (e) {\n    print('$s2');\n    continue;\n  } finally {\n    print('$s3');\n  }\n  print('$s4');\n}",
      lambda p: [1, 3, 4, 2, 3] + [1, 3, 4] * (p["k"] - 2),
      "On the turn that throws, continue skips the last print, but the finally still runs.", lambda p, rng: p.update(k=rng.randint(2, 3))),
]
