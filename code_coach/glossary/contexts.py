"""Words a screen always teaches, whatever the code on it looks like.

A context is the id of the thing the learner is doing: a Brain Drills activity
(`code_coach.brain.ACTIVITIES`). Its terms are shown first by `find_words`, in
this order, whether or not the snippet's text mentions them - the Truthy or Falsy
drill's code is `print("truthy" if (0) else "falsy")`, and the words that drill
is about are not in it.

Two sources, one answer:

* `CONTEXTS` is the hand-kept map for the ORIGINAL seven activities (exact glossary
  ids, same words in both languages; an id a language does not define is skipped for
  that language - Loop Count lists `range`, which only Python has).
* Every OTHER activity (the packs) is DERIVED: its `Activity.concepts` are plain words a
  pack author chose, and `glossary.resolve()` turns each into an entry per language
  (id, term or aka; hyphen, space, case and plural differences are ignored). A concept a
  language has no word for is skipped for that language. Nothing here needs an edit when
  a pack is added; to teach a missing word, write the entry (terms_brain_*.py).

The brain package is imported lazily, inside `concepts_for`, so the glossary never
needs it at import time.
"""

from __future__ import annotations

CONTEXTS: dict[str, tuple[str, ...]] = {
    # Quick Eval: work out what an expression prints.
    "eval": ("expression", "evaluate", "operator", "precedence"),
    # Truthy or Falsy: which values an if treats as true.
    "truthy": ("truthy", "falsy"),
    # Loop Count: how many times a loop's body runs.
    "loops": ("loop", "iteration", "off-by-one", "range"),
    # Final Value: follow assignments to the last value of x.
    "trace": ("variable", "assignment", "reassign"),
    # Bracket Check: are the brackets balanced.
    "brackets": ("bracket", "balanced", "nesting"),
    # Variable Recall: remember names and their values.
    "recall": ("variable", "value", "assignment"),
    # Syntax Snap: would the language accept this line.
    "syntax": ("syntax", "syntax-error", "token", "keyword"),
}


def concepts_for(activity_id: str) -> tuple[str, ...]:
    """The `concepts` a Brain Drills activity declares ("" ids, unknown ids, or a brain package
    that cannot be imported: an empty tuple, never an error)."""
    key = (activity_id or "").strip().lower()
    if not key:
        return ()
    try:
        from code_coach.brain import ACTIVITIES_BY_ID  # lazy: brain must never be needed to import us
    except Exception:
        return ()
    activity = ACTIVITIES_BY_ID.get(key)
    return tuple(activity.concepts) if activity is not None else ()
