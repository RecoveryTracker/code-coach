/**
 * A regular expression, read out loud, one piece at a time.
 *
 * Regex is a string of symbols where every character might mean something,
 * and nothing on screen says which ones do. This reads a pattern left to
 * right and gives each piece its meaning in plain words - "\d{3}" is
 * "exactly 3 digits", "[^aeiou]" is "one character that is not a, e, i, o
 * or u" - so the pattern being typed can be checked against the idea in
 * your head while you type it.
 *
 * It covers what the tasks use: literals, escapes, sets and ranges, the
 * dot, anchors, groups and lookarounds, alternation, and every quantifier,
 * lazy or not. Anything it does not recognise is said to be so, rather
 * than guessed at.
 */

export type Piece = {
  /** The characters of the pattern this piece covers. */
  text: string;
  /** What they mean, in plain words. */
  meaning: string;
  /** How deep inside groups it sits, for indenting. */
  depth: number;
};

const ESCAPES: Record<string, string> = {
  d: "one digit (0-9)",
  D: "one character that is not a digit",
  w: "one word character (a letter, digit or _)",
  W: "one character that is not a word character",
  s: "one space, tab or line break",
  S: "one character that is not a space",
  b: "a word boundary - the edge between a word and a non-word",
  B: "not a word boundary",
  n: "a line break",
  t: "a tab",
};

const SET_ESCAPES: Record<string, string> = {
  d: "any digit",
  D: "anything but a digit",
  w: "any word character",
  W: "anything but a word character",
  s: "any space",
  S: "anything but a space",
};

function listWords(items: string[]): string {
  if (items.length <= 1) return items.join("");
  return `${items.slice(0, -1).join(", ")} or ${items[items.length - 1]}`;
}

/** What a [...] set means. `body` is what is between the brackets. */
function describeSet(body: string): string {
  let negated = false;
  let i = 0;
  if (body.startsWith("^")) {
    negated = true;
    i = 1;
  }
  const parts: string[] = [];
  while (i < body.length) {
    const ch = body[i];
    if (ch === "\\" && i + 1 < body.length) {
      const next = body[i + 1];
      parts.push(SET_ESCAPES[next] ?? `"${next}"`);
      i += 2;
      continue;
    }
    if (body[i + 1] === "-" && i + 2 < body.length) {
      parts.push(`${ch} to ${body[i + 2]}`);
      i += 3;
      continue;
    }
    parts.push(ch === " " ? "a space" : ch);
    i += 1;
  }
  const what = listWords(parts);
  return negated ? `one character that is not ${what}` : `one character: ${what}`;
}

/** The quantifier at `at`, if there is one: [text, meaning]. */
function readQuantifier(pattern: string, at: number): [string, string] | null {
  const ch = pattern[at];
  let text = "";
  let meaning = "";
  if (ch === "*") {
    text = "*";
    meaning = "zero or more times";
  } else if (ch === "+") {
    text = "+";
    meaning = "one or more times";
  } else if (ch === "?") {
    text = "?";
    meaning = "optional - zero or one time";
  } else if (ch === "{") {
    const found = /^\{(\d+)(,(\d*))?\}/.exec(pattern.slice(at));
    if (!found) return null;
    text = found[0];
    const low = found[1];
    if (found[2] === undefined) meaning = `exactly ${low} time${low === "1" ? "" : "s"}`;
    else if (found[3] === "") meaning = `${low} or more times`;
    else meaning = `between ${low} and ${found[3]} times`;
  } else {
    return null;
  }
  if (pattern[at + text.length] === "?") {
    text += "?";
    meaning += ", as few as possible (lazy)";
  }
  return [text, meaning];
}

/** Turn "one digit" + "exactly 3 times" into "exactly 3 digits"-ish words. */
function combine(atom: string, times: string): string {
  return `${atom}, ${times}`;
}

export function explainPattern(pattern: string): Piece[] {
  const pieces: Piece[] = [];
  let depth = 0;
  let i = 0;
  let literal = "";

  const flushLiteral = () => {
    if (!literal) return;
    pieces.push({
      text: literal,
      meaning: literal.length === 1
        ? `the character "${literal}"`
        : `the letters "${literal}", in that order`,
      depth,
    });
    literal = "";
  };

  /** Add an atom, folding in a quantifier that follows it. */
  const addAtom = (text: string, meaning: string, next: number) => {
    const q = readQuantifier(pattern, next);
    if (q) {
      pieces.push({ text: text + q[0], meaning: combine(meaning, q[1]), depth });
      return next + q[0].length;
    }
    pieces.push({ text, meaning, depth });
    return next;
  };

  while (i < pattern.length) {
    const ch = pattern[i];

    // A plain character, unless a quantifier follows - then it stands alone.
    const special = "\\[]().*+?{}|^$";
    if (!special.includes(ch)) {
      if (readQuantifier(pattern, i + 1)) {
        flushLiteral();
        i = addAtom(ch, `the character "${ch}"`, i + 1);
      } else {
        literal += ch;
        i += 1;
      }
      continue;
    }
    flushLiteral();

    if (ch === "\\") {
      const next = pattern[i + 1];
      if (next === undefined) {
        pieces.push({ text: "\\", meaning: "a backslash with nothing after it - unfinished", depth });
        break;
      }
      const meaning = ESCAPES[next] ?? `a real "${next}" (the backslash makes it plain)`;
      i = addAtom(`\\${next}`, meaning, i + 2);
      continue;
    }
    if (ch === "[") {
      const close = pattern.indexOf("]", i + 2);
      if (close === -1) {
        pieces.push({ text: pattern.slice(i), meaning: "a set that is never closed with ]", depth });
        break;
      }
      const text = pattern.slice(i, close + 1);
      i = addAtom(text, describeSet(pattern.slice(i + 1, close)), close + 1);
      continue;
    }
    if (ch === ".") {
      i = addAtom(".", "any one character", i + 1);
      continue;
    }
    if (ch === "^") {
      pieces.push({ text: "^", meaning: "the start of the text", depth });
      i += 1;
      continue;
    }
    if (ch === "$") {
      pieces.push({ text: "$", meaning: "the end of the text", depth });
      i += 1;
      continue;
    }
    if (ch === "|") {
      pieces.push({ text: "|", meaning: "OR - either what is before this, or what is after", depth });
      i += 1;
      continue;
    }
    if (ch === "(") {
      const rest = pattern.slice(i);
      const kinds: [string, string][] = [
        ["(?:", "start of a group that is not captured - just for grouping"],
        ["(?=", "start of a look-ahead: what follows must match this, but is not taken"],
        ["(?!", "start of a negative look-ahead: what follows must NOT match this"],
        ["(?<=", "start of a look-behind: what comes before must match this"],
        ["(?<!", "start of a negative look-behind: what comes before must NOT match this"],
      ];
      const named = /^\(\?<([A-Za-z_]\w*)>/.exec(rest);
      const kind = kinds.find(([open]) => rest.startsWith(open));
      if (named) {
        pieces.push({ text: named[0], meaning: `start of a group named "${named[1]}" - what it matches is kept`, depth });
        i += named[0].length;
      } else if (kind) {
        pieces.push({ text: kind[0], meaning: kind[1], depth });
        i += kind[0].length;
      } else {
        pieces.push({ text: "(", meaning: "start of group - what it matches is captured (kept)", depth });
        i += 1;
      }
      depth += 1;
      continue;
    }
    if (ch === ")") {
      depth = Math.max(0, depth - 1);
      const q = readQuantifier(pattern, i + 1);
      if (q) {
        pieces.push({ text: `)${q[0]}`, meaning: `end of group - the whole group, ${q[1]}`, depth });
        i += 1 + q[0].length;
      } else {
        pieces.push({ text: ")", meaning: "end of group", depth });
        i += 1;
      }
      continue;
    }
    // A quantifier with nothing before it, or a stray bracket.
    pieces.push({
      text: ch,
      meaning: "*+?{".includes(ch)
        ? "a repeat with nothing to repeat - put something before it"
        : `"${ch}" - not understood here`,
      depth,
    });
    i += 1;
  }
  flushLiteral();
  return pieces;
}
