"""Run a student's program under a line tracer and print JSON snapshots.

Spawned as a subprocess by `visualize.trace_code` — deliberately standalone
(no code_coach imports) so it runs with a bare `python runner.py target.py`
and inherits the same timeout and resource limits as a normal Run.

Output on stdout is a single JSON object preceded by SENTINEL. Anything the
student's own program prints is captured separately and reported inside that
JSON, so their print() can't corrupt the payload.
"""

from __future__ import annotations

import io
import json
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr

SENTINEL = "<<<CODE_COACH_TRACE>>>"

# Ceilings. A tight loop can produce millions of line events and a recursive
# structure can be unboundedly wide; the point is a readable picture, not a
# complete memory dump.
MAX_STEPS = 400
MAX_ITEMS = 60
MAX_FIELDS = 12
MAX_DEPTH = 8
MAX_STRING = 120


def _prim(value: object) -> dict | None:
    """A JSON-safe leaf, or None if this needs a heap entry."""
    if value is None or isinstance(value, bool):
        return {"k": "prim", "t": "bool" if isinstance(value, bool) else "none",
                "v": value}
    if isinstance(value, int):
        return {"k": "prim", "t": "int", "v": value}
    if isinstance(value, float):
        return {"k": "prim", "t": "float", "v": value}
    if isinstance(value, str):
        clipped = value[:MAX_STRING]
        return {"k": "prim", "t": "str", "v": clipped,
                "clipped": len(value) > MAX_STRING}
    return None


def _encode(value: object, heap: dict, seen: dict, depth: int = 0) -> dict:
    """Serialise `value`, putting containers/objects in `heap` and returning a
    reference. `seen` maps id() → heap key so shared and cyclic structures
    (a linked list that loops, a tree with parent pointers) terminate."""
    leaf = _prim(value)
    if leaf is not None:
        return leaf

    if depth >= MAX_DEPTH:
        return {"k": "prim", "t": "str", "v": "…", "clipped": True}

    key = id(value)
    if key in seen:
        return {"k": "ref", "id": seen[key]}

    ref = len(seen) + 1
    seen[key] = ref
    entry: dict = {}
    heap[ref] = entry

    if isinstance(value, (list, tuple)):
        entry.update(
            k="list",
            tuple=isinstance(value, tuple),
            n=len(value),
            items=[_encode(v, heap, seen, depth + 1) for v in value[:MAX_ITEMS]],
        )
    elif isinstance(value, dict):
        pairs = []
        for i, (k, v) in enumerate(value.items()):
            if i >= MAX_ITEMS:
                break
            pairs.append([_encode(k, heap, seen, depth + 1),
                          _encode(v, heap, seen, depth + 1)])
        entry.update(k="dict", n=len(value), pairs=pairs)
    elif isinstance(value, (set, frozenset)):
        entry.update(
            k="set",
            n=len(value),
            items=[_encode(v, heap, seen, depth + 1)
                   for v in list(value)[:MAX_ITEMS]],
        )
    elif hasattr(value, "__dict__") and not callable(value):
        fields = {}
        for i, (name, v) in enumerate(vars(value).items()):
            if i >= MAX_FIELDS:
                break
            fields[name] = _encode(v, heap, seen, depth + 1)
        entry.update(k="obj", cls=type(value).__name__, fields=fields)
    else:
        try:
            text = repr(value)
        except Exception:
            text = f"<{type(value).__name__}>"
        entry.update(k="opaque", cls=type(value).__name__, v=text[:MAX_STRING])

    return {"k": "ref", "id": ref}


_MISSING = object()


def _snapshot(frame, returned: object = _MISSING) -> dict:
    heap: dict = {}
    seen: dict = {}
    local_vars = {}
    for name, value in list(frame.f_locals.items())[:40]:
        if name.startswith("__"):
            continue
        try:
            local_vars[name] = _encode(value, heap, seen)
        except Exception:
            local_vars[name] = {"k": "prim", "t": "str", "v": "<unreadable>"}
    snap = {"line": frame.f_lineno, "func": frame.f_code.co_name,
            "vars": local_vars, "heap": heap}
    # A `line` event fires BEFORE its line runs, so the last one only ever
    # shows the state just short of the answer. `return` fires after the value
    # is computed — that's the frame that actually finishes the story.
    if returned is not _MISSING:
        try:
            snap["returned"] = _encode(returned, heap, seen)
        except Exception:
            snap["returned"] = {"k": "prim", "t": "str", "v": "<unreadable>"}
    return snap


def main() -> int:
    target = sys.argv[1]
    with open(target, encoding="utf-8") as fh:
        source = fh.read()

    steps: list[dict] = []
    truncated = False

    def tracer(frame, event, arg):
        nonlocal truncated
        # Only the student's file; skip our own frames and the stdlib.
        if frame.f_code.co_filename != target:
            return None
        if event not in ("line", "return"):
            return tracer
        if len(steps) >= MAX_STEPS:
            truncated = True
            sys.settrace(None)
            return None
        try:
            if event == "return":
                # Skip the module's own return — it carries no useful value and
                # would tack a bare "returned None" onto the end.
                if frame.f_code.co_name != "<module>":
                    steps.append(_snapshot(frame, arg))
            else:
                steps.append(_snapshot(frame))
        except Exception:
            pass
        return tracer

    out, err = io.StringIO(), io.StringIO()
    error = None
    code_obj = compile(source, target, "exec")
    globals_ns: dict = {"__name__": "__main__", "__file__": target}
    try:
        with redirect_stdout(out), redirect_stderr(err):
            sys.settrace(tracer)
            try:
                exec(code_obj, globals_ns)
            finally:
                sys.settrace(None)
    except BaseException:
        error = traceback.format_exc(limit=3)

    payload = {
        "steps": steps,
        "truncated": truncated,
        "stdout": out.getvalue()[:4000],
        "stderr": err.getvalue()[:2000],
        "error": error,
    }
    sys.stdout.write(SENTINEL + json.dumps(payload))
    return 0


if __name__ == "__main__":
    sys.exit(main())
