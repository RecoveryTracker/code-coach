/**
 * Does a saved buffer come back only under the exercise it was written for?
 *
 * The editor can't be read from a test, so the logic is run directly instead
 * of looked at through Monaco. This is the check the browser could not give.
 */
const path = require("path");
const drafts = require(path.join(process.env.DRAFTS_OUT, "drafts.js"));

// A stub store, so this is the real code path and not a re-implementation.
const mem = new Map();
globalThis.localStorage = {
  getItem: (k) => (mem.has(k) ? mem.get(k) : null),
  setItem: (k, v) => mem.set(k, String(v)),
  removeItem: (k) => mem.delete(k),
  key: (i) => [...mem.keys()][i] ?? null,
  get length() {
    return mem.size;
  },
};

const { stampOf, loadDraft, saveDraft, clearDraft, draftKey } = drafts;

let failures = 0;
function check(name, got, want) {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  if (!ok) failures++;
  console.log(`${ok ? "ok  " : "FAIL"}  ${name}`);
  if (!ok) console.log(`        got ${JSON.stringify(got)} want ${JSON.stringify(want)}`);
}

const TWO_SUM = "def two_sum(nums, target):";
const PALINDROME = "def is_palindrome(s):";

const slot = (over = {}) => ({
  drillId: "lc-hashing",
  index: 3,
  level: 3,
  language: "python",
  window: 0,
  stamp: stampOf(TWO_SUM),
  ...over,
});

// 1. Your own work comes back.
saveDraft(slot(), "my half-finished answer");
check("a draft returns under the exercise it was written for",
  loadDraft(slot()), "my half-finished answer");

// 2. The reported bug: same position, different problem.
check("a draft is refused when the position now means another problem",
  loadDraft(slot({ stamp: stampOf(PALINDROME) })), null);

// 3. The exact shape of the bug: window 0 ex 3 must not leak into window 5 ex 3.
mem.clear();
saveDraft(slot({ window: 0 }), "window zero work");
check("window 0's buffer does not surface in window 5",
  loadDraft(slot({ window: 5, stamp: stampOf(PALINDROME) })), null);
check("...and not even at the same stamp, because the key differs",
  loadDraft(slot({ window: 5 })), null);

// 4. Buffers written before stamping cannot be attributed, so they go.
mem.clear();
mem.set(draftKey(slot()), "plain string from an older build");
check("an unstamped legacy buffer is dropped rather than guessed at",
  loadDraft(slot()), null);

// 5. Two problems that happen to start the same way are the same target.
//    (Stamps are content, not position — this is the intended behaviour.)
mem.clear();
saveDraft(slot(), "shared");
check("an identical target at a different index is a different slot",
  loadDraft(slot({ index: 4 })), null);

// 6. Nothing survives a clear.
mem.clear();
saveDraft(slot(), "x");
clearDraft(slot());
check("clearing removes it", loadDraft(slot()), null);

// 7. Languages don't cross.
mem.clear();
saveDraft(slot({ language: "python" }), "python answer");
check("a python buffer stays out of the dart editor",
  loadDraft(slot({ language: "dart" })), null);

// 8. Round trip through every level.
mem.clear();
for (let lv = 1; lv <= 5; lv++) saveDraft(slot({ level: lv }), `level ${lv}`);
for (let lv = 1; lv <= 5; lv++) {
  check(`level ${lv} keeps its own buffer`, loadDraft(slot({ level: lv })), `level ${lv}`);
}

// 9. Position memory survives, and stays per window.
drafts.savePos("lc-hashing", 3, 6, "python", 2);
check("position comes back", drafts.loadPos("lc-hashing", 3, "python", 2), 6);
check("another window has its own position",
  drafts.loadPos("lc-hashing", 3, "python", 0), null);

// 10. Clear-all takes drafts and positions, nothing else.
mem.set("code-coach:free", "my scratch script");
mem.set("code-coach:saved:hello", "print('hi')");
saveDraft(slot(), "work");
drafts.clearAllDrafts();
check("clear-all leaves saved scripts alone",
  [...mem.keys()].sort(), ["code-coach:free", "code-coach:saved:hello"]);

// 11. Two exercises that open with the same line are still told apart, because
//     the waypoint id goes into the stamp. This is the case a prose-only
//     fingerprint would have missed.
mem.clear();
const twinA = { id: "lc-hashing-1", label: "return []" };
const twinB = { id: "lc-hashing-217", label: "return []" };
check("two waypoints share a first line but not a stamp",
  stampOf(twinA) === stampOf(twinB), false);
saveDraft(slot({ stamp: stampOf(twinA) }), "answer to the first one");
check("...so the twin does not inherit it",
  loadDraft(slot({ stamp: stampOf(twinB) })), null);
check("...and the original still opens",
  loadDraft(slot({ stamp: stampOf(twinA) })), "answer to the first one");

// 12. Same id, re-cut content — the other direction.
mem.clear();
saveDraft(slot({ stamp: stampOf({ id: "lc-2-abc", label: "old wording" }) }), "old");
check("a re-cut exercise under the same id is refused",
  loadDraft(slot({ stamp: stampOf({ id: "lc-2-abc", label: "new wording" }) })), null);

// 13. An id survives a reload unchanged, so work survives with it.
check("the same waypoint stamps the same way twice",
  stampOf(twinA) === stampOf({ id: "lc-hashing-1", label: "return []" }), true);

// 14. A drill with no waypoints keeps working as it always did.
mem.clear();
check("nothing to stamp is the empty stamp", stampOf(undefined), "");
check("...and so is an empty waypoint", stampOf({}), "");
saveDraft(slot({ stamp: stampOf(undefined) }), "unstamped work");
check("an unstamped drill still round-trips",
  loadDraft(slot({ stamp: stampOf(undefined) })), "unstamped work");

console.log(failures ? `\n${failures} failing` : "\nall good");
process.exit(failures ? 1 : 0);
