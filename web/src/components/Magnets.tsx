/**
 * Code magnets: the lines of a working program, shuffled.
 *
 * The katas ask you to write a function from nothing. The typing drills ask
 * you to copy a shape until your hands know it. This asks the thing in
 * between, which is oddly harder: here are the exact lines of a program that
 * works, in the wrong order — put them back.
 *
 * Placing rather than dragging. Drag and drop is the obvious interface and
 * it is the wrong one here: it needs a mouse, it needs aim, and getting a
 * line into position becomes a test of the pointer rather than of whether
 * you know where the line goes. Clicking a magnet in the tray appends it,
 * clicking one in the program takes it back, and the arrows move it. All of
 * which work from the keyboard, which matters in an app about typing.
 *
 * It is marked by running it, not by comparing your order with the
 * reference. There is always more than one arrangement that works — a
 * function declaration is hoisted, two independent statements can go either
 * way round — and marking those wrong would teach you to guess at the
 * author's preference rather than at what the language does.
 */

import { useCallback, useEffect, useMemo, useState } from "react";

import { checkMagnet, fetchMagnets } from "../api";
import type { MagnetCheck, MagnetList, MagnetPuzzle } from "../types";

/** Which puzzle you were on. */
const LAST_KEY = "code-coach:magnet-last";

/**
 * Which to offer next: fewest goes, and of those the longest ago.
 * Same rule as every other mode here, for the same reason.
 */
function nextUp<T extends { done: number; last: string }>(
  all: T[],
): T | null {
  if (!all.length) return null;
  return all.reduce((best, item) => {
    if (item.done !== best.done) return item.done < best.done ? item : best;
    return item.last < best.last ? item : best;
  }, all[0]);
}

/** A magnet, wherever it currently sits. Index keeps duplicates apart. */
type Piece = { key: number; text: string };

export default function Magnets() {
  const [list, setList] = useState<MagnetList | null>(null);
  const [chosen, setChosen] = useState("");
  const [tray, setTray] = useState<Piece[]>([]);
  const [program, setProgram] = useState<Piece[]>([]);
  const [result, setResult] = useState<MagnetCheck | null>(null);
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState("");

  const load = useCallback((keepOn?: string) => {
    return fetchMagnets().then((data) => {
      setList(data);
      const all = data.families.flatMap((f) => f.magnets);
      let want = keepOn ?? "";
      if (!want) {
        try {
          want = localStorage.getItem(LAST_KEY) ?? "";
        } catch {
          /* a blocked store is not worth interrupting practice for */
        }
      }
      const start = all.find((m) => m.id === want) ?? nextUp(all);
      if (start) setChosen(start.id);
      return data;
    });
  }, []);

  useEffect(() => {
    load().catch((e: unknown) =>
      setError(e instanceof Error ? e.message : String(e)),
    );
  }, [load]);

  const puzzle = useMemo(
    () =>
      list?.families.flatMap((f) => f.magnets).find((m) => m.id === chosen) ??
      null,
    [list, chosen],
  );

  /* Keyed on the id rather than the object: the list is rebuilt after a
     pass, which changes the object's identity, and an effect watching the
     object would fire and clear the board it just set. */
  useEffect(() => {
    if (!puzzle) return;
    setTray(puzzle.pieces.map((text, i) => ({ key: i, text })));
    setProgram([]);
    setResult(null);
    try {
      localStorage.setItem(LAST_KEY, puzzle.id);
    } catch {
      /* same */
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chosen]);

  const place = (piece: Piece) => {
    setTray((was) => was.filter((p) => p.key !== piece.key));
    setProgram((was) => [...was, piece]);
    setResult(null);
  };

  const takeBack = (piece: Piece) => {
    setProgram((was) => was.filter((p) => p.key !== piece.key));
    setTray((was) => [...was, piece]);
    setResult(null);
  };

  const move = (index: number, by: number) => {
    setProgram((was) => {
      const to = index + by;
      if (to < 0 || to >= was.length) return was;
      const next = [...was];
      [next[index], next[to]] = [next[to], next[index]];
      return next;
    });
    setResult(null);
  };

  const check = useCallback(async () => {
    if (!puzzle || checking) return;
    setChecking(true);
    setError("");
    try {
      const got = await checkMagnet({
        magnet_id: puzzle.id,
        lines: program.map((p) => p.text),
      });
      setResult(got);
      if (got.passed) {
        setList((was) =>
          was
            ? {
                ...was,
                families: was.families.map((f) => ({
                  ...f,
                  magnets: f.magnets.map((m) =>
                    m.id === puzzle.id
                      ? { ...m, done: got.done, last: new Date().toISOString() }
                      : m,
                  ),
                })),
              }
            : was,
        );
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setChecking(false);
    }
  }, [puzzle, program, checking]);

  /* Another go means another jumble, which has to come from the server —
     the finished order is not in the payload, and a reshuffle on this side
     could only reorder what it already has. */
  const again = useCallback(() => {
    if (!puzzle) return;
    setResult(null);
    load(puzzle.id).catch((e: unknown) =>
      setError(e instanceof Error ? e.message : String(e)),
    );
  }, [puzzle, load]);

  const leastDone = useMemo(
    () => nextUp(list?.families.flatMap((f) => f.magnets) ?? []),
    [list],
  );

  if (error && !list) {
    return <div className="lessons-empty">Could not load these: {error}</div>;
  }
  if (!list || !puzzle) return <div className="lessons-empty">Loading…</div>;

  return (
    <div className="lessons-wrap">
      <nav className="lessons-list">
        <h2>Magnets</h2>
        <p className="lessons-intro">
          The lines of a program that works, in the wrong order. Put them
          back. It is marked by running what you built, so any arrangement
          that prints the right thing is right.
        </p>
        {leastDone && leastDone.id !== chosen ? (
          <button
            type="button"
            className="ws-btn kata-next"
            onClick={() => setChosen(leastDone.id)}
            title={
              leastDone.done
                ? `${leastDone.name} — done ${leastDone.done} so far, and `
                  + `the longest ago of those`
                : `${leastDone.name} — not tried yet`
            }
          >
            Next up: {leastDone.name}
          </button>
        ) : null}
        {list.families.map((family) => (
          <div key={family.name} className="wb-section">
            <h4 className="wb-section-head">
              {family.name}
              <span className="wb-section-count">{family.magnets.length}</span>
            </h4>
            {family.magnets.map((m: MagnetPuzzle) => (
              <button
                key={m.id}
                type="button"
                className={`lessons-pick${m.id === chosen ? " on" : ""}`}
                onClick={() => setChosen(m.id)}
              >
                <span className="lessons-pick-name">{m.name}</span>
                {m.done ? (
                  <span className="lessons-pick-blurb">done {m.done}&#215;</span>
                ) : null}
              </button>
            ))}
          </div>
        ))}
      </nav>

      <article className="lessons-open wb">
        <header>
          <h3>
            {puzzle.name}
            <span className="predict-lang">
              {puzzle.language === "javascript" ? "JavaScript" : "Python"}
            </span>
          </h3>
        </header>

        <p className="lessons-blurb">{puzzle.note}</p>

        <div className="magnet-board">
          <div className="magnet-side">
            <p className="wb-prompt">
              Loose magnets
              {tray.length ? ` (${tray.length})` : " — all placed"}
            </p>
            <div className="magnet-tray">
              {tray.map((piece) => (
                <button
                  key={piece.key}
                  type="button"
                  className="magnet"
                  onClick={() => place(piece)}
                  title="Put this at the bottom of the program"
                >
                  <code>{piece.text}</code>
                </button>
              ))}
              {!tray.length ? (
                <p className="magnet-empty">
                  Every piece is placed. Check it, or move lines around.
                </p>
              ) : null}
            </div>
          </div>

          <div className="magnet-side">
            <p className="wb-prompt">Your program</p>
            <ol className="magnet-program">
              {program.map((piece, i) => (
                <li key={piece.key}>
                  <span className="magnet-num">{i + 1}</span>
                  <code className="magnet-line">{piece.text}</code>
                  <span className="magnet-controls">
                    <button
                      type="button"
                      className="ws-btn magnet-move"
                      onClick={() => move(i, -1)}
                      disabled={i === 0}
                      title="Move up"
                      aria-label={`Move line ${i + 1} up`}
                    >
                      ↑
                    </button>
                    <button
                      type="button"
                      className="ws-btn magnet-move"
                      onClick={() => move(i, 1)}
                      disabled={i === program.length - 1}
                      title="Move down"
                      aria-label={`Move line ${i + 1} down`}
                    >
                      ↓
                    </button>
                    <button
                      type="button"
                      className="ws-btn magnet-move"
                      onClick={() => takeBack(piece)}
                      title="Take it back"
                      aria-label={`Remove line ${i + 1}`}
                    >
                      ×
                    </button>
                  </span>
                </li>
              ))}
              {!program.length ? (
                <li className="magnet-empty">
                  Click a magnet to start the program.
                </li>
              ) : null}
            </ol>
          </div>
        </div>

        <div className="wb-actions">
          <button
            type="button"
            className="ws-btn primary"
            onClick={() => void check()}
            disabled={checking || tray.length > 0 || !program.length}
            title={
              tray.length
                ? "Every magnet has to be placed first"
                : "Run it and see what it prints"
            }
          >
            {checking ? "Running…" : "Check"}
          </button>
          <button
            type="button"
            className="ws-btn"
            onClick={again}
            title="Jumble them again and go once more — the next go is the point"
          >
            Again
          </button>
        </div>

        {error ? <p className="wb-verdict bad">{error}</p> : null}

        {result ? (
          <div className="kata-result">
            <p
              className={
                result.passed
                  ? "wb-verdict ok"
                  : result.broke
                    ? "wb-verdict bad"
                    : "wb-verdict bad"
              }
            >
              {result.passed
                ? `That runs and prints exactly that. Done ${result.done}×.`
                : result.broke
                  ? result.broke
                  : "It ran, and printed something else."}
            </p>
            {!result.passed && !result.broke ? (
              <div className="predict-compare">
                <div>
                  <p className="wb-walkthrough-note">Yours printed</p>
                  <pre className="wb-stderr">
                    {result.printed || "(nothing)"}
                  </pre>
                </div>
                <div>
                  <p className="wb-walkthrough-note">It should print</p>
                  <pre className="wb-stderr">{result.expect}</pre>
                </div>
              </div>
            ) : null}
            {result.passed && result.why ? (
              <p className="kata-bug">
                <strong>Why that order:</strong> {result.why}
              </p>
            ) : null}
          </div>
        ) : null}
      </article>
    </div>
  );
}
