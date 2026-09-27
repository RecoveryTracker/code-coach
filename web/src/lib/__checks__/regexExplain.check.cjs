/**
 * Does the pattern explainer say the right thing about real patterns?
 *
 * Run by tests/test_regex_explain.py after compiling regexExplain.ts. The
 * expected readings are written out by hand; PATTERNS (every answer and
 * pitfall in the Regex tasks, passed in as JSON) only has to be read
 * without anything coming back "not understood".
 */
const path = require("path");
const { explainPattern } = require(path.join(process.env.EXPLAIN_OUT, "regexExplain.js"));

let failures = 0;
function check(name, got, want) {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  if (!ok) failures++;
  console.log(`${ok ? "ok  " : "FAIL"}  ${name}`);
  if (!ok) console.log(`        got ${JSON.stringify(got)}\n       want ${JSON.stringify(want)}`);
}
const read = (p) => explainPattern(p).map((x) => [x.text, x.meaning]);

check("letters stay together", read("cat"), [["cat", 'the letters "cat", in that order']]);
check("a counted digit", read("^\\d{3}$"), [
  ["^", "the start of the text"],
  ["\\d{3}", "one digit (0-9), exactly 3 times"],
  ["$", "the end of the text"],
]);
check("a negated set", read("[^aeiou]"), [["[^aeiou]", "one character that is not a, e, i, o or u"]]);
check("a range set, one or more", read("[a-z]+"), [["[a-z]+", "one character: a to z, one or more times"]]);
check("an escaped dot", read("\\d+\\.\\d{2}"), [
  ["\\d+", "one digit (0-9), one or more times"],
  ["\\.", 'a real "." (the backslash makes it plain)'],
  ["\\d{2}", "one digit (0-9), exactly 2 times"],
]);
check("a quantifier binds to one letter only", read("colou?r"), [
  ["colo", 'the letters "colo", in that order'],
  ["u?", 'the character "u", optional - zero or one time'],
  ["r", 'the character "r"'],
]);
check("lazy repeat inside quotes", read('"(.*?)"'), [
  ['"', 'the character """'],
  ["(", "start of group - what it matches is captured (kept)"],
  [".*?", "any one character, zero or more times, as few as possible (lazy)"],
  [")", "end of group"],
  ['"', 'the character """'],
]);
check("alternation", read("cat|dog"), [
  ["cat", 'the letters "cat", in that order'],
  ["|", "OR - either what is before this, or what is after"],
  ["dog", 'the letters "dog", in that order'],
]);
check("a repeated group", read("(ab){2,}"), [
  ["(", "start of group - what it matches is captured (kept)"],
  ["ab", 'the letters "ab", in that order'],
  ["){2,}", "end of group - the whole group, 2 or more times"],
]);
check("a lookahead", read("cat(?!alog)")[1], ["(?!", "start of a negative look-ahead: what follows must NOT match this"]);
check("a stray repeat is called out", read("+a")[0][1], "a repeat with nothing to repeat - put something before it");

const patterns = JSON.parse(process.env.PATTERNS || "[]");
for (const p of patterns) {
  const bad = explainPattern(p).filter((x) => /not understood|never closed|unfinished|nothing to repeat/.test(x.meaning));
  if (bad.length) {
    failures++;
    console.log(`FAIL  task pattern ${JSON.stringify(p)} -> ${JSON.stringify(bad)}`);
  }
}
console.log(`${patterns.length} task patterns read`);

process.exit(failures ? 1 : 0);
