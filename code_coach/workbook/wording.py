"""Small wording helpers for prompts built out of parts.

A prompt assembled from a condition and a fixed tail can end up
ungrammatical for some conditions and fine for others, which is a thing
no test notices and every reader does.
"""

from __future__ import annotations

#: Forms of "be". English elides the verb in the second half of "print A
#: if n is big, and B if it is not", and the stand-in has to be the same
#: verb: "is not" after "is", "does not" after a verb like "divides".
_BE = {"is": "is not", "are": "are not",
       "was": "was not", "were": "were not"}


def negated(condition: str) -> str:
    """The negative half of "print A if <condition>, and B if it ...".

    "n is more than 5" elides a copula, so the tail is "if it is not".
    "n divides exactly by 2" elides a lexical verb, so it is "if it does
    not". Writing either one down flat gets half of them wrong, which is
    what it did: seventy-three prompts read "if n is more than 5 ... if
    it does not" until someone reading the page noticed.

    Derived from the condition rather than chosen per template, so a
    condition added later is worded correctly without anyone remembering
    this rule.
    """
    first = condition.strip().split(" ", 1)[0].lower()
    return _BE.get(first, "does not")
