/**
 * A tiny syntax colourer for the short programs on a Gotchas card.
 *
 * Not a parser: it cuts source text into runs a stylesheet can colour (comments, strings, numbers,
 * keywords, the constants True/None/null, C's types and #preprocessor lines, names being called), and every character of the input ends
 * up in exactly one run, so joining the runs gives the source back. The card renders the runs as real
 * text in a <pre>, so the code can still be selected, read by a screen reader and copied.
 */

export type Kind =
  | "plain"
  | "space"
  | "keyword"
  | "const"
  | "string"
  | "number"
  | "comment"
  | "fn"
  | "punct"
  | "type"
  | "preproc";

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

const C_KEYWORDS = new Set(
  ("auto break case const continue default do else enum extern for goto if inline register restrict return "
    + "sizeof static struct switch typedef union volatile while").split(" "),
);
const C_TYPES = new Set(
  ("void char short int long float double signed unsigned bool _Bool size_t ssize_t ptrdiff_t FILE "
    + "int8_t int16_t int32_t int64_t uint8_t uint16_t uint32_t uint64_t intptr_t uintptr_t intmax_t uintmax_t").split(" "),
);
const C_CONSTS = new Set(["NULL", "true", "false", "EOF", "UINT_MAX", "INT_MAX", "INT_MIN", "CHAR_BIT"]);

const IDENT_START = /[A-Za-z_$]/;
const IDENT = /[A-Za-z0-9_$]/;
const DIGIT = /[0-9]/;

/**
 * Cut `code` into coloured runs. `language` is "python", "javascript" or "c" (anything else reads as Python).
 * C's #include / #define lines are one "preproc" run each (up to a comment or the end of the line, a backslash
 * continuing it); its type names are "type".
 */
export function tokenize(code: string, language: string): Run[] {
  const c = language === "c";
  const js = language === "javascript";
  const slashes = js || c; // JavaScript and C share // and /* */ comments
  const keywords = c ? C_KEYWORDS : js ? JS_KEYWORDS : PY_KEYWORDS;
  const consts = c ? C_CONSTS : js ? JS_CONSTS : PY_CONSTS;
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

    // C's preprocessor lines: #include <stdio.h>, #define SQUARE(x) x * x
    if (c && ch === "#") {
      let k = i - 1;
      while (k >= 0 && (code[k] === " " || code[k] === "\t")) k--;
      if (k < 0 || code[k] === "\n") {
        let j = i;
        while (j < n && code[j] !== "\n") {
          if (code[j] === "\\" && code[j + 1] === "\n") {
            j += 2; // a backslash joins the next line to this one
            continue;
          }
          if (code[j] === "/" && (code[j + 1] === "/" || code[j + 1] === "*")) break;
          j++;
        }
        push(code.slice(i, j), "preproc");
        i = j;
        continue;
      }
    }

    // Comments.
    if ((!slashes && ch === "#") || (slashes && ch === "/" && code[i + 1] === "/")) {
      let j = i;
      while (j < n && code[j] !== "\n") j++;
      push(code.slice(i, j), "comment");
      i = j;
      continue;
    }
    if (slashes && ch === "/" && code[i + 1] === "*") {
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
    } else if (!js && !c && /[A-Za-z]/.test(ch)) {
      let j = i;
      while (j < n && j - i < 3 && /[A-Za-z]/.test(code[j])) j++;
      if (j < n && (code[j] === '"' || code[j] === "'") && /^(?:[rRbBuUfF]|[rR][bBfF]|[bBfF][rR])$/.test(code.slice(i, j))) {
        quoteAt = j;
      }
    }
    if (quoteAt !== -1) {
      const q = code[quoteAt];
      const triple = !js && !c && code.startsWith(q.repeat(3), quoteAt);
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
      else if (c && C_TYPES.has(word) && !afterDot) push(word, "type");
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
