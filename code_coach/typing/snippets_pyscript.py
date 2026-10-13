"""Python for scripting: files, arguments, logging, processes and asyncio.

The lines are the ones a command-line tool or an automation script is
made of: pathlib for paths and files, argparse for options, logging,
subprocess and shlex for running other programs, JSON kept on disk,
environment variables, urllib and http.server for the web, asyncio for
doing several things at once, contextlib and the with statement, f-string
formatting, the `__main__` guard, and the commands that make a virtual
environment and install into it (typed as strings, since a line of shell
is not Python).

The blocks are whole little programs that print their result, and the
tests run every one in the real interpreter and hold what it prints to an
answer worked out by hand. They never read sys.argv: argparse is given an
explicit list. A block that touches the disk works inside a
TemporaryDirectory, which removes itself, and prints names rather than
paths. No block starts another program or reaches the internet. The one
exception to the network rule is the one with a server: it listens on
127.0.0.1, port 0 (the system picks a free one), asks itself a question and
shuts down. The asyncio blocks tell their tasks apart by delays of tens of
milliseconds, far more than the event loop needs to keep them in order.
"""

from __future__ import annotations

from code_coach.typing.texts import Passage


def _s(text: str, note: str) -> Passage:
    return Passage(text, note)


# -- Lines ----------------------------------------------------

PYSCRIPT_LINES: tuple[Passage, ...] = (
    # pathlib
    _s("from pathlib import Path, PurePath", "paths as objects, not strings"),
    _s("root = Path(__file__).resolve().parent.parent",
       "two folders up from this script"),
    _s("config = root / \"config\" / \"settings.json\"", "the slash joins path parts"),
    _s("config.parent.mkdir(parents=True, exist_ok=True)",
       "make the folder and its parents, quietly if it exists"),
    _s("text = config.read_text(encoding=\"utf-8\")", "the whole file as a string"),
    _s("config.write_text(json.dumps(settings, indent=2), encoding=\"utf-8\")",
       "save settings as readable JSON"),
    _s("for path in sorted(root.rglob(\"*.log\")):", "every log file below here"),
    _s("stale = [p for p in logs.iterdir() if p.suffix == \".tmp\"]",
       "the leftover temp files"),
    _s("print(path.name, path.stem, path.suffix)", "the three parts of a file name"),
    _s("backup = path.with_name(path.stem + \".bak\")", "a sibling file with a new name"),
    _s("path.unlink(missing_ok=True)", "delete it, and do not mind if it is gone"),
    _s("home = Path.home() / \".config\" / \"tool\"", "where a tool keeps its settings"),
    _s("if path.is_file() and path.suffix == \".py\":", "only real Python files"),
    _s("shutil.rmtree(build_dir, ignore_errors=True)", "remove a folder and all inside it"),

    # argparse
    _s("parser = argparse.ArgumentParser(description=\"Tidy a folder\")",
       "the description shows in --help"),
    _s("parser.add_argument(\"folder\", type=Path)", "a required argument, made a Path"),
    _s("parser.add_argument(\"-v\", \"--verbose\", action=\"store_true\")",
       "a flag that is False unless given"),
    _s("parser.add_argument(\"--limit\", type=int, default=10, help=\"how many\")",
       "a number option with a default"),
    _s("parser.add_argument(\"--mode\", choices=[\"fast\", \"safe\"], default=\"safe\")",
       "only these two values are accepted"),
    _s("args = parser.parse_args()", "read sys.argv"),
    _s("args = parser.parse_args([\"--limit\", \"5\", \"docs\"])",
       "or an explicit list, which is how to test it"),
    _s("sub = parser.add_subparsers(dest=\"command\", required=True)",
       "git-style commands: tool add, tool reset"),
    _s("def main(argv: list[str] | None = None) -> int:",
       "taking argv as a parameter makes main testable"),
    _s("raise SystemExit(main())", "exit with whatever code main returns"),
    _s("sys.exit(f\"error: {exc}\")", "a string prints to stderr and exits with 1"),

    # logging
    _s("logging.basicConfig(level=logging.INFO, format=\"%(levelname)s %(message)s\")",
       "one call to set up the root logger"),
    _s("log = logging.getLogger(__name__)", "a logger named after this module"),
    _s("log.info(\"copied %d files to %s\", count, target)",
       "arguments are formatted only if the line is emitted"),
    _s("log.warning(\"skipping %s\", path)", "something odd, but the run goes on"),
    _s("log.exception(\"could not read %s\", path)",
       "an error message with the traceback attached"),

    # subprocess
    _s("result = subprocess.run(cmd, capture_output=True, text=True, check=True)",
       "run a program, keep its output, raise if it fails"),
    _s("out = subprocess.check_output([\"git\", \"rev-parse\", \"HEAD\"], text=True)",
       "a program's output as a string"),
    _s("print(result.stdout.strip(), result.returncode)", "its output and its exit code"),
    _s("subprocess.run([sys.executable, \"-m\", \"pytest\", \"-q\"], check=True)",
       "run a module with the same Python that is running now"),
    _s("except subprocess.CalledProcessError as exc:",
       "check=True turns a failed exit code into this"),
    _s("parts = shlex.split(command)", "split a command line the way a shell would"),

    # JSON files, environment and temp folders
    _s("with tempfile.TemporaryDirectory() as tmp:",
       "a scratch folder that deletes itself"),
    _s("path = Path(tmp) / \"state.json\"", "a file inside it"),
    _s("state = json.loads(path.read_text()) if path.exists() else {}",
       "start empty the first time"),
    _s("with path.open(\"w\", encoding=\"utf-8\") as f:", "open for writing"),
    _s("json.dump(state, f, indent=2)", "write the JSON straight into the file"),
    _s("token = os.environ[\"API_TOKEN\"]", "required: a KeyError if it is missing"),

    # Web
    _s("with urllib.request.urlopen(url, timeout=5) as resp:",
       "always give a request a timeout"),
    _s("data = json.load(resp)", "parse the response body as JSON"),
    _s("req = urllib.request.Request(url, headers={\"User-Agent\": \"tool/1.0\"})",
       "a request that says who is asking"),
    _s("query = urllib.parse.urlencode({\"q\": \"python\", \"page\": 2})",
       "q=python&page=2, with anything awkward escaped"),
    _s("server = HTTPServer((\"127.0.0.1\", 0), Handler)",
       "port 0 asks the system for a free port"),
    _s("thread = threading.Thread(target=server.serve_forever, daemon=True)",
       "serve in the background"),
    _s("class Handler(BaseHTTPRequestHandler):", "one method per HTTP verb"),
    _s("def do_GET(self) -> None:", "called for every GET request"),

    # asyncio
    _s("async def main() -> None:", "a coroutine, run by asyncio.run"),
    _s("asyncio.run(main())", "start the event loop, run main, then close it"),
    _s("await asyncio.sleep(0.1)", "wait without blocking the other tasks"),
    _s("results = await asyncio.gather(fetch(1), fetch(2), return_exceptions=True)",
       "run both at once; results keep the order asked for"),
    _s("task = asyncio.create_task(worker(name, delay))", "start it now, await it later"),
    _s("async with asyncio.TaskGroup() as group:",
       "all tasks finish, or all are cancelled"),
    _s("async with asyncio.timeout(2):", "cancel whatever is inside after two seconds"),

    # contextlib and with
    _s("from contextlib import contextmanager, suppress", "write a with-block as a function"),
    _s("@contextmanager", "everything before yield is setup; after, cleanup"),
    _s("with suppress(FileNotFoundError):", "ignore that one error and carry on"),
    _s("with ExitStack() as stack:", "a with-block whose parts are chosen at run time"),
    _s("with open(src) as fin, open(dst, \"w\") as fout:", "two files in one with"),

    # f-strings
    _s("print(f\"{name:<12}{size:>8,} bytes\")", "a left column and a right column"),
    _s("print(f\"{ratio:.1%} done\")", "0.256 becomes 25.6%"),
    _s("print(f\"{count:03d} files\")", "zero-padded to three digits"),
    _s("print(f\"{value=}\")", "prints the name and the value: value=42"),
    _s("print(f\"{when:%Y-%m-%d %H:%M}\")", "a date, in the format you choose"),

    # Environments, as strings
    _s("CREATE_VENV = \"python -m venv .venv\"", "make a virtual environment"),
    _s("ACTIVATE = \".venv\\\\Scripts\\\\activate\"", "how to switch it on, on Windows"),
    _s("INSTALL = \"python -m pip install -r requirements.txt\"",
       "install from the list; python -m pip uses the right Python"),
    _s("FREEZE = \"python -m pip freeze > requirements.txt\"",
       "write down the exact versions installed"),
    _s("if sys.prefix != sys.base_prefix:", "true when running inside a venv"),
)


# -- Blocks ---------------------------------------------------

def _b(code: str, note: str) -> Passage:
    return Passage(code, f"Python · {note}")


PYSCRIPT_BLOCKS: tuple[Passage, ...] = (
    _b(r"""from pathlib import PurePosixPath

p = PurePosixPath("/home/ann/music/demo.final.mp3")
print(p.name, p.stem, p.suffix, p.parent)
print(p.with_suffix(".wav").name, p.parts[-2])
print(p.relative_to("/home/ann"), p.suffixes)
print(PurePosixPath("a") / "b" / "c.txt", p.is_absolute())""",
       "taking a path apart with PurePosixPath"),
    _b(r"""import json
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "state.json"
    path.write_text(json.dumps({"runs": 1, "tags": ["a"]}), encoding="utf-8")
    state = json.loads(path.read_text(encoding="utf-8"))
    state["runs"] += 1
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    print(state, len(path.read_text().splitlines()))
    print(sorted(p.name for p in Path(tmp).iterdir()))
print(Path(tmp).exists())""",
       "JSON kept in a temporary folder that cleans up after itself"),
    _b(r"""import argparse

parser = argparse.ArgumentParser(prog="tidy")
parser.add_argument("folder")
parser.add_argument("-v", "--verbose", action="store_true")
parser.add_argument("--limit", type=int, default=10)
args = parser.parse_args(["-v", "--limit", "5", "docs"])
print(args.folder, args.verbose, args.limit + 1)
print(parser.parse_args(["src"]))""",
       "argparse reading an explicit list, not sys.argv"),
    _b(r"""import argparse

parser = argparse.ArgumentParser(prog="t")
sub = parser.add_subparsers(dest="command", required=True)
add = sub.add_parser("add")
add.add_argument("numbers", nargs="+", type=int)
sub.add_parser("reset")
args = parser.parse_args(["add", "2", "3", "4"])
print(args.command, sum(args.numbers))
print(parser.parse_args(["reset"]).command)""",
       "argparse subcommands"),
    _b(r"""import io
import logging

stream = io.StringIO()
log = logging.getLogger("tool")
log.setLevel(logging.INFO)
handler = logging.StreamHandler(stream)
handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
log.addHandler(handler)
log.debug("hidden")
log.info("copied %d files", 3)
log.warning("skipping %s", "a.tmp")
print(stream.getvalue(), end="")""",
       "logging into a string, with a level and a format"),
    _b(r"""import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer


class Hello(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(self.path.upper().encode())

    log_message = lambda *args: None


server = HTTPServer(("127.0.0.1", 0), Hello)
threading.Thread(target=server.serve_forever, daemon=True).start()
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
print(opener.open(f"http://127.0.0.1:{server.server_port}/hello").read().decode())
server.shutdown()""",
       "a tiny server on port 0 that answers its own request"),
    _b(r"""import asyncio


async def job(name, delay, log):
    await asyncio.sleep(delay)
    log.append(name)
    return name.upper()


async def main():
    log = []
    results = await asyncio.gather(
        job("slow", 0.06, log), job("fast", 0.01, log), job("mid", 0.03, log)
    )
    print(results, log)


asyncio.run(main())""",
       "gather: results in call order, finishing in delay order"),
    _b(r"""import asyncio


async def step(name, delay, order):
    await asyncio.sleep(delay)
    order.append(name)


async def main():
    order = []
    async with asyncio.TaskGroup() as group:
        group.create_task(step("b", 0.04, order))
        group.create_task(step("a", 0.01, order))
    print(order)


asyncio.run(main())""",
       "a TaskGroup that waits for every task"),
    _b(r"""import asyncio


async def main():
    try:
        async with asyncio.timeout(0.02):
            await asyncio.sleep(1)
    except TimeoutError:
        print("timed out")
    print(await asyncio.wait_for(asyncio.sleep(0.01, "done"), timeout=1))


asyncio.run(main())""",
       "asyncio.timeout cuts a slow wait short"),
    _b(r"""from contextlib import contextmanager

events = []


@contextmanager
def tag(name):
    events.append(f"open {name}")
    try:
        yield name.upper()
    finally:
        events.append(f"close {name}")


with tag("a") as a, tag("b") as b:
    events.append(a + b)
print(events)""",
       "a context manager written as a generator"),
    _b(r"""from contextlib import ExitStack, suppress

with suppress(ZeroDivisionError):
    print(1 / 0)
    print("never")
with ExitStack() as stack:
    stack.callback(print, "closing 1")
    stack.callback(print, "closing 2")
    print("working")
print("done")""",
       "suppress, and an ExitStack that closes in reverse"),
    _b(r"""def main(argv=None):
    rows = [("notes.txt", 1536), ("photo.jpg", 2_480_000), ("a.py", 90)]
    for name, size in rows:
        print(f"{name:<12}{size:>10,} {size / 1024:7.1f} KiB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())""",
       "a size table, behind the main guard"),
    _b(r"""import os
import shlex

os.environ["CC_DEMO"] = "1"
cmd = "python -m venv '.venv 2' --prompt demo"
print(shlex.split(cmd))
print(os.environ.get("CC_DEMO"), os.environ.get("CC_NOPE", "unset"))
print(shlex.join(["pip", "install", "my pkg"]))""",
       "environment variables and splitting a command line"),
)
