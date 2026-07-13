"""
Adaptive coach messages.

Level 1 (dictation): ONLY show the exact line to type. Clear wrong/missing feedback.
Level 2 (vocabulary): more recall; example still available.
"""

from __future__ import annotations

import re
from typing import Any

# A whole-number assignment in a step's example: favorite_number = 7
_INT_ASSIGN_RE = re.compile(r"^(\w+)\s*=\s*(-?\d+)\s*$", re.MULTILINE)


def _quoted_number_note(code: str, example: str) -> str | None:
    """The classic beginner slip: var = \"5\" where a number is expected.
    Quotes turn the digits into text, so the check (rightly) fails — but the
    student needs to hear WHY, not 'type this line'."""
    for var, num in _INT_ASSIGN_RE.findall(example or ""):
        quoted = rf"{re.escape(var)}\s*=\s*[\"']\s*-?\d+\s*[\"']"
        if re.search(quoted, code):
            return (
                f"Not yet — quotes make it text, not a number. "
                f"Drop them: {var} = {num}"
            )
    return None


def build_adaptation(
    *,
    code: str,
    step: Any | None,
    style: str,
    stdout: str,
    stderr: str,
    exit_code: int,
    ran: bool,
    passed: int,
    total: int,
    complete: bool,
    just_passed_label: str | None = None,
) -> dict[str, Any]:
    nonempty = [
        ln
        for ln in code.splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]

    if complete:
        return {
            "observation": f"All {total} lines are in. Nice work.",
            "guidance": "Press Run to see output, then Continue.",
            "example": None,
            "tone": "celebrate",
            "status": "done",
        }

    if ran and exit_code != 0:
        err = (stderr or "").strip() or "Unknown runtime error."
        short = err.splitlines()[-1] if err else err
        return {
            "observation": f"Error: {short}",
            "guidance": "Fix the error, then keep typing the line below.",
            "example": step.example if step else None,
            "tone": "error",
            "status": "error",
        }

    if not step:
        return {
            "observation": "Caught up.",
            "guidance": "",
            "example": None,
            "tone": "ok",
            "status": "done",
        }

    example = step.example
    wrong_note = _whats_wrong(code, step)

    if style == "dictation":
        # Zero abstraction: the example IS the task. No line numbers here —
        # the exercise box and nav already show position, and this message
        # must describe the same line the student is looking at.
        if just_passed_label:
            obs = "Got it. Next line:"
        elif not nonempty:
            obs = "Type this line in the editor:"
        elif wrong_note:
            obs = wrong_note
        else:
            obs = "Keep typing this line:"

        return {
            "observation": obs,
            # No prose goals — UI shows the code block as the instruction
            "guidance": "",
            "example": example,
            "tone": "wrong" if (wrong_note and nonempty) else ("nudge" if nonempty else "ok"),
            "status": (
                "wrong"
                if wrong_note and nonempty
                else ("working" if nonempty else "waiting")
            ),
        }

    # vocabulary
    if wrong_note and nonempty:
        obs = wrong_note
        tone, status = "wrong", "wrong"
    elif not nonempty:
        obs = "Recall and type the next line."
        tone, status = "ok", "waiting"
    else:
        obs = f"{passed}/{total} · working on next line"
        tone, status = "nudge", "working"

    return {
        "observation": obs,
        "guidance": f"{step.concept}: {step.hint}",
        "example": example,
        "tone": tone,
        "status": status,
    }


def _whats_wrong(code: str, step: Any) -> str | None:
    sid = getattr(step, "id", "") or ""
    compact = code.replace(" ", "")
    lower = code.lower()
    ex = getattr(step, "example", "") or ""

    if "pint(" in compact or "pint " in lower:
        return "Not yet — typo: use print( not pint("
    if "Print(" in code and "print(" not in compact:
        return "Not yet — use lowercase print("

    # Quoted digits where the goal wants a real number — diagnose it directly.
    quoted_num = _quoted_number_note(code, ex)
    if quoted_num:
        return quoted_num

    if sid == "print":
        if "print" in lower and "print(" not in compact:
            return "Not yet — need parentheses: print(...)"
        if "print(" in compact and not any(
            ln.strip().startswith("print(") and ln.strip().endswith(")")
            for ln in code.splitlines()
        ):
            return "Keep typing — finish the whole line (closing quote and )."
        if "print(" in compact and '"' not in code and "'" not in code:
            return 'Not yet — put text in quotes: print("Hello, world!")'
        return f"Not yet — finish this full line:\n{ex}"

    if sid in ("name_var", "city_var"):
        var = "name" if sid == "name_var" else "city"
        for ln in code.splitlines():
            s = ln.strip()
            if s.startswith(var) and "=" in s and not (
                s.count('"') >= 2 or s.count("'") >= 2
            ):
                return "Keep typing — finish the quotes on this line."
        return f"Not yet — finish this full line:\n{ex}"

    if sid == "favorite_number_var":
        for ln in code.splitlines():
            s = ln.strip().replace(" ", "")
            if s.startswith("favorite_number=") and ('"' in s or "'" in s):
                return "Not yet — no quotes around the number:\nfavorite_number = 7"
        return f"Not yet — type this line:\n{ex}"

    if sid == "print_name":
        if 'print("name")' in compact or "print('name')" in compact:
            return "Not yet — no quotes around name:\nprint(name)"
        return f"Not yet — type this line:\n{ex}"

    if sid == "print_city":
        if 'print("city")' in compact or "print('city')" in compact:
            return "Not yet — no quotes around city:\nprint(city)"
        return f"Not yet — type this line:\n{ex}"

    if sid == "print_favorite_number":
        return f"Not yet — type this line:\n{ex}"

    # Build exercises aren't verbatim — don't say "type this line" (it sends
    # students hunting for exact wording) and don't leak the solution here;
    # the Hint ladder owns that. Dictation keeps the literal instruction.
    if getattr(step, "concept", "") == "build":
        return "Not yet — check the small details: quotes, parentheses, spelling. Hint can help."

    return f"Not yet — type this line:\n{ex}" if ex else "Not yet — keep going."
