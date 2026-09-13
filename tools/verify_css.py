"""Check every CSS quiz against a real browser.

    python tools/verify_css.py && start scratch/css_check.html

Writes a page that renders each quiz in its own 800x300 iframe, asks
getComputedStyle for the property the quiz is about, and compares the
answer with what the quiz claims. Disagreements are listed first and in
red, with both values, so a wrong expectation is a thing you read rather
than a thing you have to go looking for.

Why a page rather than a test
-----------------------------
There is no browser engine in this project and the half-built ones get
the cascade wrong, so a passing check against one of those would mean
less than no check at all. The only honest oracle for "what does the
browser compute" is a browser. This is that, in the smallest form that
can be re-run in ten seconds whenever a quiz changes.

The pytest suite does the part that does not need an engine: it asserts
every quiz in the content files reaches this page, so none can be added
and quietly skipped.

The iframe is 800px wide on purpose. One quiz resolves a percentage
against the initial containing block, so the answer depends on the
viewport, and a fixed frame makes that answer stable.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from code_coach.css import quizzes  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "scratch" / "css_check.html"

FRAME_WIDTH = 800
FRAME_HEIGHT = 300

PAGE = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>CSS quiz check</title>
<style>
  body { font: 14px system-ui, sans-serif; margin: 24px; }
  h1 { font-size: 18px; }
  #summary { font-size: 16px; font-weight: 600; margin: 12px 0 20px; }
  table { border-collapse: collapse; width: 100%; }
  th, td { text-align: left; padding: 6px 10px; border-bottom: 1px solid #ddd;
           vertical-align: top; font-family: ui-monospace, monospace; }
  th { font-family: system-ui, sans-serif; }
  tr.bad td { background: #ffe9e9; color: #8a0000; }
  tr.ok td { color: #333; }
  iframe { position: absolute; left: -9999px; top: 0;
           width: WIDTHpx; height: HEIGHTpx; border: 0; }
</style>
</head>
<body>
<h1>CSS quiz check</h1>
<div id="summary">measuring...</div>
<table>
  <thead><tr>
    <th>quiz</th><th>property</th><th>recorded</th><th>browser says</th>
  </tr></thead>
  <tbody id="rows"></tbody>
</table>
<h2>record</h2>
<pre id="record"></pre>
<script>
const QUIZZES = QUIZDATA;

function measure(q) {
  return new Promise((resolve) => {
    const frame = document.createElement("iframe");
    frame.setAttribute("sandbox", "allow-same-origin");
    frame.srcdoc = q.page;
    frame.onload = () => {
      let got;
      try {
        const doc = frame.contentDocument;
        const found = doc.querySelectorAll(q.target);
        if (found.length !== 1) {
          got = `selector matched ${found.length} elements`;
        } else if (q.prop.startsWith("rect.")) {
          // The space it really takes, for the questions where the
          // computed property reports the declaration and lies.
          const box = found[0].getBoundingClientRect();
          const n = box[q.prop.slice(5)];
          got = `${Math.round(n * 100) / 100}px`;
        } else {
          got = frame.contentWindow
            .getComputedStyle(found[0])
            .getPropertyValue(q.prop)
            .trim();
        }
      } catch (err) {
        got = `could not measure: ${err.message}`;
      }
      frame.remove();
      resolve(got);
    };
    document.body.appendChild(frame);
  });
}

(async () => {
  const results = [];
  for (const q of QUIZZES) {
    const got = await measure(q);
    results.push({ q, got, ok: got === q.expect });
  }
  // Disagreements first: the whole point is not having to hunt.
  results.sort((a, b) => Number(a.ok) - Number(b.ok));

  const rows = document.getElementById("rows");
  for (const r of results) {
    const tr = document.createElement("tr");
    tr.className = r.ok ? "ok" : "bad";
    for (const cell of [r.q.id, r.q.prop, r.q.expect, r.got]) {
      const td = document.createElement("td");
      td.textContent = cell;
      tr.appendChild(td);
    }
    rows.appendChild(tr);
  }

  // What the suite reads back. The hash is of the exact document
  // measured, so editing a quiz's markup or styles without coming back
  // here leaves a record that no longer matches and a failing test.
  window.__record = results.map((r) => ({
    id: r.q.id,
    prop: r.q.prop,
    page_sha256: r.q.sha,
    browser_value: r.got,
  }));
  document.getElementById("record").textContent =
    JSON.stringify(window.__record, null, 1);

  const bad = results.filter((r) => !r.ok).length;
  const line = bad === 0
    ? `ALL AGREE - ${results.length} quizzes`
    : `${bad} DISAGREE of ${results.length}`;
  document.getElementById("summary").textContent = line;
  document.title = line;
})();
</script>
</body>
</html>
"""


def build() -> str:
    data = [
        {
            "id": q.id,
            "target": q.target,
            "prop": q.prop,
            "expect": q.expect,
            "page": q.page(),
            "sha": hashlib.sha256(q.page().encode("utf-8")).hexdigest(),
        }
        for q in quizzes()
    ]
    return (
        PAGE.replace("QUIZDATA", json.dumps(data, ensure_ascii=False))
        .replace("WIDTHpx", f"{FRAME_WIDTH}px")
        .replace("HEIGHTpx", f"{FRAME_HEIGHT}px")
    )


def main() -> None:
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(build(), encoding="utf-8")
    print(f"wrote {OUT} with {len(quizzes())} quizzes")


if __name__ == "__main__":
    main()
