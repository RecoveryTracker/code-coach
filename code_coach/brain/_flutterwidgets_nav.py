"""Flutter widgets pack, activity 6: Navigate.

A `MaterialApp` shows its `home` Text('1'); the declaration `r(label)` makes a page route whose body is `Text(label)`;
`go(n)` runs some Navigator calls on the app's NavigatorState (the oracle calls it, then `pumpAndSettle()`s, so
animations are done and popped or replaced routes are gone). The question asks for the text of the page on top, for
how many page Texts are left in the tree (`find.byType(Text, skipOffstage: false)`: a covered page is kept, offstage),
for all of them bottom to top, or for `canPop()`.

The model keeps the route stack as a Python list of labels and applies each call by Navigator's rules: push adds;
pop removes the top; pushReplacement swaps the top; pushAndRemoveUntil removes routes until the predicate holds and
pushes; popUntil pops until the predicate holds; maybePop asks the page first (a `PopScope(canPop: false)` refuses,
a plain pop() does not ask); removeRoute / replace / replaceRouteBelow edit the middle of the stack; the Future a push
returns completes with the value given to the pop (or pushReplacement's `result:`, which goes to the replaced route).
"""

from __future__ import annotations

import random

from ._flutter_model import Retry
from ._flutterwidgets_kit import mk, template
from .items import Item

TEMPLATES: list = []

R = "r(s) => MaterialPageRoute(builder: (_) => Text(s));"
R_INT = "r(s) => MaterialPageRoute<int>(builder: (_) => Text(s));"
HOME = "MaterialApp(home: Text('1'))"
GO = "void go(NavigatorState n) {"
CHECK_HEAD = "final n = tester.state<NavigatorState>(find.byType(Navigator));\n"
TOP = "tester.widget<Text>(find.byType(Text)).data"
DEPTH = "count(find.byType(Text, skipOffstage: false))"
JOINED = "tester.widgetList<Text>(find.byType(Text, skipOffstage: false)).map((t) => t.data).join()"

ASK = {
    "top": ("text on top", TOP),
    "depth": ("page Texts left", DEPTH),
    "joined": ("page Texts, bottom to top", JOINED),
    "can_pop": ("canPop() as 1 or 0", "n.canPop() ? 1 : 0"),
}


def observe(stack: list[str], what: str) -> str:
    return {"top": stack[-1], "depth": str(len(stack)), "joined": "".join(stack), "can_pop": "1" if len(stack) > 1 else "0"}[what]


def explain_stack(stack: list[str], what: str) -> str:
    shown = "[" + ", ".join(stack) + "]"
    return {"top": f"The stack ends as {shown}, so the page on top shows {stack[-1]}.",
            "depth": f"The stack ends as {shown}: {len(stack)} pages are still in the tree (the covered ones stay, offstage).",
            "joined": f"The stack ends as {shown}, bottom to top.",
            "can_pop": f"The stack ends as {shown}; canPop() is true when there is a page below the top."}[what]


def run_check(what: str, asynchronous: bool = False) -> str:
    call = "await go(n);" if asynchronous else "go(n);"
    return f"{CHECK_HEAD}{call}\nawait tester.pumpAndSettle();\nreturn {ASK[what][1]};"


def decl(lines: list[str], asynchronous: bool = False, extra: str = R) -> str:
    head = "Future<void> go(NavigatorState n) async {" if asynchronous else GO
    return extra + "\n" + head + "\n" + "\n".join("  " + ln for ln in lines) + "\n}"


class Stack:
    """The route stack as labels; applies the calls the same way the Navigator does."""

    def __init__(self) -> None:
        self.s = ["1"]
        self.lines: list[str] = []
        self.next = 2
        self.vars: dict[str, str] = {}

    def label(self) -> str:
        k = str(self.next)
        self.next += 1
        return k


OPS = {
    "push": lambda st, lb: (f"n.push(r('{lb}'));", lambda: st.s.append(lb)),
    "pop": lambda st, lb: ("n.pop();", lambda: st.s.pop()),
    "replace": lambda st, lb: (f"n.pushReplacement(r('{lb}'));", lambda: st.s.__setitem__(-1, lb)),
    "keep_first": lambda st, lb: (f"n.pushAndRemoveUntil(r('{lb}'), (x) => x.isFirst);", lambda: st.s.__setitem__(slice(1, None), [lb])),
    "remove_all": lambda st, lb: (f"n.pushAndRemoveUntil(r('{lb}'), (x) => false);", lambda: st.s.__setitem__(slice(0, None), [lb])),
    "pop_first": lambda st, lb: ("n.popUntil((x) => x.isFirst);", lambda: st.s.__setitem__(slice(1, None), [])),
}


def random_ops(rng: random.Random, kinds: tuple[str, ...], count: int) -> Stack:
    st = Stack()
    tries = 0
    while len(st.lines) < count:
        tries += 1
        if tries > 100:
            raise Retry()
        kind = rng.choice(kinds)
        if kind in ("pop", "replace", "pop_first") and len(st.s) < 2:
            continue
        if kind == "pop_first" and len(st.s) < 3:
            continue
        lb = st.label() if kind not in ("pop", "pop_first") else ""
        line, apply = OPS[kind](st, lb)
        apply()
        st.lines.append(line)
    return st


def stack_template(kinds: tuple[str, ...], what: str, count: tuple[int, int] = (2, 3), name: str = ""):
    def make(rng: random.Random) -> Item:
        st = random_ops(rng, kinds, rng.randint(*count))
        ans = observe(st.s, what)
        ask = ASK[what][0]
        return mk(ask, HOME, ans, explain_stack(st.s, what), run_check(what), decls=decl(st.lines))
    make.__name__ = name
    return make


def register(name: str, kinds: tuple[str, ...], what: str, count: tuple[int, int] = (2, 3)) -> None:
    from ._flutter_model import fit

    TEMPLATES.append(fit(stack_template(kinds, what, count, name), whole=False))


register("push_pop_top", ("push", "push", "pop"), "top")
register("push_pop_depth", ("push", "push", "pop"), "depth")
register("push_pop_joined", ("push", "push", "pop"), "joined")
register("push_pop_can_pop", ("push", "pop", "pop"), "can_pop", (2, 3))
register("replace_top", ("push", "replace", "pop"), "top")
register("replace_depth", ("push", "replace", "replace"), "depth")
register("replace_joined", ("push", "replace", "pop"), "joined")
register("keep_first_top", ("push", "push", "keep_first"), "top")
register("keep_first_joined", ("push", "keep_first", "push"), "joined")
register("remove_all_depth", ("push", "push", "remove_all"), "depth")
register("remove_all_joined", ("push", "remove_all", "pop"), "joined")
register("pop_first_depth", ("push", "push", "pop_first"), "depth")
register("pop_first_joined", ("push", "pop_first", "push"), "joined")
register("replace_pop_first_top", ("push", "replace", "pop_first"), "top")
register("push_replace_remove_depth", ("push", "replace", "remove_all"), "depth")
register("keep_first_can_pop", ("push", "keep_first", "pop"), "can_pop")
register("mixed_top", ("push", "pop", "replace", "keep_first", "pop_first"), "top", (3, 3))
register("mixed_joined", ("push", "pop", "replace", "keep_first", "remove_all", "pop_first"), "joined", (3, 3))
register("mixed_can_pop", ("push", "pop", "replace", "keep_first", "remove_all", "pop_first"), "can_pop", (3, 3))


# ── routes you hold on to ───────────────────────────────────────────────

@template(TEMPLATES)
def remove_route_in_the_middle(rng):
    st = Stack()
    k = rng.randint(3, 4)
    lines, held = [], {}
    for i in range(k - 1):
        lb = st.label()
        if rng.random() < 0.7 or not held:
            var = "abc"[len(held)]
            lines.append(f"final {var} = r('{lb}');")
            lines.append(f"n.push({var});")
            held[var] = lb
        else:
            lines.append(f"n.push(r('{lb}'));")
        st.s.append(lb)
    var = rng.choice(list(held))
    lines.append(f"n.removeRoute({var});")
    st.s.remove(held[var])
    what = rng.choice(("top", "joined", "depth"))
    return mk(ASK[what][0], HOME, observe(st.s, what), "removeRoute takes that one page out of the stack wherever it is, without touching the others. "
              + explain_stack(st.s, what), run_check(what), decls=decl(lines))


# ── PopScope and results ────────────────────────────────────────────────

@template(TEMPLATES)
def pop_result(rng):
    val = rng.choice((None, 3, 5, 7))
    route = "MaterialPageRoute<int>(builder: (_) => Text('2'))"
    lines = [f"n.push({route}).then((v) => got = v ?? -1);", "n.pop();" if val is None else f"n.pop({val});"]
    ans = -1 if val is None else val
    d = "int got = 0;\nvoid go(NavigatorState n) {\n" + "\n".join("  " + ln for ln in lines) + "\n}"
    return mk("got after go()", HOME, ans, "The Future a push returns completes with the value given to pop; with no value it completes with null, "
              f"which ?? -1 turns into -1: {ans}.", f"{CHECK_HEAD}go(n);\nawait tester.pumpAndSettle();\nreturn got;", decls=d)


# ── named routes ────────────────────────────────────────────────────────

NAMED_APP = "MaterialApp(routes: {'/2': (c) => Text('2'), '/3': (c) => Text('3')}, home: Text('1'))"


@template(TEMPLATES)
def named_routes(rng):
    st = ["1"]
    lines = []
    for _ in range(rng.randint(2, 3)):
        lb = rng.choice("23")
        kind = rng.choice(("pushNamed", "pushNamed", "pushReplacementNamed", "popAndPushNamed", "pop", "removeUntil", "withName"))
        if kind in ("pop", "pushReplacementNamed", "popAndPushNamed", "withName") and len(st) < 2:
            kind = "pushNamed"
        if kind == "pushNamed":
            lines.append(f"n.pushNamed('/{lb}');")
            st.append(lb)
        elif kind == "pushReplacementNamed":
            lines.append(f"n.pushReplacementNamed('/{lb}');")
            st[-1] = lb
        elif kind == "popAndPushNamed":
            lines.append(f"n.popAndPushNamed('/{lb}');")
            st[-1] = lb
        elif kind == "pop":
            lines.append("n.pop();")
            st.pop()
        elif kind == "removeUntil":
            lines.append(f"n.pushNamedAndRemoveUntil('/{lb}', (x) => x.isFirst);")
            st[1:] = [lb]
        else:
            target = rng.choice(st)
            lines.append(f"n.popUntil(ModalRoute.withName('{'/' if target == '1' else '/' + target}'));")
            while st[-1] != target:
                st.pop()
    what = rng.choice(("top", "depth", "joined"))
    return mk(ASK[what][0], NAMED_APP, observe(st, what), "Named routes work like pushed ones, looked up in the routes table; the home page is the route named '/'. "
              + explain_stack(st, what), run_check(what), decls=decl(lines, extra=""))


@template(TEMPLATES)
def initial_route(rng):
    kind = rng.choice(("plain", "initial2", "initial_both"))
    if kind == "plain":
        app, st = "MaterialApp(routes: {'/2': (c) => Text('2')}, home: Text('1'))", ["1"]
    elif kind == "initial2":
        app, st = "MaterialApp(initialRoute: '/2', routes: {'/2': (c) => Text('2')}, home: Text('1'))", ["1", "2"]
    else:
        app, st = "MaterialApp(initialRoute: '/3', routes: {'/2': (c) => Text('2'), '/3': (c) => Text('3')}, home: Text('1'))", ["1", "3"]
    lines = []
    if rng.random() < 0.5:
        lines.append("n.pushNamed('/2');")
        st = st + ["2"]
    what = rng.choice(("top", "depth", "joined"))
    why = ("With no initialRoute the app starts on its home page, route '/'." if kind == "plain" else
           "initialRoute starts the app on that route; the home page ('/') is put underneath, so the user can go back to it.")
    return mk(ASK[what][0], app, observe(st, what), why + " " + explain_stack(st, what), run_check(what), decls=decl(lines, extra=""))


# ── real buttons ────────────────────────────────────────────────────────

PAGES = ("Widget page(int k) {\n  return Builder(builder: (c) => TextButton(\n      onPressed: () => Navigator.push(c, MaterialPageRoute(builder: (_) => page(k + STEP))),\n"
         "      child: Text('$k')));\n}")


@template(TEMPLATES)
def dialogs_are_not_opaque(rng):
    st = [("1", True)]
    lines = []
    for _ in range(rng.randint(2, 3)):
        kind = rng.choice(("push", "dialog", "dialog", "pop"))
        if kind == "pop" and len(st) < 2:
            kind = "push"
        lb = str(len(lines) + 2 + sum(1 for ln in lines if "pop" in ln) * 0)
        lb = str(2 + len(lines))
        if kind == "push":
            lines.append(f"n.push(r('{lb}'));")
            st.append((lb, True))
        elif kind == "dialog":
            lines.append(f"showDialog(context: n.context, builder: (_) => Text('{lb}'));")
            st.append((lb, False))
        else:
            lines.append("n.pop();")
            st.pop()
    onstage = []
    for lb, opaque in reversed(st):
        onstage.append(lb)
        if opaque:
            break
    ans = "".join(reversed(onstage))
    return mk("Texts on screen, bottom to top", HOME, ans,
              "A page route is opaque: the pages below it are hidden (offstage) and skipped by find.byType. A dialog is not: the route underneath stays on stage. "
              f"The stack is {[x for x, _ in st]}; on stage from the top down to the first opaque route: {ans}.",
              f"{CHECK_HEAD}go(n);\nawait tester.pumpAndSettle();\nreturn tester.widgetList<Text>(find.byType(Text)).map((t) => t.data).join();",
              decls=decl(lines))


@template(TEMPLATES)
def sheets_and_pages(rng):
    st = [("1", True)]
    lines = []
    for i in range(rng.randint(2, 3)):
        kind = rng.choice(("push", "sheet", "sheet", "dialog", "pop"))
        if kind == "pop" and len(st) < 2:
            kind = "sheet"
        lb = str(2 + i)
        if kind == "push":
            lines.append(f"n.push(r('{lb}'));")
            st.append((lb, True))
        elif kind == "sheet":
            lines.append(f"showModalBottomSheet(context: n.context, builder: (_) => Text('{lb}'));")
            st.append((lb, False))
        elif kind == "dialog":
            lines.append(f"showDialog(context: n.context, builder: (_) => Text('{lb}'));")
            st.append((lb, False))
        else:
            lines.append("n.pop();")
            st.pop()
    onstage = []
    for lb, opaque in reversed(st):
        onstage.append(lb)
        if opaque:
            break
    ans = "".join(reversed(onstage))
    return mk("Texts on screen, bottom to top", HOME, ans,
              "A bottom sheet and a dialog are routes that do not cover the page below (they are not opaque), so it stays on stage; a page route covers everything under it. "
              f"The stack is {[x for x, _ in st]}; on stage from the top down to the first opaque route: {ans}.",
              f"{CHECK_HEAD}go(n);\nawait tester.pumpAndSettle();\nreturn tester.widgetList<Text>(find.byType(Text)).map((t) => t.data).join();",
              decls=decl(lines))
