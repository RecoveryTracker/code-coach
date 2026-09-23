"""The local PostgreSQL, started on demand.

SQLite needed none of this: it is a file, and the runner opens it. A
real PostgreSQL is a server, which is the whole reason it is worth
learning and also the reason it takes a hundred lines to get to the
first query.

What this does not do is as deliberate as what it does. No installer,
no Windows service, no admin rights, nothing on the machine outside
this project's .tools directory. The cluster lives beside the binaries,
listens on 127.0.0.1 only, and uses a port nobody else would pick — so
a real PostgreSQL installed later for work cannot collide with it, and
neither can reach the network. Undoing all of it is deleting a folder.

Why a real one rather than pretending
-------------------------------------
The features worth practising are the ones SQLite does not have:
RETURNING, ILIKE, ON CONFLICT, ::casts, generate_series, JSONB, real
window functions. A dialect emulated on SQLite would be a set of
answers this app made up, which is exactly the thing the rest of the
project refuses to do. If PostgreSQL is going to be taught here, then
PostgreSQL has to be the one answering.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path

#: Where the downloaded toolchains live, beside the Node runtime.
TOOLS = Path(__file__).resolve().parent.parent / ".tools"

#: Deliberately not 5432. A PostgreSQL installed for work owns that one,
#: and this must never be the thing standing in its way.
PORT = 55432
HOST = "127.0.0.1"
USER = "coach"
PASSWORD = "coach"
DATABASE = "coach"

#: How long to wait for the server to answer before giving up.
#:
#: Starting it is a second or two cold. The long case is the first start
#: after the machine went down with the server running, when it replays
#: its log and syncs its files before accepting anyone - usually a few
#: seconds more, longer on a slow disk. That is a start that is working,
#: not a failure, so the budget covers it; past this it really is stuck.
START_TIMEOUT = 60.0


def home() -> Path | None:
    """Where PostgreSQL's binaries are, or None if there are none.

    PATH first, so a real installation is preferred over ours — if
    somebody has PostgreSQL for work, practising against that one is
    better than practising against a copy.
    """
    on_path = shutil.which("pg_ctl")
    if on_path:
        return Path(on_path).parent.parent
    local = TOOLS / "pgsql"
    return local if (local / "bin").exists() else None


def _binary(name: str) -> Path | None:
    base = home()
    if base is None:
        return None
    for suffix in (".exe", ""):
        found = base / "bin" / f"{name}{suffix}"
        if found.exists():
            return found
    return None


def data_dir() -> Path:
    return TOOLS / "pgdata"


def log_file() -> Path:
    """Where the server writes its log - beside the data, never in it.

    It used to be pgdata/server.log, and that cost a failed start every
    time the machine went down with the server still running. After an
    unclean shutdown PostgreSQL syncs every file in its data directory
    before it will accept a connection. On Windows the log is held open
    by the server writing it, so the sync hit a sharing violation on it
    and retried for thirty seconds - longer than the start was allowed
    to take. The server did come up, just after the app had given up
    and reported "Could not start PostgreSQL". Outside the directory,
    the sync never touches it.
    """
    return TOOLS / "pgdata.log"


def available() -> bool:
    """Whether there is anything to run at all."""
    return _binary("psql") is not None


def initialised() -> bool:
    return (data_dir() / "PG_VERSION").exists()


def env() -> dict:
    """The environment psql wants, without a password on a command line.

    PGPASSWORD rather than an argument: arguments are visible to anyone
    who can list processes, and while this password guards a practice
    database on loopback, putting one in a command line is a habit
    worth not having.
    """
    return {
        **os.environ,
        "PGPASSWORD": PASSWORD,
        "PGCLIENTENCODING": "UTF8",
        # Without this, a timestamptz prints in whatever timezone the
        # machine is set to — so the same query gives 09:30+00 here and
        # 01:30-08 there, and every exercise with a time in it becomes
        # a test of where you live. UTC is the only answer that is the
        # same everywhere, and "stored in UTC, shown in a zone" is the
        # thing about timestamptz worth learning anyway.
        "PGTZ": "UTC",
    }


def running() -> bool:
    """Whether something answers on our port."""
    ready = _binary("pg_isready")
    if ready is None:
        return False
    try:
        done = subprocess.run(
            [str(ready), "-h", HOST, "-p", str(PORT)],
            capture_output=True, timeout=10, text=True, errors="replace",
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return done.returncode == 0


def start() -> tuple[bool, str]:
    """Start it if it is not already up. (ok, what went wrong)."""
    if running():
        return True, ""
    if not available():
        return False, (
            "PostgreSQL is not installed. See tools/get_postgres.py for "
            "the local one, or install PostgreSQL and put psql on PATH."
        )
    if not initialised():
        return False, (
            "The practice database has not been created yet. Run "
            "tools/get_postgres.py to set it up."
        )
    ctl = _binary("pg_ctl")
    if ctl is None:
        return False, "pg_ctl is missing from the PostgreSQL install."
    try:
        subprocess.run(
            [
                str(ctl), "-D", str(data_dir()),
                "-o", f"-p {PORT} -h {HOST}",
                "-l", str(log_file()),
                # Launch and return, rather than have pg_ctl wait for
                # the server itself. Its wait has its own clock that
                # knows nothing about ours: a start that ran long - a
                # recovery after a crash - came back as a timeout from
                # pg_ctl while the server was still happily coming up.
                # Asking the server whether it is ready, below, is the
                # only answer that means anything.
                "-W",
                "start",
            ],
            # Not capture_output, and this is the whole bug.
            #
            # pg_ctl starts the server and exits. The server inherits
            # whatever handles pg_ctl had, so with pipes here the server
            # holds the write end open for as long as it runs — which is
            # the point of a server. communicate() then waits for an EOF
            # that is never coming, and `timeout` does not save it: the
            # timeout fires, Python goes to join the reader threads, and
            # those threads are the ones blocked on the pipe.
            #
            # It hung the whole suite three times and looked random,
            # because it only happens when the server was not already
            # running — every other call finds it up and returns in a
            # tenth of a second.
            #
            # Nothing is lost by discarding the output: -l already sends
            # the server's log to a file, and pg_ctl's own chatter is
            # "waiting for server to start.... done".
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            timeout=START_TIMEOUT,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f"Could not start PostgreSQL: {exc}"

    # pg_ctl returns before the server is necessarily accepting
    # connections, so the answer to "is it up" is asking it.
    deadline = time.time() + START_TIMEOUT
    while time.time() < deadline:
        if running():
            return True, ""
        time.sleep(0.3)
    return False, (
        f"PostgreSQL did not start within {START_TIMEOUT:.0f} seconds. "
        f"Its log is {log_file()}, and the last lines say why."
    )


def stop() -> None:
    """Stop it, for tests and for tidying up. Never called on a query."""
    ctl = _binary("pg_ctl")
    if ctl is None or not initialised():
        return
    try:
        subprocess.run(
            [str(ctl), "-D", str(data_dir()), "-m", "fast", "stop"],
            capture_output=True, timeout=30, text=True, errors="replace",
        )
    except (OSError, subprocess.SubprocessError):
        pass
