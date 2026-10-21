/**
 * "Add a quiz I found": paste a program from a quiz post, optionally type the options you saw and
 * say which you think is right, and the server runs it for real. What it actually printed is the
 * right answer, whatever the post (or you) said; blank options are filled only with honest
 * misreads, or left out. Everything here is typed or pasted by you - nothing is fetched.
 *
 * Your cards live in gotchas_user.json beside the progress file, come up in the same feed with a
 * "Yours" badge (the first one right after you add it), and can be deleted again.
 */

import { useCallback, useEffect, useState } from "react";

import { deleteGotchaUser, fetchGotchaUserCards, previewGotchaUser, saveGotchaUser } from "../api";
import type { GotchaUserForm } from "../api";
import { MAX_LINES, addHint, codeLabel, errorText, lineCount } from "../lib/gotchas";
import type { GotchaLang, GotchaSummary, GotchaUserCard, GotchaUserResult } from "../lib/gotchas";

const SLOTS = 4;

/** A tiny example in the box, to show the shape (any other language shows a generic hint). */
const PLACEHOLDER: Record<string, string> = {
  python: "arr = [1, 2, 3]\nfor i in arr:\n    i = i * 2\nprint(arr)",
  javascript: "const a = [1, 2, 3];\na.forEach(n => { n = n * 2; });\nconsole.log(a);",
  typescript: "const a: number[] = [10, 9, 1];\na.sort();\nconsole.log(a.join(','));",
  c: '#include <stdio.h>\n\nint main(void) {\n    int i = 5;\n    printf("%d\\n", i++ * 2);\n}',
  java: 'public class Main {\n    public static void main(String[] args) {\n        System.out.println(1 + 2 + "3");\n    }\n}',
  go: 'package main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println(7 / 2)\n}',
  rust: 'fn main() {\n    println!("{}", 7 / 2);\n}',
  ruby: "puts [1, 2, 3].sum * 2",
  lua: "print(7 // 2)",
  sql: "CREATE TABLE t (v INTEGER);\nINSERT INTO t VALUES (1), (NULL);\nSELECT COUNT(*), COUNT(v) FROM t;",
};

export default function GotchaAdd({
  language,
  name,
  onChanged,
  onTry,
}: {
  language: GotchaLang;
  /** The language's display name ("Rust"). */
  name: string;
  onChanged: (summary: GotchaSummary) => void;
  onTry: () => void;
}) {
  const [open, setOpen] = useState(false);
  const [code, setCode] = useState("");
  const [options, setOptions] = useState<string[]>(() => Array(SLOTS).fill(""));
  const [guess, setGuess] = useState<number | null>(null);
  const [why, setWhy] = useState("");
  const [busy, setBusy] = useState<"" | "preview" | "save">("");
  const [error, setError] = useState("");
  const [shown, setShown] = useState<GotchaUserResult | null>(null);
  const [mine, setMine] = useState<GotchaUserCard[]>([]);
  const [confirming, setConfirming] = useState("");

  const refresh = useCallback(() => {
    fetchGotchaUserCards(language)
      .then((r) => setMine(r.cards))
      .catch(() => setMine([]));
  }, [language]);

  useEffect(() => {
    refresh();
    setShown(null);
    setError("");
    setConfirming("");
  }, [refresh]);

  const lines = lineCount(code);
  const form = (): GotchaUserForm => ({ language, code, options, guess, why });

  const submit = async (save: boolean) => {
    if (busy) return;
    setBusy(save ? "save" : "preview");
    setError("");
    setShown(null);
    try {
      const r = await (save ? saveGotchaUser(form()) : previewGotchaUser(form()));
      setShown(r);
      if (save) {
        if (r.summary) onChanged(r.summary);
        refresh();
      }
    } catch (e) {
      setError(errorText(e));
    } finally {
      setBusy("");
    }
  };

  const reset = () => {
    setCode("");
    setOptions(Array(SLOTS).fill(""));
    setGuess(null);
    setWhy("");
    setShown(null);
    setError("");
  };

  const remove = (id: string) => {
    if (confirming !== id) {
      setConfirming(id);
      return;
    }
    setConfirming("");
    deleteGotchaUser(language, id)
      .then((r) => {
        onChanged(r.summary);
        refresh();
      })
      .catch((e) => setError(errorText(e)));
  };

  return (
    <section className="gq-add" aria-label="Add a quiz I found">
      <button
        type="button"
        className="gq-add-toggle"
        aria-expanded={open}
        aria-controls="gq-add-body"
        onClick={() => setOpen((o) => !o)}
      >
        <span aria-hidden="true">{open ? "▾" : "▸"}</span> Add a quiz I found
        {mine.length > 0 ? <span className="gq-add-count">{mine.length} yours</span> : null}
      </button>

      {open ? (
        <div id="gq-add-body" className="gq-add-body">
          <p className="gq-add-lead">
            Saw a good one online? Paste the {name} program here. It is run for real, and what it
            actually prints becomes the right answer.
            {addHint(language)}
          </p>

          <label className="gq-field" htmlFor="gq-add-code">
            <span>The code</span>
            <span className={`gq-count${lines > MAX_LINES ? " over" : ""}`}>
              {lines}/{MAX_LINES} lines
            </span>
          </label>
          <textarea
            id="gq-add-code"
            className="gq-textarea"
            rows={8}
            spellCheck={false}
            autoCapitalize="off"
            autoCorrect="off"
            value={code}
            placeholder={PLACEHOLDER[language] ?? `Paste a short ${name} program that prints one line.`}
            onChange={(e) => setCode(e.target.value)}
          />

          <fieldset className="gq-opts">
            <legend>
              The options you saw <span className="gq-hint">(optional, any can stay blank)</span>
            </legend>
            {options.map((o, i) => (
              <div className="gq-opt-row" key={i}>
                <input
                  type="radio"
                  name="gq-guess"
                  aria-label={`I think option ${"ABCD"[i]} is right`}
                  checked={guess === i}
                  disabled={!o.trim()}
                  onChange={() => setGuess(i)}
                />
                <span className="gq-key small" aria-hidden="true">
                  {"ABCD"[i]}
                </span>
                <input
                  type="text"
                  className="gq-input"
                  aria-label={`Option ${"ABCD"[i]}`}
                  maxLength={200}
                  value={o}
                  onChange={(e) => {
                    const v = e.target.value;
                    setOptions((cur) => cur.map((x, j) => (j === i ? v : x)));
                    if (!v.trim() && guess === i) setGuess(null);
                  }}
                />
              </div>
            ))}
            <p className="gq-hint">
              The round button marks the one you think is right.
              {guess !== null ? (
                <>
                  {" "}
                  <button type="button" className="gq-link" onClick={() => setGuess(null)}>
                    Clear my pick
                  </button>
                </>
              ) : null}
            </p>
          </fieldset>

          <label className="gq-field" htmlFor="gq-add-why">
            <span>
              A note on why <span className="gq-hint">(optional)</span>
            </span>
          </label>
          <input
            id="gq-add-why"
            type="text"
            className="gq-input wide"
            maxLength={400}
            value={why}
            onChange={(e) => setWhy(e.target.value)}
          />

          <div className="gq-add-actions">
            <button
              type="button"
              className="ws-btn primary"
              disabled={!!busy || !code.trim()}
              onClick={() => void submit(true)}
            >
              {busy === "save" ? "Running..." : "Run it & save"}
            </button>
            <button type="button" className="ws-btn" disabled={!!busy || !code.trim()} onClick={() => void submit(false)}>
              {busy === "preview" ? "Running..." : "Preview"}
            </button>
            <button type="button" className="ws-btn" disabled={!!busy} onClick={reset}>
              Clear
            </button>
          </div>

          {error ? (
            <p className="gq-add-error" role="alert" data-testid="gq-add-error">
              {error}
            </p>
          ) : null}

          {shown ? (
            <div className={`gq-add-result${shown.saved ? " saved" : ""}`} role="status" data-testid="gq-add-result">
              <p className="gq-add-head">{shown.saved ? "Saved as a card of yours." : "Preview - nothing saved yet."}</p>
              <div>
                {shown.raises ? "It stops with" : "It really prints"}
                <pre className="gq-run-text" data-testid="gq-add-output">
                  {shown.output}
                </pre>
              </div>
              {shown.notes.map((n, i) => (
                <p key={i} className="gq-add-note">
                  {n}
                </p>
              ))}
              <ul className="gq-add-options" aria-label="The card's options">
                {shown.options.map((o, i) => (
                  <li key={i} className={o === shown.answer ? "right" : ""}>
                    {o}
                    {o === shown.answer ? <span className="gq-sr"> (the right one)</span> : null}
                  </li>
                ))}
              </ul>
              {shown.saved ? (
                <div className="gq-add-actions">
                  <button type="button" className="ws-btn primary" onClick={onTry}>
                    Try it now
                  </button>
                  <button type="button" className="ws-btn" onClick={reset}>
                    Add another
                  </button>
                </div>
              ) : null}
            </div>
          ) : null}

          {mine.length > 0 ? (
            <div className="gq-mine">
              <h4>Your {name} cards</h4>
              <ul>
                {mine.map((c) => (
                  <li key={c.id}>
                    <code className="gq-mine-code">{codeLabel(c.code)}</code>
                    <span className="gq-mine-meta">
                      {c.options} options, {c.added}
                    </span>
                    <button type="button" className="gq-link danger" onClick={() => remove(c.id)}>
                      {confirming === c.id ? "Really delete?" : "Delete"}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
