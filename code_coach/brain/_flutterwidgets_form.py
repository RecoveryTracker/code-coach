"""Flutter widgets pack, activity 8: Form Check.

A Form with TextFormFields in `MaterialApp(home: Material(child: ...))`, each validator returning 'x' when the value is
bad. The comment says what the test does (types into fields, calls validate(), save() or reset()) and asks how many
error texts are on screen (`count(find.text('x'))`), whether validate() returned true, or what onSaved collected.

The model keeps, per field, its value and whether an error is showing, and applies Flutter's rules:
* validate() checks EVERY field of the Form and shows or clears each one's error; it returns true only if all are valid;
* with the default autovalidateMode (disabled) errors appear only when validate() runs, and typing a fix does not remove
  one until the next validate();
* Form(autovalidateMode: always) shows the errors of the current values all the time; onUserInteraction waits for the
  user to type, and then validates EVERY field of that Form, not just the one typed into;
* a field's own autovalidateMode only concerns that field;
* save() calls every onSaved with the current text, valid or not, and never validates; reset() puts the initial values
  back and clears the errors;
* a TextFormField's validator gets '' (not null) for an empty field; maxLength has already cut the text;
* fields of a nested Form belong to the inner Form; a field that is not in the tree (an invisible Visibility, a list
  item that was never built) is not validated, an Offstage one still is.
"""

from __future__ import annotations

import random

from ._flutter_model import fit
from ._flutterwidgets_kit import G, q, template
from ._flutterwidgets_kit import mk as _mk
from .items import Item

TEMPLATES: list = []


def mk(*args, **kw):
    """Items of this activity print their widget on as few lines as possible: the wrappers are long."""
    kw.setdefault("width", 220)
    return _mk(*args, **kw)

FORM = "tester.state<FormState>(find.byType(Form))"
ERRORS = "count(find.text('x'))"
SAVE_DECL = "int n = 0;\nvoid add(String? v) {\n  n += v!.length;\n}"


def dart_try_parse(s: str) -> bool:
    """int.tryParse(s) != null for plain decimal text: spaces around it are ignored, then an optional sign and digits."""
    s = s.strip()
    body = s[1:] if s[:1] in "+-" else s
    return body != "" and all(c in "0123456789" for c in body)


#: (Dart closure, python predicate "is this value BAD?", what it checks)
VALIDATORS = [
    ("(v) => v == '' ? 'x' : null", lambda s: s == "", "empty"),
    ("(v) => v!.length < 3 ? 'x' : null", lambda s: len(s) < 3, "shorter than 3"),
    ("(v) => v!.length > 3 ? 'x' : null", lambda s: len(s) > 3, "longer than 3"),
    ("(v) => v!.contains('@') ? null : 'x'", lambda s: "@" not in s, "has no @"),
    ("(v) => int.tryParse(v!) == null ? 'x' : null", lambda s: not dart_try_parse(s), "not a whole number"),
    ("(v) => v!.trim() == '' ? 'x' : null", lambda s: s.strip() == "", "blank"),
    ("(v) => 'x'", lambda s: True, "always complains"),
]
#: the validators whose closure is short enough for two fields in one prompt
SHORT = [0, 1, 2, 5]
MODE_NAMES = {"always": "always", "interaction": "onUserInteraction"}
VALUES = ["", "ab", "abc", "abcd", "a@b", "12", "-7", "1.5", " ", "x1", "4096"]


def app(child) -> G:
    return G("MaterialApp", home=G("Material", child=child))


def field(v_idx: int, **kw) -> G:
    return G("TextFormField", **kw, validator=VALIDATORS[v_idx][0])


def form_of(fields: list[G], **kw) -> G:
    if len(fields) == 1:
        return G("Form", **kw, child=fields[0])
    return G("Form", **kw, child=G("Column", children=fields))


def op_code(op: tuple) -> str:
    kind = op[0]
    if kind == "type":
        return f"await tester.enterText(find.byType(TextFormField).at({op[1]}), {q(op[2])});\nawait tester.pump();"
    if kind == "validate":
        return f"{FORM}.validate();\nawait tester.pump();"
    if kind == "reset":
        return f"{FORM}.reset();\nawait tester.pump();"
    return f"{FORM}.save();"


def op_words(op: tuple, single: bool = False) -> str:
    if op[0] == "type":
        return f"typing {q(op[2])}" if single else f"typing {q(op[2])} in field {op[1]}"
    return {"validate": "validate()", "reset": "reset()", "save": "save()"}[op[0]]


class Model:
    """The values and shown errors of a Form of fields without initial values."""

    def __init__(self, validators: list[int], mode: str = "disabled") -> None:
        self.v = validators
        self.mode = mode
        self.values = [""] * len(validators)
        self.flag = [False] * len(validators)
        self.saved = 0

    def bad(self, i: int) -> bool:
        if self.v[i] is None:
            return False
        return VALIDATORS[self.v[i]][1](self.values[i])

    def validate_all(self) -> None:
        self.flag = [self.bad(i) for i in range(len(self.v))]

    def apply(self, op: tuple) -> None:
        kind = op[0]
        if kind == "type":
            self.values[op[1]] = op[2]
            if self.mode == "interaction":
                self.validate_all()
        elif kind == "validate":
            self.validate_all()
        elif kind == "reset":
            self.values = [""] * len(self.v)
            self.flag = [False] * len(self.v)
        else:
            self.saved += sum(len(x) for x in self.values)

    def shown(self) -> int:
        if self.mode == "always":
            return sum(1 for i in range(len(self.v)) if self.bad(i))
        return sum(self.flag)

    def valid(self) -> bool:
        return not any(self.bad(i) for i in range(len(self.v)))


def random_ops(rng: random.Random, m: Model, kinds: tuple[str, ...], count: int) -> list[tuple]:
    ops: list[tuple] = []
    for _ in range(count):
        kind = rng.choice(kinds)
        if kind == "type":
            i = rng.randrange(len(m.v))
            t = rng.choice([x for x in VALUES if x != m.values[i] and len(x) <= 3])
            op = ("type", i, t)
        else:
            op = (kind,)
        m.apply(op)
        ops.append(op)
    return ops


def machine(kinds: tuple[str, ...], mode: str, final: str, fields: int = 2, count: tuple[int, int] = (2, 2), show_validators: bool = True,
            plain_first: bool = False):
    """A template: a Form of `fields` empty fields in `mode`, a few random actions, and a question about the end.

    With plain_first the first field has no validator at all (it keeps the prompt short, and shows that typing in one field
    makes an onUserInteraction Form check the others)."""
    def make(rng: random.Random) -> Item:
        pool = ([6] if plain_first else SHORT) if fields > 1 else list(range(len(VALIDATORS)))
        vs: list[int | None] = [rng.choice(pool) for _ in range(fields)]
        if plain_first:
            vs[0] = None
        m = Model(vs, mode)
        ops = random_ops(rng, m, kinds, rng.randint(*count))
        kw = {} if mode == "disabled" else {"autovalidateMode": f"AutovalidateMode.{MODE_NAMES[mode]}"}
        fs = []
        for v in vs:
            fkw: dict = {}
            if v is not None and show_validators:
                fkw["validator"] = VALIDATORS[v][0]
            if final == "saved":
                fkw["onSaved"] = "add"
            fs.append(G("TextFormField", **fkw))
        w = app(form_of(fs, **kw))
        steps = ", ".join(op_words(o, fields == 1) for o in ops)
        body = "\n".join(op_code(o) for o in ops)
        if final == "errors":
            ask, ans = "errors, " + steps, m.shown()
            check = body + "\nawait tester.pumpAndSettle();\nreturn " + ERRORS + ";"
        elif final == "ok":
            ans = 1 if m.valid() else 0
            ask = "validate() as 1 or 0 after " + steps
            check = body + f"\nreturn {FORM}.validate() ? 1 : 0;"
        else:
            ans = m.saved + sum(len(x) for x in m.values)
            ask = "total after " + steps + ", save()"
            check = body + f"\n{FORM}.save();\nreturn n;"
        checks = [f"field {i} ({'no validator' if v is None or not show_validators else VALIDATORS[v][2] + ' is bad'}) holds {q(m.values[i])}" for i, v in enumerate(vs)]
        why = "; ".join(checks) + ". "
        if final == "errors":
            if mode == "always":
                why += "With autovalidateMode.always every field shows its error for its current value, all the time"
            elif mode == "interaction":
                why += "With onUserInteraction, typing into ANY field validates every field of the Form (validate() does too); reset() clears the errors"
            else:
                why += "Errors appear only when validate() runs; typing a fix leaves an old error showing until the next validate(); reset() clears them"
            why += f": {ans} showing."
        elif final == "ok":
            why += "validate() runs every validator on the current text and is true only if none complains: " + str(ans) + "."
        else:
            why += ("save() sends every field's current text to onSaved, valid or not: the total is the sum of the lengths "
                    "(earlier save() calls add up too): " + str(ans) + ".")
        return mk(ask, w, ans, why, check, decls=SAVE_DECL if final == "saved" else "")
    return make


def register(name: str, kinds: tuple[str, ...], mode: str, final: str, fields: int = 2, count: tuple[int, int] = (2, 2), show_validators: bool = True,
             plain_first: bool = False) -> None:
    fn = machine(kinds, mode, final, fields, count, show_validators, plain_first)
    fn.__name__ = name
    TEMPLATES.append(fit(fn, whole=False))


register("validate_counts_errors", ("type", "validate"), "disabled", "errors", 1, (2, 3))
register("validate_then_fix_stays", ("type", "validate", "type"), "disabled", "errors", 1, (3, 3))
register("validate_reset_errors", ("type", "validate", "reset"), "disabled", "errors", 1, (3, 3))
register("validate_counts_two_fields", ("validate",), "disabled", "errors", 2, (1, 1))
register("interaction_validates_all", ("type", "reset"), "interaction", "errors", 2, (1, 2), True, True)
register("interaction_single_field", ("type", "reset", "type"), "interaction", "errors", 1, (2, 3))
register("always_follows_typing", ("type", "type", "reset"), "always", "errors", 1, (2, 3))
register("validate_returns_true_or_false", ("type", "validate", "type"), "disabled", "ok", 1, (2, 3))
register("always_validate_returns", ("type", "type"), "always", "ok", 1, (1, 2))
register("save_collects_text", ("type", "type", "save"), "disabled", "saved", 1, (2, 3), False)
register("save_ignores_validation", ("type", "validate", "save"), "disabled", "saved", 1, (2, 3))


# ── single-field and special cases ──────────────────────────────────────

@template(TEMPLATES)
def field_level_autovalidate(rng):
    mode = rng.choice(("always", "always", "onUserInteraction"))
    idx = rng.choice(SHORT)
    typed = [rng.choice([x for x in VALUES if x]) for _ in range(rng.randint(0, 2))]
    cur, flagged = "", False
    for t in typed:
        if t != cur:
            cur = t
            flagged = True
    bad = VALIDATORS[idx][1](cur)
    if mode == "always":
        n = 1 if bad else 0
        why = "autovalidateMode.always on the field checks it whenever it builds, so its error follows the text with no validate() at all"
    else:
        n = 1 if (flagged and bad) else 0
        why = "onUserInteraction on the field waits until the user has typed into it, then keeps checking"
    w = app(form_of([G("TextFormField", autovalidateMode=f"AutovalidateMode.{mode}", validator=VALIDATORS[idx][0])]))
    pre = "".join(f"await tester.enterText(find.byType(TextFormField), {q(t)});\nawait tester.pump();\n" for t in typed)
    steps = ", ".join(f"typing {q(t)}" for t in typed) or "nothing typed"
    return mk(f"errors showing, {steps}", w, n, f"{why}: the text is {q(cur)} ({VALIDATORS[idx][2]} is bad), {n} showing.", pre + "await tester.pumpAndSettle();\nreturn " + ERRORS + ";")


@template(TEMPLATES)
def initial_values_validated(rng):
    idx = rng.randrange(len(VALIDATORS))
    init = rng.choice([x for x in VALUES if x])
    bad = VALIDATORS[idx][1](init)
    kind = rng.choice(("validate", "ok"))
    w = app(form_of([G("TextFormField", initialValue=q(init), validator=VALIDATORS[idx][0])]))
    if kind == "validate":
        ask, ans = "errors showing after validate()", 1 if bad else 0
        check = f"{FORM}.validate();\nawait tester.pump();\nreturn {ERRORS};"
    else:
        ask, ans = "validate() as 1 or 0", 0 if bad else 1
        check = f"return {FORM}.validate() ? 1 : 0;"
    why = f"The validator runs on the starting text {q(init)} ({VALIDATORS[idx][2]} is bad): it {'complains' if bad else 'is satisfied'}, so {ask.split(' after')[0].split(' as')[0]} gives {ans}."
    return mk(ask, w, ans, why, check)


@template(TEMPLATES)
def limit_then_validate(rng):
    m = rng.choice((2, 3, 4))
    cutoff = rng.choice((2, 3))
    t = rng.choice(["abcdef", "12345", "hello", "xyz", "ab"])
    shown = t[:m]
    bad = len(shown) > cutoff
    w = app(form_of([G("TextFormField", maxLength=str(m), validator=f"(v) => v!.length > {cutoff} ? 'x' : null")]))
    n = 1 if bad else 0
    return mk(f"error texts after typing {q(t)} and validate()", w, n, f"maxLength {m} cuts the typed text to {q(shown)} first; the validator then sees {len(shown)} "
              f"characters and complains above {cutoff}: {n}.",
              f"await tester.enterText(find.byType(TextFormField), {q(t)});\n{FORM}.validate();\nawait tester.pump();\nreturn {ERRORS};")


@template(TEMPLATES)
def what_the_validator_receives(rng):
    kind = rng.choice([("v == null ? 'x' : null", False, "an empty field gives the validator '', not null, so this test never fires"),
                       ("v!.isEmpty ? 'x' : null", True, "an empty field gives ''"),
                       ("v == '' ? 'x' : null", True, "an empty field gives ''"),
                       ("(v ?? '').isEmpty ? 'x' : null", True, "an empty field gives ''"),
                       ("v?.isEmpty ?? true ? 'x' : null", True, "an empty field gives ''")])
    code, fires, why = kind
    w = app(form_of([G("TextFormField", validator=f"(v) => {code}")]))
    n = 1 if fires else 0
    return mk("error texts after validate() on an empty field", w, n, f"{why[0].upper() + why[1:]}: {n}.", f"{FORM}.validate();\nawait tester.pump();\nreturn {ERRORS};")


@template(TEMPLATES)
def which_message_shows(rng):
    msgs = rng.sample("123", 3)
    t = rng.choice(["", "ab", "abcd", "abc"])
    code = f"(v) => v == '' ? '{msgs[0]}' : v!.length < 3 ? '{msgs[1]}' : null"
    shown = msgs[0] if t == "" else msgs[1] if len(t) < 3 else None
    asked = rng.choice(msgs[:2])
    n = 1 if shown == asked else 0
    w = app(form_of([G("TextFormField", validator=code)]))
    pre = f"await tester.enterText(find.byType(TextFormField), {q(t)});\n" if t else ""
    return mk(f"find.text('{asked}') matches how many after {('typing ' + q(t) + ' and ') if t else ''}validate()?", w, n,
              f"The validator returns the first message that applies: with {q(t)} that is {shown!r}; asked for '{asked}': {n}.",
              pre + f"{FORM}.validate();\nawait tester.pump();\nreturn count(find.text('{asked}'));")


@template(TEMPLATES)
def nested_forms(rng):
    idx = rng.choice(SHORT)
    inner = rng.random() < 0.6
    w = app(G("Form", child=G("Column", children=[G("TextFormField"), G("Form", child=G("TextFormField", validator=VALIDATORS[idx][0]))])))
    bad = VALIDATORS[idx][1]("")
    n = (1 if bad else 0) if inner else 0
    which = "last" if inner else "first"
    return mk(f"errors showing after validate() on the {'inner' if inner else 'outer'} Form", w, n,
              "A field belongs to its NEAREST Form: the validated field is inside the inner Form, so the outer Form's validate() never looks at it. "
              f"The empty field ({VALIDATORS[idx][2]} is bad) is {'bad' if bad else 'fine'}; validating the {'inner' if inner else 'outer'} Form: {n}.",
              f"tester.state<FormState>(find.byType(Form).{which}).validate();\nawait tester.pump();\nreturn {ERRORS};")


@template(TEMPLATES)
def hidden_field_validation(rng):
    kind = rng.choice(("offstage", "visibility", "visibility_keep", "visible"))
    bad_field = G("TextFormField", validator="(v) => 'x'")
    wrap = {"offstage": G("Offstage", child=bad_field), "visibility": G("Visibility", visible="false", child=bad_field),
            "visibility_keep": G("Visibility", visible="false", maintainState="true", child=bad_field), "visible": bad_field}[kind]
    ok_field = G("TextFormField", validator="(v) => null")
    validated = kind != "visibility"
    w = app(G("Form", child=G("Column", children=[ok_field, wrap])))
    why = {"offstage": "An Offstage field is still in the tree, so it is validated", "visibility": "An invisible Visibility builds nothing: its field does not exist, so it is not validated",
           "visibility_keep": "maintainState keeps the field alive (offstage), so it is still validated", "visible": "A visible field is validated"}[kind]
    return mk("validate() as 1 or 0 (the field that always complains is wrapped)", w, 1 - int(validated), f"{why}: validate() is {'false' if validated else 'true'}: {1 - int(validated)}.",
              f"return {FORM}.validate() ? 1 : 0;")


@template(TEMPLATES)
def lazy_list_field(rng):
    gap = rng.choice((100, 800))
    first_bad = rng.random() < 0.5
    v1 = "(v) => 'x'" if first_bad else "(v) => null"
    w = app(G("Form", child=G("ListView", children=[G("TextFormField", validator=v1), G("SizedBox", height=str(gap)), G("TextFormField", validator="(v) => 'x'")])))
    second_built = gap == 100
    n = int(first_bad) + int(second_built)
    return mk("error texts after validate()", w, n, f"The ListView builds only what is near the screen: the second field is {gap} pixels further down, so it is "
              f"{'built (and complains)' if second_built else 'never built, so nobody validates it'}; the first field {'complains' if first_bad else 'is fine'}: {n}.",
              f"{FORM}.validate();\nawait tester.pump();\nreturn {ERRORS};")


@template(TEMPLATES)
def custom_form_field(rng):
    init = rng.choice(("false", "true"))
    ops = [rng.choice(("validate", "true", "false")) for _ in range(rng.randint(1, 2))] + ["validate"]
    val = init == "true"
    shown = False
    code = []
    for o in ops:
        if o == "validate":
            shown = not val
            code.append(f"{FORM}.validate();\nawait tester.pump();")
        else:
            val = o == "true"
            code.append(f"tester.state<FormFieldState<bool>>(find.byType(FormField<bool>)).didChange({o});\nawait tester.pump();")
    w = G("Form", child=G("FormField<bool>", initialValue=init, validator="(v) => v! ? null : 'x'", builder="(s) => Text(s.errorText ?? 'ok')"))
    n = 1 if shown else 0
    steps = ", ".join("validate()" if o == "validate" else f"didChange({o})" for o in ops)
    return mk("find.text('x') matches how many after " + steps + "?", w, n, "The error text is whatever the last validate() found for the value at that moment; "
              f"didChange alone changes the value but does not validate. Final: value {str(val).lower()}, error {'showing' if shown else 'not showing'}: {n}.",
              "\n".join(code) + f"\nreturn {ERRORS};")


@template(TEMPLATES)
def numeric_validator(rng):
    t = rng.choice(["12", "1a", " 5", "-3", "3.5", "+4", "007", "1e3", "", "4 2"])
    bad = not dart_try_parse(t)
    w = app(form_of([G("TextFormField", validator="(v) => int.tryParse(v!) == null ? 'x' : null")]))
    n = 1 if bad else 0
    return mk(f"error texts after typing {q(t)} and validate()", w, n, f"int.tryParse ignores spaces around the text and accepts an optional sign and digits only (no dot, no exponent, no spaces inside): {q(t)} "
              f"{'fails' if bad else 'parses'}: {n}.",
              f"await tester.enterText(find.byType(TextFormField), {q(t)});\n{FORM}.validate();\nawait tester.pump();\nreturn {ERRORS};")


@template(TEMPLATES)
def reset_text_length(rng):
    init = rng.choice(["ab", "abc", "hello", ""])
    t = rng.choice(["wxyz", "q", "12345"])
    w = app(form_of([G("TextFormField", initialValue=q(init))] if init else [G("TextFormField")]))
    n = len(init)
    return mk(f"length of the text after typing {q(t)} and reset()", w, n, f"reset() puts the initialValue ({q(init)}) back: {n} characters.",
              f"await tester.enterText(find.byType(TextFormField), {q(t)});\n{FORM}.reset();\nawait tester.pump();\nreturn tester.widget<EditableText>(find.byType(EditableText)).controller.text.length;")


@template(TEMPLATES)
def validation_at_start(rng):
    mode = rng.choice(("disabled", "always", "onUserInteraction"))
    idx = rng.randrange(len(VALIDATORS))
    kw = {} if mode == "disabled" else {"autovalidateMode": f"AutovalidateMode.{mode}"}
    w = app(G("Form", **kw, child=G("TextFormField", validator=VALIDATORS[idx][0])))
    bad = VALIDATORS[idx][1]("")
    n = 1 if (mode == "always" and bad) else 0
    why = {"disabled": "The default, disabled, never validates by itself: nothing shows until validate() is called",
           "always": "always validates the fields as soon as they are built, with no user action",
           "onUserInteraction": "onUserInteraction waits for the user to change a field, and nobody has"}[mode]
    return mk("errors showing before anything is typed", w, n, f"{why}. The field is empty and {VALIDATORS[idx][2]} is bad: {n}.", "await tester.pumpAndSettle();\nreturn " + ERRORS + ";")


@template(TEMPLATES)
def decoration_text_vs_validator(rng):
    kind = rng.choice(("errorText", "helperText"))
    typed = rng.choice(["", "ab", "abc", "abcd"])
    bad = typed == ""
    deco = G("InputDecoration", **{kind: "'y'"})
    w = app(form_of([G("TextFormField", decoration=deco, validator="(v) => v == '' ? 'x' : null")]))
    if kind == "errorText":
        n = 0 if bad else 1
        why = ("The validator's message replaces the decoration's errorText while the field is invalid" if bad else
               "The field is valid, so nothing replaces the decoration's own errorText, which keeps showing")
    else:
        n = 0 if bad else 1
        why = ("An error hides the helperText" if bad else "With no error the helperText shows")
    pre = f"await tester.enterText(find.byType(TextFormField), {q(typed)});\n" if typed else ""
    return mk(f"find.text('y') matches how many after {('typing ' + q(typed) + ' and ') if typed else ''}validate()?", w, n,
              f"{why}: {n}.", pre + f"{FORM}.validate();\nawait tester.pumpAndSettle();\nreturn count(find.text('y'));")


@template(TEMPLATES)
def disabled_field_in_form(rng):
    enabled = rng.random() < 0.5
    kind = rng.choice(("validate", "always"))
    kw = {} if enabled else {"enabled": "false"}
    form_kw = {"autovalidateMode": "AutovalidateMode.always"} if kind == "always" else {}
    w = app(G("Form", **form_kw, child=G("TextFormField", **kw, validator="(v) => 'x'")))
    n = 1 if (enabled or kind == "validate") else 0
    why = ("An enabled field with a validator that always complains shows its error" if enabled else
           "validate() still runs the validator of a disabled field" if kind == "validate" else
           "A disabled field is not auto-validated, so autovalidateMode.always leaves it alone")
    check = ("await tester.pumpAndSettle();\n" if kind == "always" else f"{FORM}.validate();\nawait tester.pumpAndSettle();\n") + f"return {ERRORS};"
    return mk("errors showing after " + ("validate()" if kind == "validate" else "the first frame (autovalidateMode.always)"), w, n, f"{why}: {n}.", check)
