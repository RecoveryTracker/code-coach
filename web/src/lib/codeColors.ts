/**
 * A tiny syntax colourer for the short programs on a Gotchas card.
 *
 * Not a parser: it cuts source text into runs a stylesheet can colour (comments, strings, numbers,
 * keywords, the constants True/None/null, names being called), and every character of the input ends
 * up in exactly one run, so joining the runs gives the source back. The card renders the runs as real
 * text in a <pre>, so the code can still be selected, read by a screen reader and copied.
 */

export type Kind = "plain" | "space" | "keyword" | "const" | "string" | "number" | "comment" | "fn" | "punct";

export interface Run {
  text: string;
  kind: Kind;
}

const PY_KEYWORDS = new Set(
  ("and as assert async await break class continue def del elif else except finally for from global if import "
    + "in is lambda nonlocal not or pass raise return try while with yield").split(" "),
);
const PY_CONSTS = new Set(["True", "False", "None"]);
const JS_KEYWORDS = new Set(
  ("async await break case catch class const continue default delete do else export extends finally for from "
    + "function if import in instanceof let new of return static super switch this throw try typeof var void "
    + "while with yield").split(" "),
);
const JS_CONSTS = new Set(["true", "false", "null", "undefined", "NaN", "Infinity"]);

const IDENT_START = /[A-Za-z_$]/;
const IDENT = /[A-Za-z0-9_$]/;
const DIGIT = /[0-9]/;

/** Cut `code` into coloured runs. `language` is "python" or "javascript" (anything else reads as Python). */
export function tokenize(code: string, language: string): Run[] {
  const js = language === "javascript";
  const keywords = js ? JS_KEYWORDS : PY_KEYWORDS;
  const consts = js ? JS_CONSTS : PY_CONSTS;
  const runs: Run[] = [];
  const push = (text: string, kind: Kind) => {
    if (text === "") return;
    const last = runs[runs.length - 1];
    if (last && last.kind === kind && (kind === "space" || kind === "punct" || kind === "plain")) {
      last.text += text;
    } else {
      runs.push({ text, kind });
    }
  };

  let i = 0;
  const n = code.length;
  while (i < n) {
    const ch = code[i];

    if (ch === " " || ch === "\t" || ch === "\n" || ch === "\r") {
      let j = i + 1;
      while (j < n && " \t\n\r".includes(code[j])) j++;
      push(code.slice(i, j), "space");
      i = j;
      continue;
    }

    // Comments.
    if ((!js && ch === "#") || (js && ch === "/" && code[i + 1] === "/")) {
      let j = i;
      while (j < n && code[j] !== "\n") j++;
      push(code.slice(i, j), "comment");
      i = j;
      continue;
    }
    if (js && ch === "/" && code[i + 1] === "*") {
      const end = code.indexOf("*/", i + 2);
      const j = end === -1 ? n : end + 2;
      push(code.slice(i, j), "comment");
      i = j;
      continue;
    }

    // Strings, with Python's prefixes (f"..", rb'..') and triple quotes.
    let quoteAt = -1;
    if (ch === '"' || ch === "'" || (js && ch === "`")) {
      quoteAt = i;
    } else if (!js && /[A-Za-z]/.test(ch)) {
      let j = i;
      while (j < n && j - i < 3 && /[A-Za-z]/.test(code[j])) j++;
      if (j < n && (code[j] === '"' || code[j] === "'") && /^(?:[rRbBuUfF]|[rR][bBfF]|[bBfF][rR])$/.test(code.slice(i, j))) {
        quoteAt = j;
      }
    }
    if (quoteAt !== -1) {
      const q = code[quoteAt];
      const triple = !js && code.startsWith(q.repeat(3), quoteAt);
      const closer = triple ? q.repeat(3) : q;
      let j = quoteAt + closer.length;
      while (j < n) {
        if (code[j] === "\\") {
          j += 2;
          continue;
        }
        if (code.startsWith(closer, j)) {
          j += closer.length;
          break;
        }
        if (!triple && !(js && q === "`") && code[j] === "\n") break; // an unclosed string ends at the line
        j++;
      }
      j = Math.min(j, n);
      push(code.slice(i, j), "string");
      i = j;
      continue;
    }

    // Numbers.
    if (DIGIT.test(ch) || (ch === "." && DIGIT.test(code[i + 1] ?? ""))) {
      let j = i + 1;
      while (j < n && (/[0-9A-Za-z_.]/.test(code[j]))) {
        // 1e-5 / 1E+5: a sign belongs to the number right after an exponent letter
        j++;
        if ((code[j - 1] === "e" || code[j - 1] === "E") && (code[j] === "-" || code[j] === "+") && !/[xX]/.test(code.slice(i, j))) j++;
      }
      push(code.slice(i, j), "number");
      i = j;
      continue;
    }

    // Names.
    if (IDENT_START.test(ch)) {
      let j = i + 1;
      while (j < n && IDENT.test(code[j])) j++;
      const word = code.slice(i, j);
      let k = j;
      while (k < n && (code[k] === " " || code[k] === "\t")) k++;
      const afterDot = i > 0 && code[i - 1] === ".";
      if (consts.has(word) && !afterDot) push(word, "const");
      else if (keywords.has(word) && !afterDot) push(word, "keyword");
      else if (code[k] === "(" && k === j) push(word, "fn");
      else push(word, "plain");
      i = j;
      continue;
    }

    push(ch, /[()[\]{},.:;=<>+\-*/%!&|^~?@]/.test(ch) ? "punct" : "plain");
    i++;
  }
  return runs;
}

/** The source back from its runs (the invariant the tests hold). */
export function join(runs: readonly Run[]): string {
  return runs.map((r) => r.text).join("");
}
