"""Predict the output, in JavaScript, for the event loop.

Async ordering is the thing people get wrong most in JavaScript, and it
is wrong in the same way every time: the code is read top to bottom as
if it ran top to bottom. It does not. There are three places a line can
be waiting. The call stack runs the script, and anything it calls, to
the end. Then the microtask queue is emptied completely — promise
callbacks, the rest of an async function after an await, and
queueMicrotask — including anything those callbacks add to it. Only
then does one task come off the task queue: one timer, one interval
tick. After that task, the microtasks are emptied again, and so on.

Everything here runs in plain Node, and nothing depends on a race
between timers: where two timers matter, their delays are far apart or
exactly equal. Every expected output was worked out by hand first and
then checked against what Node printed, and
tests/test_predict_jsasync.py keeps checking.
"""

from __future__ import annotations

from code_coach.kata.puzzle import Puzzle, _p

LOOP = "Event loop"


JS_ASYNC_PUZZLES: tuple[Puzzle, ...] = (
    _p(
        id="predict-jsa-timeout-zero",
        level=1,
        name="A timer of zero",
        family=LOOP,
        language="javascript",
        code=(
            'console.log("start");\n'
            'setTimeout(() => console.log("timeout"), 0);\n'
            'console.log("end");'
        ),
        expect="start\nend\ntimeout",
        why=(
            "setTimeout never calls its function straight away, even "
            "with a delay of zero. It puts the function on the task "
            "queue, and the task queue is only looked at once the call "
            "stack is empty — once the whole script has run. So `end` "
            "prints first. Zero means \"as soon as you are free\", not "
            "\"now\"."
        ),
    ),
    _p(
        id="predict-jsa-promise-before-timer",
        level=1,
        name="The timer was written first",
        family=LOOP,
        language="javascript",
        code=(
            'setTimeout(() => console.log("timeout"), 0);\n'
            'Promise.resolve().then(() => console.log("promise"));\n'
            'console.log("script");'
        ),
        expect="script\npromise\ntimeout",
        why=(
            "The order the lines are written in does not decide this. "
            "The script runs to the end first. Then every microtask — "
            "which is where a promise's then goes — runs before the "
            "next task, which is where the timer went. The promise "
            "wins even though the timer was set up first."
        ),
    ),
    _p(
        id="predict-jsa-executor-is-sync",
        level=1,
        name="Inside new Promise",
        family=LOOP,
        language="javascript",
        code=(
            'console.log("A");\n'
            "new Promise((resolve) => {\n"
            '  console.log("B");\n'
            "  resolve();\n"
            '  console.log("C");\n'
            '}).then(() => console.log("D"));\n'
            'console.log("E");'
        ),
        expect="A\nB\nC\nE\nD",
        why=(
            "The function passed to new Promise runs immediately, on the "
            "call stack, as part of the constructor — nothing about it "
            "is asynchronous. Calling resolve does not stop it either, "
            "so C prints too. Only the then callback waits: it goes to "
            "the microtask queue, and runs after E, when the script is "
            "done."
        ),
    ),
    _p(
        id="predict-jsa-timer-delays",
        level=1,
        name="Four timers",
        family=LOOP,
        language="javascript",
        code=(
            'setTimeout(() => console.log("slow"), 100);\n'
            'setTimeout(() => console.log("first"), 0);\n'
            'setTimeout(() => console.log("medium"), 50);\n'
            'setTimeout(() => console.log("second"), 0);'
        ),
        expect="first\nsecond\nmedium\nslow",
        why=(
            "Each timer waits off to the side until it is due, then joins "
            "the task queue, so timers fire in order of when they are due, "
            "not the order they were written. Two timers due at the same moment fire "
            "in the order they were set — first in, first out — so the "
            "two zeros keep their order. A delay is a minimum wait, "
            "never an exact one, which is why these are kept far apart."
        ),
    ),
    _p(
        id="predict-jsa-async-returns-promise",
        level=2,
        name="What an async function returns",
        family=LOOP,
        language="javascript",
        code=(
            "async function load() {\n"
            '  console.log("loading");\n'
            "  return 42;\n"
            "}\n"
            "const p = load();\n"
            'console.log("got", typeof p);\n'
            'p.then((v) => console.log("value", v));\n'
            'console.log("done");'
        ),
        expect="loading\ngot object\ndone\nvalue 42",
        why=(
            "An async function with no await in it runs all the way "
            "through on the call stack, so `loading` prints straight "
            "away. But it never hands back the value itself: `return 42` "
            "becomes a promise resolved with 42, and typeof a promise is "
            "object. The value only comes out through then, which is a "
            "microtask, so it waits for `done`."
        ),
    ),
    _p(
        id="predict-jsa-queue-microtask",
        level=2,
        name="queueMicrotask and then",
        family=LOOP,
        language="javascript",
        code=(
            'setTimeout(() => console.log("timer"), 0);\n'
            'queueMicrotask(() => console.log("micro 1"));\n'
            'Promise.resolve().then(() => console.log("then"));\n'
            'queueMicrotask(() => console.log("micro 2"));\n'
            'console.log("sync");'
        ),
        expect="sync\nmicro 1\nthen\nmicro 2\ntimer",
        why=(
            "queueMicrotask puts a function straight on the same "
            "microtask queue that promise callbacks use. It is one queue, "
            "first in first out, so the three run in the order they "
            "were queued, all after the script and all before the timer."
        ),
    ),
    _p(
        id="predict-jsa-interval-cleared",
        level=2,
        name="An interval that stops itself",
        family=LOOP,
        language="javascript",
        code=(
            "let n = 0;\n"
            "const id = setInterval(() => {\n"
            "  n++;\n"
            '  console.log("tick", n);\n'
            "  if (n === 3) clearInterval(id);\n"
            "}, 10);\n"
            'setTimeout(() => console.log("n =", n), 0);'
        ),
        expect="n = 0\ntick 1\ntick 2\ntick 3",
        why=(
            "setInterval does not run its function when it is set up — "
            "the first tick is one whole interval away, so the zero "
            "timer gets in first and sees n still 0. Each tick is its "
            "own task. After the third, clearInterval takes it off the "
            "queue, nothing is left waiting, and Node exits on its own."
        ),
    ),
    _p(
        id="predict-jsa-await-plain-value",
        level=2,
        name="Awaiting a number",
        family=LOOP,
        language="javascript",
        code=(
            "async function f() {\n"
            "  console.log(1);\n"
            "  const x = await 5;\n"
            "  console.log(x);\n"
            "}\n"
            "f();\n"
            "Promise.resolve().then(() => console.log(3));\n"
            "console.log(4);"
        ),
        expect="1\n4\n5\n3",
        why=(
            "await on something that is not a promise still waits: 5 is "
            "wrapped in a resolved promise, and the rest of f is queued "
            "as a microtask. That happens while f is running, before the "
            "next line queues the then, so f's continuation is ahead of "
            "it in the queue. The script's own `4` beats both."
        ),
    ),
    _p(
        id="predict-jsa-microtask-in-microtask",
        level=3,
        name="A microtask that queues another",
        family=LOOP,
        language="javascript",
        code=(
            'setTimeout(() => console.log("timer"), 0);\n'
            "Promise.resolve().then(() => {\n"
            '  console.log("outer");\n'
            '  queueMicrotask(() => console.log("inner"));\n'
            "});\n"
            'Promise.resolve().then(() => console.log("second"));'
        ),
        expect="outer\nsecond\ninner\ntimer",
        why=(
            "`inner` is queued while `outer` runs, which puts it at the "
            "back of the microtask queue, behind `second`, which was "
            "already waiting. But the microtask queue is emptied "
            "completely — including anything added while emptying it — "
            "before the next timer runs. A microtask that keeps queueing "
            "microtasks would starve every timer forever."
        ),
    ),
    _p(
        id="predict-jsa-then-inside-timer",
        level=3,
        name="A promise inside a timer",
        family=LOOP,
        language="javascript",
        code=(
            "setTimeout(() => {\n"
            '  console.log("t1");\n'
            '  Promise.resolve().then(() => console.log("p1"));\n'
            "}, 0);\n"
            'setTimeout(() => console.log("t2"), 0);'
        ),
        expect="t1\np1\nt2",
        why=(
            "Both timers are due at once, but they are two separate "
            "tasks. After each task the microtask queue is emptied, so "
            "the then queued inside the first timer runs before the "
            "second timer starts. (Node before version 11 ran both "
            "timers first; browsers and modern Node do it this way.)"
        ),
    ),
    _p(
        id="predict-jsa-two-async-interleave",
        level=3,
        name="Two async functions take turns",
        family=LOOP,
        language="javascript",
        code=(
            "async function a() {\n"
            '  console.log("a1");\n'
            "  await null;\n"
            '  console.log("a2");\n'
            "  await null;\n"
            '  console.log("a3");\n'
            "}\n"
            "async function b() {\n"
            '  console.log("b1"); await null; console.log("b2");\n'
            "}\n"
            "a(); b();"
        ),
        expect="a1\nb1\na2\nb2\na3",
        why=(
            "a runs until its first await and hands back; then b runs "
            "until its first await. Each await queues the rest of its "
            "function as a microtask, so the two take turns: a's next "
            "piece, b's next piece, a's last. Nothing runs in parallel "
            "— there is one call stack, and each await is a place to "
            "step off it."
        ),
    ),
    _p(
        id="predict-jsa-two-chains",
        level=3,
        name="Two then chains",
        family=LOOP,
        language="javascript",
        code=(
            "Promise.resolve()\n"
            '  .then(() => console.log("A1"))\n'
            '  .then(() => console.log("A2"))\n'
            '  .then(() => console.log("A3"));\n'
            "Promise.resolve()\n"
            '  .then(() => console.log("B1"))\n'
            '  .then(() => console.log("B2"));'
        ),
        expect="A1\nB1\nA2\nB2\nA3",
        why=(
            "A chain is not queued all at once. Only the first then of "
            "each chain is queued by the script; each later then is "
            "queued when the one before it finishes. So A1 and B1 are "
            "in the queue together, A1 queues A2, B1 queues B2, and the "
            "chains zip together one step at a time."
        ),
    ),
    _p(
        id="predict-jsa-finally",
        level=3,
        name="finally on both roads",
        family=LOOP,
        language="javascript",
        code=(
            'Promise.resolve("ok")\n'
            '  .finally(() => console.log("finally"))\n'
            '  .then((v) => console.log("then", v));\n'
            'Promise.reject(new Error("no"))\n'
            '  .finally(() => console.log("cleanup"))\n'
            '  .catch((e) => console.log("catch", e.message));\n'
            'console.log("sync");'
        ),
        expect="sync\nfinally\ncleanup\nthen ok\ncatch no",
        why=(
            "finally runs whether the promise kept or broke its word, "
            "and it gets no argument — it cannot see or change the "
            "result. What came in goes out untouched: \"ok\" reaches the "
            "then, and the error reaches the catch. Both chains take "
            "the same number of steps through the microtask queue, so "
            "they stay in the order the script started them."
        ),
    ),
    _p(
        id="predict-jsa-all-keeps-order",
        level=3,
        name="Promise.all and who finished first",
        family=LOOP,
        language="javascript",
        code=(
            "const wait = (ms, v) => new Promise((r) => setTimeout(() => {\n"
            '  console.log("done", v);\n'
            "  r(v);\n"
            "}, ms));\n"
            'Promise.all([wait(60, "a"), wait(0, "b"), wait(30, "c")])\n'
            '  .then((vs) => console.log(vs.join(" ")));'
        ),
        expect="done b\ndone c\ndone a\na b c",
        why=(
            "The three timers reach the task queue shortest first, and "
            "each prints as it runs. Promise.all waits "
            "for the last of them, and then hands back the results in "
            "the order the promises were given to it — not the order "
            "they finished in. Each result goes into its own slot, so "
            "the array reads a, b, c whatever the timing."
        ),
    ),
    _p(
        id="predict-jsa-async-vs-chain",
        level=4,
        name="An await against a chain",
        family=LOOP,
        language="javascript",
        code=(
            "async function run() {\n"
            '  console.log("run start");\n'
            "  await Promise.resolve();\n"
            '  console.log("run after await");\n'
            "}\n"
            "Promise.resolve()\n"
            '  .then(() => console.log("then 1"))\n'
            '  .then(() => console.log("then 2"));\n'
            "run();\n"
            'console.log("sync end");'
        ),
        expect="run start\nsync end\nthen 1\nrun after await\nthen 2",
        why=(
            "`then 1` was queued before run was even called, so it is "
            "first in the microtask queue. run prints and reaches its "
            "await, which queues the rest of run behind `then 1`. When "
            "`then 1` finishes it queues `then 2` — behind run. Awaiting "
            "an already-resolved promise costs one turn of the queue, "
            "the same as one then."
        ),
    ),
    _p(
        id="predict-jsa-catch-hops",
        level=4,
        name="How far away the catch is",
        family=LOOP,
        language="javascript",
        code=(
            'Promise.reject(new Error("boom"))\n'
            '  .then(() => console.log("then 1"))\n'
            '  .then(() => console.log("then 2"))\n'
            '  .catch((e) => console.log("caught", e.message));\n'
            "Promise.resolve()\n"
            '  .then(() => console.log("x1"))\n'
            '  .then(() => console.log("x2"))\n'
            '  .then(() => console.log("x3"));'
        ),
        expect="x1\nx2\ncaught boom\nx3",
        why=(
            "A rejection does not jump to the catch. It walks down the "
            "chain one then at a time, and each then it skips is still "
            "a microtask: it runs, finds it has no error handler, and "
            "passes the rejection on. The catch is three steps from the "
            "start, so it lands between x2 and x3 in the other chain."
        ),
    ),
    _p(
        id="predict-jsa-race",
        level=4,
        name="Who wins the race",
        family=LOOP,
        language="javascript",
        code=(
            "const wait = (ms, v) => new Promise((r) => setTimeout(() => r(v), ms));\n"
            'Promise.race([wait(0, "timer"), "plain", Promise.resolve("promise")])\n'
            '  .then((v) => console.log("race:", v));\n'
            'Promise.race([wait(80, "slow"), wait(20, "quick")])\n'
            '  .then((v) => console.log("race:", v));'
        ),
        expect="race: plain\nrace: quick",
        why=(
            "Promise.race settles with whichever entry settles first. "
            "A timer, even of zero, is a task, so both settled entries "
            "beat it. Between those two it is a tie, and a tie goes to "
            "the earlier one in the list: a plain value counts as an "
            "already-resolved promise, and it comes first. The second "
            "race is decided by the shorter delay."
        ),
    ),
    _p(
        id="predict-jsa-throw-timer-vs-then",
        level=4,
        name="Throwing later",
        family=LOOP,
        language="javascript",
        code=(
            'process.on("uncaughtException", (e) => console.log("uncaught:", e.message));\n'
            "try {\n"
            '  setTimeout(() => { throw new Error("in timer"); }, 0);\n'
            '  Promise.resolve().then(() => { throw new Error("in then"); })\n'
            '    .catch((e) => console.log("caught:", e.message));\n'
            "} catch (e) {\n"
            '  console.log("try caught:", e.message);\n'
            "}\n"
            'console.log("sync done");'
        ),
        expect="sync done\ncaught: in then\nuncaught: in timer",
        why=(
            "The try block only sets things up and finishes without "
            "error, so its catch never runs: by the time either "
            "callback throws, the try is long gone from the call stack. "
            "A throw inside a then becomes a rejected promise, which the "
            "chain's catch handles. A throw inside a timer has no "
            "promise to land in, so it reaches the top — normally a "
            "crash; here Node's last-chance handler reports it."
        ),
    ),
)
