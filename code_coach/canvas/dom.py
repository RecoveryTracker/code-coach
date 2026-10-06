"""Pages for the steps that run on a web page rather than a canvas (To-do).

A canvas step's check runs in node against a stand-in canvas. A page step's
check cannot: a homemade DOM would pass code that a browser fails, and fail
code a browser passes. So it runs in a real browser - in Code Coach, in a
hidden sandboxed frame beside the preview, which posts the verdict back; in
the tests, in headless Chrome, with the frames sandboxed the same way.

Both load the page built here: the step's HTML and stylesheet, the harness
(dom_harness.js), and your code, which the harness puts in at the end of
the body as <script src="app.js"> would be.
"""

from __future__ import annotations

import html as html_lib
import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from code_coach.canvas.content import Step

HERE = Path(__file__).resolve().parent
HARNESS = HERE / "dom_harness.js"

#: The preview may submit forms - the harness catches one that would leave
#: the page and Code Coach loads the page again, as a browser would. A
#: check's frame may not: there the harness fires a submit's events itself,
#: so nothing a check does can take the page away mid-check.
PLAY_SANDBOX = "allow-scripts allow-forms"
CHECK_SANDBOX = "allow-scripts"

#: The size a check's page is laid out at, here and in Code Coach.
CHECK_WIDTH = 480
CHECK_HEIGHT = 640


def harness_source() -> str:
    return HARNESS.read_text(encoding="utf-8")


def _script_json(value: object) -> str:
    """JSON that is safe inside a <script>: nothing in it can close the tag."""
    return (
        json.dumps(value, ensure_ascii=False)
        .replace("<", "\\u003c")
        .replace("\u2028", "\\u2028")
        .replace("\u2029", "\\u2029")
    )


def page(
    step: Step,
    code: str,
    mode: str = "play",
    storage: dict[str, str] | None = None,
    token: str = "",
) -> str:
    """The whole document for one step, with `code` as app.js.

    `mode` is 'play' for the preview, which starts with `storage` in its
    localStorage, or 'check', which starts with none and runs the step's
    check once the page has loaded, posting {type: 'result'} to its parent.
    Every message the page posts carries `token` as its id.
    """
    data = {
        "mode": mode,
        "code": code,
        "check": step.check if mode == "check" else "",
        "storage": dict(storage or {}) if mode == "play" else {},
        "html": step.html,
        "id": token,
    }
    return (
        "<!doctype html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '<meta charset="utf-8">\n'
        f"<title>{html_lib.escape(page_title(step))}</title>\n"
        f"<style>\n{step.css}\n</style>\n"
        f"<script>\n{harness_source()}\n</script>\n"
        "</head>\n"
        "<body>\n"
        f"{step.html}\n"
        f"<script>__ccDom.boot({_script_json(data)})</script>\n"
        "</body>\n"
        "</html>\n"
    )


def page_title(step: Step) -> str:
    """The page's <title>: its first heading's text, as written in the HTML."""
    found = re.search(r"<h1[^>]*>(.*?)</h1>", step.html, re.S)
    return html_lib.unescape(re.sub(r"<[^>]+>", "", found.group(1))).strip() if found else "Page"


def source_html(step: Step) -> str:
    """index.html as you read it: the page as it would be written by hand."""
    body = "\n".join("  " + line if line else line for line in step.html.strip("\n").split("\n"))
    return (
        "<!doctype html>\n"
        '<html lang="en">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        f"  <title>{html_lib.escape(page_title(step))}</title>\n"
        '  <link rel="stylesheet" href="style.css">\n'
        "</head>\n"
        "<body>\n"
        f"{body}\n"
        '  <script src="app.js"></script>\n'
        "</body>\n"
        "</html>\n"
    )


# ── Headless Chrome, for the tests ────────────────────────────────────

_CHROME_PLACES = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
)


def find_chrome() -> str | None:
    """Google Chrome or Chromium, wherever it is; None when there is none."""
    for name in ("chrome", "google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            return found
    for place in _CHROME_PLACES:
        if Path(place).is_file():
            return place
    return None


def _host(pages: dict[str, str | tuple[str, str]]) -> str:
    """One page holding every page given, each in a sandboxed frame - a
    check's, unless a page comes with a sandbox of its own - writing down
    every message they post, by id."""
    frames: list[str] = []
    for given in pages.values():
        doc, sandbox = given if isinstance(given, tuple) else (given, CHECK_SANDBOX)
        frames.append(
            f'<iframe sandbox="{sandbox}" width="{CHECK_WIDTH}" height="{CHECK_HEIGHT}" '
            f'srcdoc="{html_lib.escape(doc, quote=True)}"></iframe>'
        )
    body = "\n".join(frames)
    # Listening from the <head>: a frame can finish its check and post
    # before the parser has reached anything after it.
    return (
        "<!doctype html><html><head><meta charset='utf-8'><title>checks</title>\n"
        "<script>\n"
        "const got = {};\n"
        "addEventListener('message', (e) => {\n"
        "  const d = e.data;\n"
        "  if (!d || !d.cc) return;\n"
        "  (got[d.id] = got[d.id] || []).push(d);\n"
        "  const out = document.getElementById('got');\n"
        "  if (out) out.textContent = JSON.stringify(got);\n"
        "});\n"
        "</script></head><body>\n"
        "<pre id='got'></pre>\n"
        f"{body}\n"
        "</body></html>\n"
    )


def run_pages(pages: dict[str, str | tuple[str, str]], timeout: float = 180) -> dict[str, list[dict]]:
    """Load every page in one headless Chrome and return what each posted.

    Keys are the tokens the pages were built with; a page is its document,
    or (document, sandbox) to load it the way the preview is. The frames run in the
    page's own process, under virtual time, so Chrome finishes every task
    they queue - every check, however slow the machine - before it prints
    the page; a page that posted nothing is simply missing from the result.
    """
    chrome = find_chrome()
    if chrome is None:
        raise RuntimeError("headless checks need Google Chrome or Chromium")
    work = Path(tempfile.mkdtemp(prefix="cc-dom-"))
    try:
        host = work / "checks.html"
        host.write_text(_host(pages), encoding="utf-8")
        args = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions",
            f"--user-data-dir={work / 'profile'}",
            # Frames in the page's own process, so virtual time covers them.
            "--disable-features=IsolateSandboxedIframes",
            "--disable-site-isolation-trials",
            "--virtual-time-budget=60000",
            "--dump-dom",
            host.as_uri(),
        ]
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        try:
            out, _ = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            _kill_tree(proc)
            raise
        text = out.decode("utf-8", "replace")
        found = re.search(r'<pre id="got">(.*?)</pre>', text, re.S)
        if not found or not found.group(1).strip():
            return {}
        return json.loads(html_lib.unescape(found.group(1)))
    finally:
        shutil.rmtree(work, ignore_errors=True)


def _kill_tree(proc: subprocess.Popen) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
    else:
        proc.kill()
    proc.wait()


def check_pages(cases: dict[str, tuple[Step, str]], timeout: float = 180) -> dict[str, dict]:
    """Check each (step, code) in headless Chrome: {passed, message} by key.

    A case whose page never reported comes back failed, saying so.
    """
    pages = {key: page(step, code, mode="check", token=key) for key, (step, code) in cases.items()}
    got = run_pages(pages, timeout=timeout)
    results: dict[str, dict] = {}
    for key in cases:
        result = next((m for m in got.get(key, []) if m.get("type") == "result"), None)
        results[key] = (
            {"passed": bool(result["passed"]), "message": str(result.get("message", ""))}
            if result
            else {"passed": False, "message": "the page never reported a result"}
        )
    return results
