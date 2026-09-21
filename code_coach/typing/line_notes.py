"""What one line of code does, worked out from the line itself.

The hand-picked snippets each carry a note written by a person: "the
Two Sum line", "pick the winner". The curriculum lines do not. They are
real solutions sliced into lines, so all several hundred of them carry
the same note, which is the name of the problem they came from. Typing
fourteen lines of Decode String shows you "#394 Decode String"
fourteen times and tells you nothing about the line under your fingers.

Writing a note for every line by hand is the obvious fix and the wrong
one: it is a list keyed on content that somebody has to maintain
forever, and this project has been bitten by five of those already. So
the note is derived from the line.

The rule that keeps this honest
-------------------------------
A description must never assert something the line does not say.

That is achievable only by refusing to guess. Each rule matches an
exact syntactic shape, and every name that appears in the output is
lifted verbatim out of the line it describes — nothing is inferred
about types, intent, or what the surrounding function is doing. A line
that matches no rule gets no description at all and falls back to the
problem name, which was the old behaviour. Silence is a correct answer
here; a confident wrong caption is not, because the person reading it
is by definition not yet able to catch it.

So the coverage will never be a hundred per cent, and it should not be.
`start = left` genuinely cannot be explained without knowing the
algorithm, and this module has no way to know the algorithm.
"""

from __future__ import annotations

import re

#: Lines that describe nothing on their own: closing punctuation, a
#: lone brace, a decorator's argument spilling over. Restating these
#: adds a caption saying "a closing bracket", which is noise.
_NOT_WORTH_SAYING = re.compile(r"^[\s)\]}>;,]*$")

#: A bare name or dotted name, used to check a captured fragment really
#: is one identifier rather than an expression we would be paraphrasing.
_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _is_name(text: str) -> bool:
    return bool(_NAME.match(text.strip()))


def _python(line: str) -> str | None:
    """Python shapes, most specific first."""
    s = line.strip()

    # Loops. enumerate and the plain form say different things, and the
    # difference is the whole reason enumerate exists.
    m = re.match(r"^for\s+\w+\s*,\s*\w+\s+in\s+enumerate\(([^)]+)\)\s*:$", s)
    if m:
        return f"walk {m.group(1)} with the index as well as the value"
    m = re.match(r"^for\s+\w+\s*,\s*\w+\s+in\s+([\w.]+)\.items\(\)\s*:$", s)
    if m:
        return f"walk {m.group(1)}, key and value together"
    m = re.match(r"^for\s+\w+\s*,\s*\w+\s+in\s+zip\(([^)]+)\)\s*:$", s)
    if m:
        return f"walk {m.group(1)} side by side"
    m = re.match(r"^for\s+(\w+)\s+in\s+range\((.+)\)\s*:$", s)
    if m:
        return f"count {m.group(1)} through range({m.group(2)})"
    # Anything else iterable, including a call chain. The expression is
    # quoted rather than summarised, so this cannot claim the wrong thing.
    m = re.match(r"^for\s+\w+\s+in\s+(.+?)\s*:$", s)
    if m:
        return f"one pass over {m.group(1)}"

    m = re.match(r"^while\s+(.+?)\s*:$", s)
    if m:
        return f"keep going while {m.group(1)}"

    # Branches. The condition is quoted rather than interpreted.
    m = re.match(r"^if\s+(.+?)\s*:$", s)
    if m:
        return f"the branch taken when {m.group(1)}"
    m = re.match(r"^elif\s+(.+?)\s*:$", s)
    if m:
        return f"otherwise, the branch for {m.group(1)}"
    if s == "else:":
        return "what happens when none of the tests above matched"

    # Definitions.
    m = re.match(r"^def\s+(\w+)\s*\(", s)
    if m:
        return f"the signature of {m.group(1)}"
    m = re.match(r"^class\s+(\w+)\b", s)
    if m:
        return f"the start of the {m.group(1)} type"

    # Leaving.
    if s == "return":
        return "leave the function with nothing to hand back"
    m = re.match(r"^return\s+(.+)$", s)
    if m:
        return f"hand back {m.group(1)}"
    if s == "break":
        return "stop the loop here, skip the rest of it"
    if s == "continue":
        return "skip to the next turn of the loop"
    if s == "pass":
        return "deliberately do nothing"
    m = re.match(r"^yield\s+(.+)$", s)
    if m:
        return f"hand out {m.group(1)} and wait to be asked again"
    m = re.match(r"^raise\s+(\w+)\b", s)
    if m:
        return f"give up and report a {m.group(1)}"

    # Errors and resources.
    if s == "try:":
        return "the block that is allowed to fail"
    m = re.match(r"^except\s+([\w.]+)", s)
    if m:
        return f"what to do about a {m.group(1)}"
    if s == "except:":
        return "what to do about anything that went wrong"
    if s == "finally:":
        return "the cleanup that runs whether or not it worked"
    m = re.match(r"^with\s+(.+?)\s+as\s+(\w+)\s*:$", s)
    if m:
        return f"open {m.group(1)} as {m.group(2)}, and close it afterwards"

    # Imports.
    m = re.match(r"^import\s+([\w.]+)$", s)
    if m:
        return f"bring in {m.group(1)}"
    m = re.match(r"^from\s+([\w.]+)\s+import\s+(.+)$", s)
    if m:
        return f"take {m.group(2)} out of {m.group(1)}"

    # Common method calls, where the method name is the meaning.
    m = re.match(r"^([\w.]+)\.append\((.+)\)$", s)
    if m:
        return f"add {m.group(2)} onto the end of {m.group(1)}"
    m = re.match(r"^([\w.]+)\.add\((.+)\)$", s)
    if m:
        return f"put {m.group(2)} into {m.group(1)}"
    m = re.match(r"^([\w.]+)\.pop\(\)$", s)
    if m:
        return f"take the last item off {m.group(1)}"
    m = re.match(r"^([\w.]+)\.sort\(\)$", s)
    if m:
        return f"sort {m.group(1)} where it stands"
    m = re.match(r"^print\((.+)\)$", s)
    if m:
        return f"show {m.group(1)}"

    # Assignment, last because almost anything can be one.
    m = re.match(r"^(\w+)\s*\+=\s*(.+)$", s)
    if m:
        return f"add {m.group(2)} to {m.group(1)}"
    m = re.match(r"^(\w+)\s*-=\s*(.+)$", s)
    if m:
        return f"take {m.group(2)} off {m.group(1)}"
    m = re.match(r"^(\w+)\s*,\s*(\w+)\s*=\s*(.+)$", s)
    if m:
        return f"set {m.group(1)} and {m.group(2)} together, in one step"
    m = re.match(r"^(\w+)\s*=\s*(.+)$", s)
    if m and _is_name(m.group(1)):
        return f"give {m.group(1)} its value"
    m = re.match(r"^(\w+)\[(.+?)\]\s*=\s*(.+)$", s)
    if m:
        return f"store something in {m.group(1)} under {m.group(2)}"

    return None


def _javascript(line: str) -> str | None:
    """JavaScript and TypeScript shapes."""
    s = line.strip()

    m = re.match(r"^for\s*\(\s*const\s+\[\s*\w+\s*,\s*\w+\s*\]\s+of\s+(.+?)\)\s*\{$", s)
    if m:
        return f"walk {m.group(1).strip()}, key and value together"
    m = re.match(r"^for\s*\(\s*(?:const|let|var)\s+\w+\s+of\s+(.+?)\)\s*\{$", s)
    if m:
        return f"one pass over {m.group(1).strip()}"
    m = re.match(r"^for\s*\(\s*(?:let|var)\s+(\w+)\s*=", s)
    if m:
        return f"the counting loop, on {m.group(1)}"
    m = re.match(r"^while\s*\((.+?)\)\s*\{$", s)
    if m:
        return f"keep going while {m.group(1)}"

    m = re.match(r"^if\s*\((.+?)\)\s*\{?$", s)
    if m:
        return f"the branch taken when {m.group(1)}"
    if re.match(r"^\}\s*else\s*\{$", s) or s == "else {":
        return "what happens when the test above failed"
    m = re.match(r"^\}\s*else if\s*\((.+?)\)\s*\{$", s)
    if m:
        return f"otherwise, the branch for {m.group(1)}"
    # if (cond) doIt(); with no brace. The test still carries the
    # meaning, and saying that much beats saying nothing.
    m = re.match(r"^if\s*\((.+?)\)\s+\S.*;$", s)
    if m:
        return f"the one thing done when {m.group(1)}"

    m = re.match(r"^(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(", s)
    if m:
        return f"the signature of {m.group(1)}"
    m = re.match(r"^(?:export\s+)?class\s+(\w+)\b", s)
    if m:
        return f"the start of the {m.group(1)} type"
    m = re.match(r"^constructor\s*\(", s)
    if m:
        return "how one of these gets built"

    if s in {"return;", "return"}:
        return "leave the function with nothing to hand back"
    m = re.match(r"^return\s+(.+?);?$", s)
    if m:
        return f"hand back {m.group(1)}"
    if s in {"break;", "break"}:
        return "stop the loop here, skip the rest of it"
    if s in {"continue;", "continue"}:
        return "skip to the next turn of the loop"
    m = re.match(r"^throw\s+new\s+(\w+)\b", s)
    if m:
        return f"give up and report a {m.group(1)}"

    if s in {"try {", "try{"}:
        return "the block that is allowed to fail"
    m = re.match(r"^\}?\s*catch\s*\(\s*(\w+)\s*\)\s*\{$", s)
    if m:
        return f"what to do when it failed, with the reason in {m.group(1)}"
    if re.match(r"^\}?\s*finally\s*\{$", s):
        return "the cleanup that runs whether or not it worked"

    m = re.match(r"^import\s+\{\s*(.+?)\s*\}\s+from\s+(.+?);?$", s)
    if m:
        return f"take {m.group(1)} out of {m.group(2)}"
    m = re.match(r"^import\s+(\w+)\s+from\s+(.+?);?$", s)
    if m:
        return f"bring in {m.group(1)} from {m.group(2)}"
    m = re.match(r"^export\s+\{\s*(.+?)\s*\};?$", s)
    if m:
        return f"offer {m.group(1)} to whoever imports this file"

    m = re.match(r"^([\w.]+)\.push\((.+?)\);?$", s)
    if m:
        return f"add {m.group(2)} onto the end of {m.group(1)}"
    m = re.match(r"^([\w.]+)\.set\((.+?)\);?$", s)
    if m:
        return f"record {m.group(2)} in {m.group(1)}"
    # The array methods whose name is the meaning. Safe to describe
    # because the method decides what happens, not the callback.
    m = re.match(r"^([\w.]+)\.forEach\(", s)
    if m:
        return f"do the same thing to every item of {m.group(1)}"
    m = re.match(r"^([\w.]+)\.map\(", s)
    if m:
        return f"build a new list from every item of {m.group(1)}"
    m = re.match(r"^([\w.]+)\.filter\(", s)
    if m:
        return f"keep only the items of {m.group(1)} that pass the test"
    m = re.match(r"^console\.log\((.+?)\);?$", s)
    if m:
        return f"show {m.group(1)}"

    m = re.match(r"^(\w+)\s*\+=\s*(.+?);?$", s)
    if m:
        return f"add {m.group(2)} to {m.group(1)}"
    m = re.match(r"^(?:const|let|var)\s+\[\s*(.+?)\s*\]\s*=\s*(.+?);?$", s)
    if m:
        return f"pull {m.group(1)} out of {m.group(2)} in order"
    m = re.match(r"^(?:const|let|var)\s+\{\s*(.+?)\s*\}\s*=\s*(.+?);?$", s)
    if m:
        return f"pull {m.group(1)} out of {m.group(2)} by name"
    m = re.match(r"^(?:const|let|var)\s+(\w+)\s*=\s*(.+?);?$", s)
    if m:
        return f"name {m.group(1)}, and give it its value"

    return None


def _assembly(line: str) -> str | None:
    """x86-64, Intel syntax, NASM — the dialect the theme is written in.

    Assembly is where the "never assert what the line does not say"
    rule earns its keep, because the meaning of an instruction depends
    on state the line cannot see. `jne .loop` jumps when the last
    comparison came out unequal, and which comparison that was is not
    in this line. So the flag-readers describe the test they perform,
    never the value they are testing, and nothing here claims to know
    what is in a register.

    Two-operand arithmetic reads destination-first, per Intel syntax.
    An AT&T-syntax line would be described backwards by these rules,
    which is exactly why the theme is one dialect and says so.
    """
    s = line.strip()
    if s.startswith(";"):
        return None

    # A label is a name for an address, and the colon is the whole tell.
    m = re.match(r"^(\.?[\w$]+):$", s)
    if m:
        return f"somewhere to jump to, named {m.group(1)}"

    m = re.match(r"^(\w+)\s+(.+)$", s)
    op = m.group(1).lower() if m else s.lower()
    rest = m.group(2).strip() if m else ""
    pair = [part.strip() for part in rest.split(",")] if rest else []
    first = pair[0] if pair else ""
    second = pair[1] if len(pair) > 1 else ""

    # Moves. The zero idioms are worth naming as themselves, because
    # that is how they are read by anyone who knows the language.
    if op in {"xor", "sub"} and first and first == second:
        return f"set {first} to zero, the short way"
    if op == "mov" and second:
        return f"put {second} into {first}"
    if op in {"movzx", "movsx"} and second:
        return f"put {second} into {first}, widened to fit"
    if op == "lea" and second:
        return f"work out the address {second} and put it in {first}"

    two_operand = {
        "add": "add {b} to {a}",
        "sub": "take {b} off {a}",
        "and": "keep in {a} only the bits also set in {b}",
        "or": "set in {a} every bit set in {b}",
        "xor": "flip in {a} the bits set in {b}",
        "imul": "multiply {a} by {b}, signed",
        "shl": "shift {a} left by {b}",
        "shr": "shift {a} right by {b}",
        "sar": "shift {a} right by {b}, keeping the sign",
    }
    if op in two_operand and second:
        return two_operand[op].format(a=first, b=second)

    one_operand = {
        "inc": "add one to {a}",
        "dec": "take one off {a}",
        "neg": "flip the sign of {a}",
        "not": "flip every bit of {a}",
        "push": "save {a} on the stack",
        "pop": "take the top of the stack back into {a}",
        "idiv": "divide by {a}, signed",
        "div": "divide by {a}, unsigned",
    }
    if op in one_operand and first and not second:
        return one_operand[op].format(a=first)

    # Comparisons set flags and produce nothing. Saying they "check
    # whether x equals y" would be asserting the outcome; they perform
    # the test and leave the answer in the flags.
    if op == "cmp" and second:
        return f"compare {first} with {second}, leaving the answer in the flags"
    if op == "test" and second:
        return f"test the bits of {first} against {second}, setting the flags"

    jumps = {
        "jmp": "go to {a}, no test",
        "je": "go to {a} if the last comparison was equal",
        "jz": "go to {a} if the zero flag is set",
        "jne": "go to {a} if the last comparison was not equal",
        "jnz": "go to {a} if the zero flag is clear",
        "jl": "go to {a} if it was less",
        "jle": "go to {a} if it was less or equal",
        "jg": "go to {a} if it was greater",
        "jge": "go to {a} if it was greater or equal",
        "loop": "count down and go to {a} until the counter runs out",
    }
    if op in jumps and first:
        return jumps[op].format(a=first)

    if op == "call" and first:
        return f"save where we are and go to {first}"
    if op == "ret":
        return "go back to whoever called, popping the address"
    if op == "syscall":
        return "hand over to the kernel"
    if op == "int" and first:
        return f"hand over to the kernel, the older way, through {first}"
    if op == "leave":
        return "undo the stack frame in one instruction"
    if op == "nop":
        return "do nothing, deliberately"
    if op == "cqo":
        return "widen the sign across, which the signed divide needs first"

    # Directives, which are instructions to the assembler rather than
    # to the processor. Worth distinguishing: they never run.
    if op == "section" and first:
        return f"everything after this goes in the {first} section"
    if op in {"global", "extern"} and first:
        return (
            f"let the linker see {first}"
            if op == "global"
            else f"{first} is defined somewhere else"
        )
    if op in {"db", "dw", "dd", "dq"} and rest:
        return f"lay down {rest} in the program's own bytes"
    if op in {"resb", "resw", "resd", "resq"} and rest:
        return f"reserve room for {rest}, filled in at run time"
    if op == "align" and first:
        return f"pad until the address divides by {first}"

    return None


#: Which describer to use. Dialects that are close enough to share one
#: are listed against it rather than given a near-copy, because a
#: near-copy is the thing that goes stale.
_BY_LANGUAGE = {
    "python": _python,
    "javascript": _javascript,
    "typescript": _javascript,
    "assembly": _assembly,
}


def describe(line: str, language: str) -> str | None:
    """What this line does, or None when there is nothing safe to say.

    None is a real answer and the common one for languages this module
    has no rules for. The caller falls back to whatever note it already
    had.
    """
    if not line or _NOT_WORTH_SAYING.match(line):
        return None
    if "\n" in line:
        return None
    describer = _BY_LANGUAGE.get(language)
    if describer is None:
        return None
    try:
        return describer(line)
    except re.error:  # pragma: no cover - a rule would have to be broken
        return None


def note_for(line: str, language: str, source: str) -> str:
    """The note to show under a line: what it does, and where it is from.

    Both, not one: the description says what the line in front of you is
    doing, and the source says which solution you are part-way through.
    Losing the second would make a long solution feel like a shuffle of
    unrelated lines.
    """
    described = describe(line, language)
    if not described:
        return source
    if not source:
        return described
    return f"{described} · {source}"
