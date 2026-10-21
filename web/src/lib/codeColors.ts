/**
 * A tiny syntax colourer for the short programs on a Gotchas card.
 *
 * Not a parser: it cuts source text into runs a stylesheet can colour (comments, strings, numbers,
 * keywords, constants like True/None/null, type names, #preprocessor lines, names being called), and every
 * character of the input ends up in exactly one run, so joining the runs gives the source back. The card
 * renders the runs as real text in a <pre>, so the code can still be selected, read by a screen reader and
 * copied.
 *
 * It knows no language by name. What a language looks like (its keyword and type sets, its comment and
 * string syntax) is a `Syntax`, which the server sends with /api/gotchas (it is the registry in
 * code_coach/gotchas/langs.py), so adding a language never touches this file.
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

/** One language's colouring rules, as the server sends them. */
export interface Syntax {
  keywords: string[];
  types: string[];
  consts: string[];
  /** What starts a comment that runs to the end of the line ("#", "//", "--", ";"). */
  line: string[];
  /** [open, close] pairs of comments that can span lines. */
  block: string[][];
  /** Characters that open a string; a backtick string may span lines. */
  quotes: string;
  /** Triple-quoted strings. */
  triple: boolean;
  /** Python's string prefixes (f"..", rb'..'). */
  prefixes: boolean;
  /** Lines starting with # are directives (#include, #define). */
  directives: boolean;
  /** A ' opens a string only when it closes within a few characters ('a', '\n'): Rust lifetimes, Lisp quote. */
  charLiterals: boolean;
  ignoreCase: boolean;
  /** Lisp reading: a word runs to a space, bracket, quote or comment. */
  lisp: boolean;
}

/** What an unknown language reads as: strings, numbers, // and # comments, no names coloured. */
export const PLAIN_SYNTAX: Syntax = {
  keywords: [],
  types: [],
  consts: [],
  line: ["//", "#"],
  block: [["/*", "*/"]],
  quotes: "\"'",
  triple: false,
  prefixes: false,
  directives: false,
  charLiterals: false,
  ignoreCase: false,
  lisp: false,
};

interface Compiled {
  syntax: Syntax;
  keywords: Set<string>;
  types: Set<string>;
  consts: Set<string>;
}

const compiled = new WeakMap<Syntax, Compiled>();

function compile(syntax: Syntax): Compiled {
  let c = compiled.get(syntax);
  if (!c) {
    const fold = (words: string[]) => new Set(syntax.ignoreCase ? words.map((w) => w.toLowerCase()) : words);
    c = { syntax, keywords: fold(syntax.keywords), types: fold(syntax.types), consts: fold(syntax.consts) };
    compiled.set(syntax, c);
  }
  return c;
}

const IDENT_START = /[A-Za-z_$]/;
const IDENT = /[A-Za-z0-9_$]/;
const DIGIT = /[0-9]/;
/** 'a', '\n', '\u{1F600}', '\x41': a character literal, as opposed to a lifetime or a quote mark. */
const CHAR_LITERAL = /^'(?:\\(?:u\{[0-9A-Fa-f]+\}|x[0-9A-Fa-f]{2}|u[0-9A-Fa-f]{4}|.)|[^\\'\n])'/;
const LISP_NUMBER = /^[+-]?(?:\d+\.?\d*|\.\d+)(?:[eEdD][+-]?\d+)?$/;
const WS = " \t\n\r";

/**
 * Cut `code` into coloured runs using `syntax` (an unknown language: `PLAIN_SYNTAX`).
 * A directive line (#include <stdio.h>, #define X 1) is one "preproc" run up to a comment or the end of the
 * line, a backslash continuing it; a type name is "type".
 */
export function tokenize(code: string, syntax: Syntax = PLAIN_SYNTAX): Run[] {
  const { keywords, types, consts } = compile(syntax);
  const fold = (w: string) => (syntax.ignoreCase ? w.toLowerCase() : w);
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

  /** The end of a block comment that starts at i, or -1 if none does. */
  const blockEnd = (i: number): number => {
    for (const [open, close] of syntax.block) {
      if (open && code.startsWith(open, i)) {
        const end = code.indexOf(close, i + open.length);
        return end === -1 ? code.length : end + close.length;
      }
    }
    return -1;
  };
  const startsLineComment = (i: number): boolean => syntax.line.some((s) => s !== "" && code.startsWith(s, i));
  const multiline = (q: string) => q === "`";

  let i = 0;
  const n = code.length;
  while (i < n) {
    const ch = code[i];

    if (WS.includes(ch)) {
      let j = i + 1;
      while (j < n && WS.includes(code[j])) j++;
      push(code.slice(i, j), "space");
      i = j;
      continue;
    }

    // Preprocessor / directive lines: #include <stdio.h>, #define SQUARE(x) x * x
    if (syntax.directives && ch === "#") {
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

    // Comments (block first: Lua's --[[ starts like its -- comment).
    const be = blockEnd(i);
    if (be !== -1) {
      push(code.slice(i, be), "comment");
      i = be;
      continue;
    }
    if (startsLineComment(i)) {
      let j = i;
      while (j < n && code[j] !== "\n") j++;
      push(code.slice(i, j), "comment");
      i = j;
      continue;
    }

    // Strings, with Python's prefixes (f"..", rb'..') and triple quotes.
    let quoteAt = -1;
    if (syntax.quotes.includes(ch)) {
      if (ch === "'" && syntax.charLiterals) {
        const m = CHAR_LITERAL.exec(code.slice(i, i + 14));
        if (m) {
          push(m[0], "string");
          i += m[0].length;
          continue;
        }
      } else {
        quoteAt = i;
      }
    } else if (syntax.prefixes && /[A-Za-z]/.test(ch)) {
      let j = i;
      while (j < n && j - i < 3 && /[A-Za-z]/.test(code[j])) j++;
      if (j < n && (code[j] === '"' || code[j] === "'") && /^(?:[rRbBuUfF]|[rR][bBfF]|[bBfF][rR])$/.test(code.slice(i, j))) {
        quoteAt = j;
      }
    }
    if (quoteAt !== -1) {
      const q = code[quoteAt];
      const triple = syntax.triple && q !== "`" && code.startsWith(q.repeat(3), quoteAt);
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
        if (!triple && !multiline(q) && code[j] === "\n") break; // an unclosed string ends at the line
        j++;
      }
      j = Math.min(j, n);
      push(code.slice(i, j), "string");
      i = j;
      continue;
    }

    // Lisp reads words differently: anything up to a space, bracket, quote or comment.
    if (syntax.lisp && !"()'`,;\"".includes(ch)) {
      let j = i + 1;
      while (j < n && !WS.includes(code[j]) && !"()'`,;\"".includes(code[j])) j++;
      const word = code.slice(i, j);
      let p = i - 1;
      while (p >= 0 && WS.includes(code[p])) p--;
      const lower = fold(word);
      if (LISP_NUMBER.test(word)) push(word, "number");
      else if (word.startsWith(":") || consts.has(lower)) push(word, "const");
      else if (keywords.has(lower)) push(word, "keyword");
      else if (types.has(lower)) push(word, "type");
      else if (p >= 0 && code[p] === "(") push(word, "fn");
      else push(word, "plain");
      i = j;
      continue;
    }

    // Numbers.
    if (DIGIT.test(ch) || (ch === "." && DIGIT.test(code[i + 1] ?? ""))) {
      let j = i + 1;
      while (j < n && /[0-9A-Za-z_.]/.test(code[j])) {
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
      const lower = fold(word);
      let k = j;
      while (k < n && (code[k] === " " || code[k] === "\t")) k++;
      const afterDot = i > 0 && code[i - 1] === ".";
      const macro = code[j] === "!" && "([{".includes(code[j + 1] ?? "");
      if (consts.has(lower) && !afterDot) push(word, "const");
      else if (keywords.has(lower) && !afterDot) push(word, "keyword");
      else if (types.has(lower) && !afterDot) push(word, "type");
      else if ((code[k] === "(" && k === j) || macro) push(word, "fn");
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
