"""async and await Basics: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

ORDER = 95

DECK = Deck(
    id="py-async",
    title="async and await Basics",
    language="python",
    blurb="Coroutines, await, tasks and gather: how asyncio lets one thread juggle many jobs that spend their time waiting.",
    slides=(
        Slide(
            title="async def makes a coroutine",
            text="A function defined with async def does not run when you call it. Calling it gives a coroutine object, which asyncio.run can then run to the end.",
            code=r"""import asyncio
async def greet():
    return "hi"
c = greet()
print(type(c).__name__)
print(asyncio.run(c))""",
            output="coroutine\nhi",
            point="Calling an async function builds a coroutine; it runs only when awaited or run.",
        ),
        Slide(
            title="asyncio.run and await",
            text="asyncio.run starts the event loop and runs one main coroutine. Inside async code, await runs another coroutine and gives you its result.",
            code=r"""import asyncio
async def double(n):
    return n * 2
async def main():
    x = await double(4)
    print(x)
asyncio.run(main())""",
            output="8",
            point="await can only be used inside async def.",
        ),
        Slide(
            title="Awaits run one after another",
            text="When you await coroutines one by one, each finishes before the next starts. Nothing overlaps yet.",
            code=r"""import asyncio
async def step(name):
    print("start", name)
    return name
async def main():
    a = await step("a")
    b = await step("b")
    print(a + b)
asyncio.run(main())""",
            output="start a\nstart b\nab",
            point="await alone is sequential; overlap needs tasks.",
        ),
        Slide(
            title="create_task and sleep(0)",
            text="create_task schedules a coroutine to run alongside. It only gets its turn when the current code awaits, and asyncio.sleep(0) is the shortest way to give up the turn.",
            code=r"""import asyncio
async def worker():
    print("worker runs")
async def main():
    task = asyncio.create_task(worker())
    print("main continues")
    await asyncio.sleep(0)
    print("main done")
asyncio.run(main())""",
            output="main continues\nworker runs\nmain done",
            point="Tasks run only when someone else awaits.",
        ),
        Slide(
            title="Two tasks take turns",
            text="Each await asyncio.sleep(0) hands control to the other task. The prints interleave in a fixed order: the tasks alternate.",
            code=r"""import asyncio
async def count(name):
    for i in range(2):
        print(name, i)
        await asyncio.sleep(0)
async def main():
    await asyncio.gather(count("A"), count("B"))
asyncio.run(main())""",
            output="A 0\nB 0\nA 1\nB 1",
            point="Cooperative: tasks switch only at an await.",
        ),
        Slide(
            title="gather returns results in order",
            text="asyncio.gather runs coroutines together and returns their results in the order you passed them, not the order they finished.",
            code=r"""import asyncio
async def get(n):
    for _ in range(n):
        await asyncio.sleep(0)
    return n
async def main():
    print(await asyncio.gather(get(3), get(1), get(2)))
asyncio.run(main())""",
            output="[3, 1, 2]",
            point="Results line up with the arguments, even if get(1) finished first.",
        ),
        Slide(
            title="gather with an error",
            text="By default the first error raised in a gather comes straight out of it. With return_exceptions=True, errors come back as ordinary results.",
            code=r"""import asyncio
async def ok():
    return 1
async def bad():
    raise ValueError("boom")
async def main():
    r = await asyncio.gather(ok(), bad(), return_exceptions=True)
    print(r[0], type(r[1]).__name__)
asyncio.run(main())""",
            output="1 ValueError",
            point="return_exceptions=True keeps one failure from hiding the others.",
        ),
        Slide(
            title="A task has a result",
            text="A task is a running coroutine. done() says whether it has finished, and awaiting it hands you its result.",
            code=r"""import asyncio
async def calc():
    return 42
async def main():
    t = asyncio.create_task(calc())
    print(t.done())
    print(await t)
    print(t.done(), t.result())
asyncio.run(main())""",
            output="False\n42\nTrue 42",
            point="A new task has not run yet: done() is False until it gets a turn.",
        ),
        Slide(
            title="async for with an async generator",
            text="An async generator uses yield inside async def, and may await between items. Loop over it with async for.",
            code=r"""import asyncio
async def ticks(n):
    for i in range(n):
        await asyncio.sleep(0)
        yield i
async def main():
    async for t in ticks(3):
        print("tick", t)
asyncio.run(main())""",
            output="tick 0\ntick 1\ntick 2",
            point="async for is for loops whose next item may need a wait.",
        ),
        Slide(
            title="async with",
            text="An async context manager has __aenter__ and __aexit__, which may await. It is used for things like network connections.",
            code=r"""import asyncio
class Session:
    async def __aenter__(self):
        print("open")
    async def __aexit__(self, *exc):
        print("close")
async def main():
    async with Session():
        print("working")
asyncio.run(main())""",
            output="open\nworking\nclose",
            point="async with is with, where set-up and clean-up can wait.",
        ),
        Slide(
            title="Timeouts",
            text="asyncio.timeout(seconds) cancels the block if it takes too long and raises TimeoutError. It needs Python 3.11 or newer. This example uses 0 seconds so nothing really waits.",
            code=r"""import asyncio
async def main():
    try:
        async with asyncio.timeout(0):
            await asyncio.sleep(10)
    except TimeoutError:
        print("too slow")
asyncio.run(main())""",
            output="too slow",
            point="Wrap slow waits in a timeout so one stuck call cannot hang the program.",
        ),
        Slide(
            title="await only works in async def",
            text="Using await in an ordinary function is a syntax error, found before anything runs. Mark the function async def to use it.",
            code=r"""src = "def f():\n    await g()"
try:
    compile(src, "s", "exec")
except SyntaxError as e:
    print(type(e).__name__)""",
            output="SyntaxError",
            point="async def on the outside, await on the inside.",
        ),
        Slide(
            title="Await in a comprehension, or gather",
            text="An await inside a comprehension still runs the items one by one. gather(*...) starts them all and waits for them together.",
            code=r"""import asyncio
async def sq(n):
    await asyncio.sleep(0)
    return n * n
async def main():
    print([await sq(n) for n in range(4)])
    print(await asyncio.gather(*(sq(n) for n in range(4))))
asyncio.run(main())""",
            output="[0, 1, 4, 9]\n[0, 1, 4, 9]",
            point="Same answers, but gather lets the waits overlap.",
        ),
        Slide(
            title="Async is for waiting, not computing",
            text="A task that never awaits holds the whole loop until it finishes. Here nothing can interleave, because busy() never gives up its turn.",
            code=r"""import asyncio
async def busy():
    print("busy start")
    total = sum(range(1000))
    print("busy end")
async def other():
    print("other")
async def main():
    await asyncio.gather(busy(), other())
asyncio.run(main())""",
            output="busy start\nbusy end\nother",
            point="Async helps when jobs wait (network, disk); it does not speed up number crunching.",
        ),
        Slide(
            title="Threads vs async",
            text="Async runs many jobs on one thread and switches only at await, so there is little to lock and thousands of waits are cheap. Threads let ordinary blocking code overlap, but they switch anywhere. For heavy computing, use processes.",
            point="Many waits: async. Blocking libraries: threads. Many CPU cores: processes.",
        ),
    ),
)
