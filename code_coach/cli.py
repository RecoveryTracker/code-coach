"""
Code Coach CLI

One-shot:
  python3 -m code_coach

Live watch:
  python3 -m code_coach --watch

Point at Learn to code (training guide):
  python3 -m code_coach --watch --curriculum "/path/to/Learn to code" --day 1
"""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from code_coach.engine import evaluate, format_report
from code_coach.lessons import UnknownLessonError, get_lesson

# Sibling folder next to this repo, if both live under GitHub/
DEFAULT_CURRICULUM_CANDIDATES = [
    Path(__file__).resolve().parent.parent.parent / "Learn to code",
    Path.home() / "Documents" / "GitHub" / "Learn to code",
]


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def find_default_curriculum() -> Path | None:
    for path in DEFAULT_CURRICULUM_CANDIDATES:
        if path.is_dir() and (path / "python").is_dir():
            return path
    return None


def resolve_practice_path(
    *,
    file: str | None,
    curriculum: str | None,
    day: int,
) -> Path:
    if file:
        return Path(file).expanduser().resolve()

    curriculum_path: Path | None
    if curriculum:
        curriculum_path = Path(curriculum).expanduser().resolve()
    else:
        curriculum_path = find_default_curriculum()

    if curriculum_path is None:
        raise SystemExit(
            "No practice file specified, and Learn to code curriculum not found.\n"
            "Use --file path/to/practice.py\n"
            "  or --curriculum path/to/Learn to code --day 1"
        )

    lesson = get_lesson(day)
    relative = lesson.get("relative_path", f"python/day-{day:02d}/practice.py")
    practice = curriculum_path / relative
    if not practice.exists():
        raise SystemExit(f"Practice file not found: {practice}")
    return practice


def once(practice: Path, lesson: dict) -> None:
    result = evaluate(lesson, practice)
    print(format_report(result))


def watch(practice: Path, lesson: dict, poll_seconds: float = 0.4) -> None:
    print("Code Coach watch mode", flush=True)
    print(f"Watching: {practice}", flush=True)
    print("Edit & save the practice file — coach updates automatically.", flush=True)
    print("Ctrl+C to stop.\n", flush=True)

    last_mtime: float | None = None
    last_report = ""

    try:
        while True:
            try:
                mtime = practice.stat().st_mtime
            except FileNotFoundError:
                time.sleep(poll_seconds)
                continue

            if last_mtime is None or mtime != last_mtime:
                last_mtime = mtime
                result = evaluate(lesson, practice)
                report = format_report(result)
                if report != last_report:
                    clear_screen()
                    print(report, flush=True)
                    print("\n--- watching for saves (Ctrl+C to quit) ---", flush=True)
                    last_report = report

            time.sleep(poll_seconds)
    except KeyboardInterrupt:
        print("\nStopped watching.", flush=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="code_coach",
        description="Code Coach — watch student code and suggest the next change",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Recalculate whenever the practice file changes",
    )
    parser.add_argument(
        "--file",
        help="Path to the student's practice.py (overrides --curriculum)",
    )
    parser.add_argument(
        "--curriculum",
        help='Path to the "Learn to code" training guide repo',
    )
    parser.add_argument(
        "--day",
        type=int,
        default=1,
        help="Lesson day number when using --curriculum (default: 1)",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        lesson = get_lesson(args.day)
    except UnknownLessonError as exc:
        raise SystemExit(str(exc)) from exc

    practice = resolve_practice_path(
        file=args.file,
        curriculum=args.curriculum,
        day=args.day,
    )

    if args.watch:
        watch(practice, lesson)
    else:
        once(practice, lesson)


if __name__ == "__main__":
    main()
