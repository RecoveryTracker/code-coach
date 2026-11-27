"""Check ONE Brain Drills C, SQL, TypeScript or Rust pack (or activity) against the real compilers / SQLite, outside pytest.

    .venv/Scripts/python.exe -m tests.brain_check ccore          # every activity of pack_ccore.py
    .venv/Scripts/python.exe -m tests.brain_check c_loop         # one activity
    .venv/Scripts/python.exe -m tests.brain_check sql_ --seeds 12

The argument is a pack name (`ccore`, `pack_ccore`) or an activity id or id prefix (`c_`, `cstr_`, `sql_win`). What it does,
per matching activity of the C or SQL language: the same samples tests/test_brain_packs.py takes (every template on
`--seeds` seeds, 12 whole rounds), the shape rules (prompt <= 220 characters and 10 lines, answer short and not
padded, no `$` hole left, an explanation), and the ORACLE - for C every item through every build (clang -O0 and -O2,
signed and unsigned `char`, MSVC /Od when installed: all must print the model's answer), the warning lint and the
undefined-behaviour sanitizer; for SQL every script in a fresh in-memory SQLite; for TypeScript every item through
`tsc --strict` and node (tests/ts_oracle.py), for Rust every item through rustc debug and -O (tests/rust_oracle.py). An
activity with `oracle="error"` is judged by whether the code fails to compile or throws / panics. Prints the first problems and exits 1
when there are any. Cost: C is ~1 s per 30 programs in a body batch plus ~50 ms for every complete program (a program
with its own `main`); SQL is ~0.3 ms an item.
"""

from __future__ import annotations

import argparse
import importlib
import random
import sys

from code_coach import brain
from code_coach.brain import activities_in, activity_for, make_round


def _matching(arg: str, language: str):
    pack = arg if arg.startswith("pack_") else "pack_" + arg
    pack_ids: set[str] = set()
    if pack in brain.PACKS:
        pack_ids = {a.id for a in importlib.import_module(f"code_coach.brain.{pack}").ACTIVITIES}
    return [a for a in activities_in(language) if a.id in pack_ids or a.id.startswith(arg)]


def _samples(activity, language: str, seeds: int) -> list:
    seen: dict[str, object] = {}
    for seed in range(12):
        for item in make_round(activity.id, seed, language):
            seen.setdefault(item.prompt + "\x00" + item.check, item)
    for template in getattr(activity_for(activity.id, language).make, "templates", ()):
        for seed in range(seeds):
            item = template(random.Random(seed))
            seen.setdefault(item.prompt + "\x00" + item.check, item)
    return list(seen.values())


def _shape(item) -> list[str]:
    problems = []
    if len(item.prompt) > 220 or item.prompt.count("\n") > 9:
        problems.append("prompt over 220 characters or 10 lines")
    if not item.answer or len(item.answer) > 40 or item.answer != item.answer.strip() or "\n" in item.answer:
        problems.append(f"answer {item.answer!r} is empty, long, padded or has a newline")
    if "$" in item.prompt or "$" in item.explain:
        problems.append("a $ hole is left")
    if len(item.explain.strip()) < 8:
        problems.append("no explanation")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", help="a pack name or an activity id / prefix")
    ap.add_argument("--seeds", type=int, default=6, help="seeds per template (default 6)")
    args = ap.parse_args(argv)

    bad = 0
    for language in ("c", "sql", "typescript", "rust"):
        acts = _matching(args.what, language)
        if not acts:
            continue
        samples = {a.id: _samples(a, language, args.seeds) for a in acts}
        flat = [(a_id, i) for a_id, items in samples.items() for i in items]
        print(f"{language}: {len(acts)} activities, {len(flat)} items")
        for a in acts:
            n = len(getattr(activity_for(a.id, language).make, "templates", ()))
            print(f"  {a.id}: {n} templates, {len(samples[a.id])} items, par {a.par} slow {a.slow}")
        for a_id, i in flat:
            for p in _shape(i):
                bad += 1
                print(f"SHAPE {a_id}: {p}: {i.prompt!r}")
        if language == "c":
            from tests import c_oracle

            if not c_oracle.HAVE_COMPILER:
                print("no C compiler: oracle skipped")
                continue
            programs = [i.check or i.prompt for _, i in flat]
            for (a_id, i), prog in zip(flat, programs):
                why = c_oracle.lint(prog)
                if why:
                    bad += 1
                    print(f"LINT {a_id}: {why}: {i.prompt!r}")
            checked = c_oracle.check_items(programs)
            for (a_id, i), c in zip(flat, checked):
                if c.value != i.answer:
                    bad += 1
                    print(f"ORACLE {a_id}: model says {i.answer!r}, compilers say {c.value!r}: {i.prompt!r}")
                if c_oracle.bad_warnings(c.warnings):
                    bad += 1
                    print(f"WARNING {a_id}: {c_oracle.bad_warnings(c.warnings)}: {i.prompt!r}")
            for k, why in c_oracle.ub_findings(programs).items():
                bad += 1
                print(f"UNDEFINED {flat[k][0]}: {why}: {flat[k][1].prompt!r}")
        elif language in ("typescript", "rust"):
            if language == "typescript":
                from tests import ts_oracle as oracle
                results = oracle.ts_results if oracle.HAVE_TSC else None
            else:
                from tests import rust_oracle as oracle
                results = oracle.rust_results if oracle.HAVE_RUSTC else None
            if results is None:
                print(f"no {language} toolchain: oracle skipped")
                continue
            modes = {a.id: a.oracle for a in acts}
            for (a_id, i), r in zip(flat, results([i.check or i.prompt for _, i in flat])):
                got = r.verdict if modes[a_id] == "error" else r.value
                if got != i.answer:
                    bad += 1
                    print(f"ORACLE {a_id}: model says {i.answer!r}, {language} says {got!r} ({r.value[:160]!r}): {i.prompt!r}")
        else:
            from tests import sql_oracle

            for (a_id, i), got in zip(flat, sql_oracle.sql_values([i.check or i.prompt for _, i in flat])):
                if got != i.answer:
                    bad += 1
                    print(f"ORACLE {a_id}: model says {i.answer!r}, SQLite says {got!r}: {i.prompt!r}")
    print("problems:", bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
