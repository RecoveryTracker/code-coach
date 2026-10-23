"""Flutter widgets pack, activity 4: Type It.

A TextField sits in `MaterialApp(home: Material(child: ...))` (text fields need a Material ancestor and
MaterialLocalizations). The comment says what the test types - `tester.enterText(finder, 'abc')`, which REPLACES the
whole text, once per call - and asks for what the field holds afterwards (as digits or a length), how often a callback
ran, which of several fields got the text, or how many Text widgets the decoration built.

Rules the model implements (each held to real Flutter by the oracle):
* maxLength cuts the typed text; a change that leaves the text as it was does not call onChanged;
* readOnly and disabled fields ignore typing; a single-line field drops newlines; maxLines 3 or null keeps them;
* after a `done`/`go`/`search`/`send` action a single-line field loses focus, so later actions do nothing - unless
  onEditingComplete is given, which replaces that default; a `newline` action on a multi-line field does nothing;
* testTextInput.enterText goes to the focused field: the autofocus one, then whichever enabled field was tapped last;
* every piece of an InputDecoration (hint, label, helper, prefix, suffix, counter) is a Text in the tree, typing or not;
  an errorText replaces the helperText; `counterText: ''` removes the counter.
"""

from __future__ import annotations

import random

from ._flutterwidgets_kit import G, col, mk, template

TEMPLATES: list = []

EDT = "tester.widget<EditableText>(find.byType(EditableText)).controller.text"
ALL_EDT = "tester.widgetList<EditableText>(find.byType(EditableText))"
HIT = "int n = 0;\nvoid hit([String? v]) {\n  n++;\n}"
ADD = "int total = 0;\nvoid add(String v) {\n  total += v.length;\n}"


SHORT = {"hintText": "a", "labelText": "b", "helperText": "c", "prefixText": "d", "suffixText": "e", "errorText": "f"}
ASK_IDX = "field index (from 0) holding 'hi' after testTextInput.enterText"


def app(child) -> G:
    return G("MaterialApp", home=G("Material", child=child))


def dq(s: str) -> str:
    """A Dart single-quoted literal for s, newlines written as \\n."""
    return "'" + s.replace("\\", "\\\\").replace("\n", "\\n").replace("'", "\\'") + "'"


def digits(rng: random.Random, n: int) -> str:
    return "".join(str(rng.randint(1, 9)) for _ in range(n))


def letters(rng: random.Random, n: int) -> str:
    return "".join(rng.choice("abcdefgh") for _ in range(n))


def enter_lines(texts: list[str], finder: str = "find.byType(TextField)") -> str:
    return "\n".join(f"await tester.enterText({finder}, {dq(t)});" for t in texts)


def typed(texts: list[str]) -> str:
    return ", ".join(f"enterText({dq(t)})" for t in texts)


def field(rng: random.Random, **kw) -> G:
    return G("TextField", **kw)


def cut(t: str, m: int | None) -> str:
    return t if m is None else t[:m]


def type_in(old: str, new: str, m: int | None) -> str:
    """What a maxLength field holds after enterText(new): too long is cut - unless the field is ALREADY full, then the
    whole edit is refused and the old text stays (LengthLimitingTextInputFormatter)."""
    if m is not None and len(new) > m:
        return old if len(old) == m else new[:m]
    return new


# ── what a field holds afterwards ───────────────────────────────────────

@template(TEMPLATES)
def max_length_cuts_digits(rng):
    m = rng.randint(2, 5)
    t = digits(rng, rng.randint(m + 1, 8))
    ans = cut(t, m)
    w = app(field(rng, maxLength=str(m)))
    return mk(f"text after {typed([t])}", w, ans, f"maxLength: {m} stops the field at {m} characters: {t} is cut to {ans}.",
              enter_lines([t]) + f"\nreturn {EDT};")


@template(TEMPLATES)
def max_length_or_not_length(rng):
    m = rng.choice((None, 3, 4, 5, 6))
    t = letters(rng, rng.randint(2, 9))
    decoy = rng.choice(("", "obscureText: true", "keyboardType: TextInputType.number", "autocorrect: false", "textAlign: TextAlign.end",
                        "textCapitalization: TextCapitalization.characters"))
    kw: dict = {}
    if decoy:
        k, v = decoy.split(": ", 1)
        kw[k] = v
    if m is not None:
        kw["maxLength"] = str(m)
    ans = len(cut(t, m))
    why = (f"maxLength {m} cuts {len(t)} characters to {ans}" if m is not None and len(t) > m else "nothing limits the text, so every typed character stays")
    if decoy:
        why += f"; {decoy.split(':')[0]} only changes how the field looks or which keyboard shows"
    return mk(f"length of the text after {typed([t])}", app(field(rng, **kw)), ans, why + f": {ans}.", enter_lines([t]) + f"\nreturn {EDT}.length;")


@template(TEMPLATES)
def enter_text_replaces(rng):
    k = rng.randint(2, 3)
    texts = [digits(rng, rng.randint(1, 5)) for _ in range(k)]
    m = rng.choice((None, None, 3))
    kw = {"maxLength": str(m)} if m else {}
    cur, notes = "", []
    for t in texts:
        new = type_in(cur, t, m)
        if m and len(t) > m:
            notes.append(f"{t} is too long: " + (f"the field is already full ({cur}), so the whole edit is refused" if len(cur) == m else f"cut to {new}"))
        cur = new
    return mk(f"text after {typed(texts)}", app(field(rng, **kw)), cur, "Each enterText replaces everything in the field"
              + (f" (maxLength {m}: " + "; ".join(notes) + ")" if notes else "") + f". Final text: {cur}.",
              enter_lines(texts) + f"\nreturn {EDT};")


@template(TEMPLATES)
def full_field_refuses_longer_text(rng):
    m = rng.randint(2, 4)
    init = digits(rng, m)
    t = digits(rng, rng.randint(m + 1, m + 3))
    shorter = digits(rng, rng.randint(1, m))
    second = rng.choice((t, shorter))
    cur = type_in(init, second, m)
    w = app(G("TextFormField", initialValue=f"'{init}'", maxLength=str(m)))
    return mk(f"text after {typed([second])}", w, cur, f"The field starts full ({m} characters). "
              + (f"{second} is longer than {m} and the field is already full, so Flutter refuses the edit and keeps {init}" if second == t
                 else f"{second} fits within {m}, so it replaces {init}") + f": {cur}.",
              enter_lines([second], "find.byType(TextFormField)") + f"\nreturn {EDT};")


@template(TEMPLATES)
def initial_text_then_typing(rng):
    init = letters(rng, rng.randint(2, 5))
    t = rng.choice([letters(rng, rng.randint(1, 6)), ""])
    w = app(field(rng, controller=f"TextEditingController(text: '{init}')"))
    ans = len(t)
    return mk(f"length of the text after {typed([t])}, the controller started with '{init}'", w, ans,
              f"The controller's starting text '{init}' is replaced, not extended: the field now holds {ans} characters.",
              enter_lines([t]) + f"\nreturn {EDT}.length;")


@template(TEMPLATES)
def ignores_typing(rng):
    kind = rng.choice(("readOnly: true", "enabled: false", "none"))
    init = rng.choice(("", "", "ab", "xyz"))
    t = letters(rng, rng.randint(3, 6))
    kw: dict = {}
    if kind != "none":
        k, v = kind.split(": ")
        kw[k] = v
    if init:
        kw["controller"] = f"TextEditingController(text: '{init}')"
    ans = len(init) if kind != "none" else len(t)
    why = (f"A {'read-only' if kind.startswith('readOnly') else 'disabled'} field does not take typed input, so it keeps its {len(init)} characters"
           if kind != "none" else "An ordinary field takes the typed text and drops the old one")
    return mk(f"length of the text after {typed([t])}", app(field(rng, **kw)), ans, why + f": {ans}.", enter_lines([t]) + f"\nreturn {EDT}.length;")


@template(TEMPLATES)
def newline_handling(rng):
    a, b = letters(rng, rng.randint(1, 3)), letters(rng, rng.randint(1, 3))
    t = a + "\n" + b
    lines = rng.choice(("none", "1", "3", "null"))
    kw = {} if lines == "none" else {"maxLines": lines}
    multi = lines in ("3", "null")
    ans = len(t) if multi else len(a + b)
    return mk(f"length of the text after {typed([t])}", app(field(rng, **kw)), ans,
              ("A multi-line field keeps the line break as a character" if multi else "A single-line field (maxLines 1 is the default) removes line breaks")
              + f": {ans}.", enter_lines([t]) + f"\nreturn {EDT}.length;")


@template(TEMPLATES)
def selection_after_typing(rng):
    m = rng.choice((None, 3, 4))
    t = letters(rng, rng.randint(2, 7))
    kw = {"maxLength": str(m)} if m else {}
    ans = len(cut(t, m))
    return mk(f"cursor position (selection.baseOffset) after {typed([t])}", app(field(rng, **kw)), ans, "After enterText the cursor sits at the end of the text"
              + (f" (cut to {m})" if m and len(t) > m else "") + f": {ans}.",
              enter_lines([t]) + "\nreturn tester.widget<EditableText>(find.byType(EditableText)).controller.selection.baseOffset;")


@template(TEMPLATES)
def selected_text_length(rng):
    text = rng.choice(("flutter", "keyboard", "widgets", "abcdefgh"))
    base, ext = rng.sample(range(0, len(text) + 1), 2)
    form = rng.choice(("range", "collapsed"))
    if form == "collapsed":
        sel, ans, why = f"TextSelection.collapsed(offset: {base})", 0, "A collapsed selection is just a cursor: nothing is selected"
    else:
        sel, ans, why = (f"TextSelection(baseOffset: {base}, extentOffset: {ext})", abs(ext - base),
                         f"The selection covers the characters between offsets {min(base, ext)} and {max(base, ext)}, whichever end the drag started")
    w = app(field(rng, controller=f"TextEditingController(text: '{text}')..selection = {sel}"))
    return mk("how many characters are selected", w, ans, why + f": {ans}.",
              "final c = tester.widget<EditableText>(find.byType(EditableText)).controller;\nreturn c.selection.textInside(c.text).length;")


# ── callbacks ───────────────────────────────────────────────────────────

@template(TEMPLATES)
def changed_call_count(rng):
    init = rng.choice(("", "", "ab"))
    pool = ["a", "ab", "abc", "", "ab", "b"]
    seq = [rng.choice(pool) for _ in range(rng.randint(3, 4))]
    m = rng.choice((None, None, 2))
    kw: dict = {"onChanged": "hit"}
    if m:
        kw["maxLength"] = str(m)
    if init:
        kw["controller"] = f"TextEditingController(text: '{init}')"
    prev, n = init, 0
    for t in seq:
        now = type_in(prev, t, m)
        if now != prev:
            n += 1
        prev = now
    return mk(f"hit calls after {typed(seq)}", app(field(rng, **kw)), n, "onChanged runs only when the text really changes"
              + (f" (after maxLength {m} cuts it)" if m else "") + (f"; the field started with '{init}'" if init else "") + f": {n} calls.",
              enter_lines(seq) + "\nreturn n;", decls=HIT)


@template(TEMPLATES)
def changed_total_length(rng):
    seq = [rng.choice(["ab", "abc", "ab", "a", "abcd"]) for _ in range(rng.randint(3, 4))]
    prev, total = "", 0
    for t in seq:
        if t != prev:
            total += len(t)
        prev = t
    return mk(f"total after {typed(seq)}", app(field(rng, onChanged="add")), total, "add receives the new text on every real change and adds its length; "
              f"a repeat of the same text is not a change: {total}.", enter_lines(seq) + "\nreturn total;", decls=ADD)


@template(TEMPLATES)
def submitted_length(rng):
    m = rng.choice((None, 3, 4))
    t = letters(rng, rng.randint(2, 6))
    action = rng.choice(("done", "go", "search", "send"))
    kw: dict = {"onSubmitted": "add"}
    if m:
        kw["maxLength"] = str(m)
    ans = len(cut(t, m))
    return mk(f"total after {typed([t])} and one {action} action", app(field(rng, **kw)), ans, f"onSubmitted gets the text of the field when the {action} "
              "action arrives" + (f", already cut to {m}" if m and len(t) > m else "") + f": add records {ans}.",
              enter_lines([t]) + f"\nawait tester.testTextInput.receiveAction(TextInputAction.{action});\nawait tester.pump();\nreturn total;", decls=ADD)


@template(TEMPLATES)
def actions_and_focus(rng):
    handler = rng.choice(("onSubmitted", "onEditingComplete", "both"))
    multi = rng.random() < 0.4
    kw: dict = {}
    if handler in ("onSubmitted", "both"):
        kw["onSubmitted"] = "hit"
    if handler in ("onEditingComplete", "both"):
        kw["onEditingComplete"] = "hit"
    if multi:
        kw["maxLines"] = "null"
    acts = [rng.choice(("done", "done", "newline", "go")) for _ in range(rng.randint(2, 3))]
    focused, n = True, 0
    for a in acts:
        if not focused:
            continue
        if a == "newline" and multi:
            continue
        if "onEditingComplete" in kw:
            n += 1
        else:
            focused = False
        if "onSubmitted" in kw:
            n += 1
    lines = "\n".join(f"await tester.testTextInput.receiveAction(TextInputAction.{a});" for a in acts)
    return mk("hit calls after " + ", ".join(acts), app(field(rng, **kw)), n,
              "A done, go or newline action finishes editing: it calls the handlers, then (unless onEditingComplete took over) the field loses focus "
              f"and later actions go nowhere; on a multi-line field a newline action just adds a line. Total: {n}.", "await tester.enterText(find.byType(TextField), 'x');\n" + lines + "\nawait tester.pump();\nreturn n;", decls=HIT)


# ── which field? ────────────────────────────────────────────────────────

@template(TEMPLATES)
def two_fields_lengths(rng):
    t = letters(rng, rng.randint(4, 7))
    ms = [rng.choice((None, 2, 3)) for _ in range(rng.randint(2, 3))]
    fields = [field(rng, maxLength=str(m)) if m else field(rng) for m in ms]
    ans = "".join(str(len(cut(t, m))) for m in ms)
    lines = "\n".join(f"await tester.enterText(find.byType(TextField).at({i}), {dq(t)});" for i in range(len(ms)))
    return mk(f"the lengths of the fields, joined, after typing {dq(t)} into each", app(col(*fields)), ans,
              "Each field is limited only by its own maxLength: " + ", ".join(str(len(cut(t, m))) for m in ms) + ".",
              lines + f"\nreturn {ALL_EDT}.map((e) => e.controller.text.length).join();")


@template(TEMPLATES)
def total_in_all_fields(rng):
    k = rng.randint(2, 3)
    ts = [letters(rng, rng.randint(1, 4)) for _ in range(k)]
    ms = [rng.choice((None, 2)) for _ in range(k)]
    fields = [field(rng, maxLength=str(m)) if m else field(rng) for m in ms]
    ans = sum(len(cut(t, m)) for t, m in zip(ts, ms))
    lines = "\n".join(f"await tester.enterText(find.byType(TextField).at({i}), {dq(t)});" for i, t in enumerate(ts))
    return mk("characters in all the fields together after typing " + ", ".join(f"{dq(t)}" for t in ts), app(col(*fields)), ans,
              "Add up what each field really holds (maxLength 2 cuts to 2): " + " + ".join(str(len(cut(t, m))) for t, m in zip(ts, ms)) + f" = {ans}.",
              lines + f"\nreturn {ALL_EDT}.fold<int>(0, (s, e) => s + e.controller.text.length);")


@template(TEMPLATES)
def autofocus_gets_the_text(rng):
    k = rng.randint(2, 3)
    which = rng.randrange(k)
    fields = [field(rng, autofocus="true") if i == which else field(rng) for i in range(k)]
    return mk(ASK_IDX, app(col(*fields)), which,
              f"testTextInput types into the focused field, and the only autofocus is the field at index {which}: {which}.",
              "await tester.pump();\ntester.testTextInput.enterText('hi');\nawait tester.pump();\n"
              f"return {ALL_EDT}.toList().indexWhere((e) => e.controller.text.isNotEmpty);")


@template(TEMPLATES)
def two_autofocus(rng):
    k = rng.randint(3, 4)
    flags = sorted(rng.sample(range(k), 2))
    fields = [field(rng, autofocus="true") if i in flags else field(rng) for i in range(k)]
    which = flags[0]
    return mk(ASK_IDX, app(col(*fields)), which,
              f"Two fields ask for autofocus (indexes {flags[0]} and {flags[1]}); the first one wins the focus: {which}.",
              "await tester.pump();\ntester.testTextInput.enterText('hi');\nawait tester.pump();\n"
              f"return {ALL_EDT}.toList().indexWhere((e) => e.controller.text.isNotEmpty);")


@template(TEMPLATES)
def tap_moves_focus(rng):
    k = rng.randint(3, 4)
    start = rng.randrange(k)
    disabled = rng.sample([i for i in range(k) if i != start], rng.randint(0, 1))
    fields = []
    for i in range(k):
        kw: dict = {}
        if i == start:
            kw["autofocus"] = "true"
        if i in disabled:
            kw["enabled"] = "false"
        fields.append(field(rng, **kw))
    taps = [rng.randrange(k) for _ in range(rng.randint(1, 2))]
    focus = start
    for t in taps:
        if t not in disabled:
            focus = t
    lines = "\n".join(f"await tester.tap(find.byType(TextField).at({t}), warnIfMissed: false);\nawait tester.pump();" for t in taps)
    return mk(ASK_IDX + ", after tapping fields " + ", ".join(map(str, taps)),
              app(col(*fields)), focus, "Tapping an enabled field moves the focus there; tapping a disabled one does nothing, so the focus stays where it was: "
              f"{focus}.", "await tester.pump();\n" + lines + "\ntester.testTextInput.enterText('hi');\nawait tester.pump();\n"
              f"return {ALL_EDT}.toList().indexWhere((e) => e.controller.text.isNotEmpty);")


# ── the decoration around the field ─────────────────────────────────────

@template(TEMPLATES)
def decoration_text_count(rng):
    pieces = rng.sample(["hintText", "labelText", "helperText", "prefixText", "suffixText", "errorText"], rng.randint(2, 4))
    kw = {p: dq(SHORT[p]) for p in pieces}
    n = len(pieces) - (1 if "helperText" in pieces and "errorText" in pieces else 0)
    m = rng.choice((None, None, 5))
    kwf: dict = {"decoration": G("InputDecoration", **kw)}
    if m:
        kwf["maxLength"] = str(m)
        n += 1
    typed_first = rng.random() < 0.5
    why = f"{len(pieces)} pieces of the decoration are Texts"
    if "helperText" in pieces and "errorText" in pieces:
        why += ", but an errorText takes the place of the helperText"
    if m:
        why += "; maxLength adds a counter such as 0/5"
    why += f"; typing does not remove any (the hint only fades out): {n}."
    pre = "await tester.enterText(find.byType(TextField), 'ab');\n" if typed_first else ""
    return mk("find.byType(Text) matches how many" + (" after typing?" if typed_first else "?"), app(field(rng, **kwf)), n, why,
              pre + "await tester.pumpAndSettle();\nreturn count(find.byType(Text));")


@template(TEMPLATES)
def counter_text(rng):
    m = rng.choice((3, 5, 8))
    t = letters(rng, rng.randint(1, 10))
    shown = min(len(t), m)
    guess = rng.choice([shown, shown, min(len(t), m) + rng.choice((-1, 1)), len(t)])
    if guess < 0:
        guess = 0
    want = f"{guess}/{m}"
    ans = 1 if guess == shown else 0
    return mk(f"find.text('{want}') matches how many, after {typed([t])}?", app(field(rng, maxLength=str(m))), ans,
              f"The counter shows how many characters the field really holds out of {m}: '{shown}/{m}'" + (f" ({len(t)} typed, cut to {m})" if len(t) > m else "")
              + f". '{want}' {'is' if ans else 'is not'} that: {ans}.", enter_lines([t]) + f"\nawait tester.pump();\nreturn count(find.text('{want}'));")


@template(TEMPLATES)
def hint_and_label_stay(rng):
    kind = rng.choice(("hintText", "labelText", "prefixText", "suffixText"))
    typed_now = rng.random() < 0.7
    w = app(field(rng, decoration=G("InputDecoration", **{kind: "'x'"})))
    return mk(f"find.text('x') matches how many{' after ' + typed(['abc']) if typed_now else ''}?", w, 1,
              f"{kind} builds a Text and keeps it in the tree for as long as the field lives" + (" - the hint just fades to invisible once there is text" if kind == "hintText" else "")
              + ": 1.", (enter_lines(["abc"]) + "\nawait tester.pumpAndSettle();\n" if typed_now else "") + "return count(find.text('x'));")


@template(TEMPLATES)
def form_field_text(rng):
    init = digits(rng, rng.randint(1, 3))
    t = digits(rng, rng.randint(2, 6))
    m = rng.choice((None, 3, 4))
    kw = {"initialValue": f"'{init}'"}
    if m:
        kw["maxLength"] = str(m)
    ans = type_in(init, t, m)
    return mk(f"text after {typed([t])}", app(G("TextFormField", **kw)), ans,
              f"enterText replaces the initialValue '{init}'" + (f" and maxLength {m} cuts the new text" if m and len(t) > m and len(init) != m else "")
              + (f" - but the field is already full, so the longer text is refused and {init} stays" if m and len(t) > m and len(init) == m else "") + f": {ans}.",
              enter_lines([t], "find.byType(TextFormField)") + f"\nreturn {EDT};")


@template(TEMPLATES)
def same_text_again(rng):
    init = letters(rng, 2)
    t = rng.choice([init, init, letters(rng, 3)])
    ans = 0 if t == init else 1
    return mk(f"hit calls after {typed([t])}",
              app(field(rng, controller=f"TextEditingController(text: '{init}')", onChanged="hit")), ans,
              "onChanged is only called when the text changes; " + ("typing exactly what is already there changes nothing" if ans == 0 else "this is new text") + f": {ans}.",
              enter_lines([t]) + "\nreturn n;", decls=HIT)


@template(TEMPLATES)
def changed_total_with_limit(rng):
    m = rng.randint(2, 4)
    seq = [digits(rng, rng.randint(1, m + 2)) for _ in range(rng.randint(2, 3))]
    cur, total = "", 0
    for t in seq:
        new = type_in(cur, t, m)
        if new != cur:
            total += len(new)
        cur = new
    return mk(f"total after {typed(seq)}", app(field(rng, maxLength=str(m), onChanged="add")), total,
              f"add gets the text AFTER maxLength {m} has been applied, and only on a real change; a full field refuses a longer edit. Total: {total}.",
              enter_lines(seq) + "\nreturn total;", decls=ADD)


@template(TEMPLATES)
def submitted_after_two_entries(rng):
    m = rng.choice((None, 3))
    seq = [letters(rng, rng.randint(1, 5)) for _ in range(2)]
    cur = ""
    for t in seq:
        cur = type_in(cur, t, m)
    kw: dict = {"onSubmitted": "add"}
    if m:
        kw["maxLength"] = str(m)
    return mk(f"total after {typed(seq)} and one done action", app(field(rng, **kw)), len(cur),
              f"onSubmitted is told the field's text at that moment, which is the last accepted text '{cur}': {len(cur)}.",
              enter_lines(seq) + "\nawait tester.testTextInput.receiveAction(TextInputAction.done);\nawait tester.pump();\nreturn total;", decls=ADD)


@template(TEMPLATES)
def controller_edits(rng):
    base = letters(rng, rng.randint(2, 4))
    new = letters(rng, rng.randint(1, 6))
    forms = [
        (f"TextEditingController(text: '{base}')..text = '{new}'", len(new), "the cascade assigns the new text after the constructor"),
        (f"TextEditingController(text: '{base}')..clear()", 0, "clear() empties the controller"),
        (f"TextEditingController(text: '{base}')..text = ''", 0, "assigning an empty string empties it"),
        (f"TextEditingController.fromValue(TextEditingValue(text: '{new}'))", len(new), "fromValue starts with the given value"),
        (f"TextEditingController(text: '{base}')..value = TextEditingValue(text: '{new}')", len(new), "assigning value replaces the text"),
        (f"TextEditingController(text: '{base}')", len(base), "nothing changed it"),
    ]
    code, ans, why = rng.choice(forms)
    return mk("how many characters the field holds", app(field(rng, controller=code)), ans, f"{why[0].upper() + why[1:]}: {ans}.",
              f"return {EDT}.length;")
