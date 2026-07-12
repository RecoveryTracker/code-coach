type Props = {
  stdout: string;
  stderr: string;
  exitCode: number | null;
  ran: boolean;
  running: boolean;
  onRun: () => void;
};

/**
 * Terminal-style run panel — this is where the program speaks back.
 */
export function Terminal({
  stdout,
  stderr,
  exitCode,
  ran,
  running,
  onRun,
}: Props) {
  let body: string;
  let kind: "idle" | "out" | "err" = "idle";

  if (running) {
    body = "Running python practice.py …";
    kind = "out";
  } else if (!ran || exitCode === null) {
    body =
      "Terminal ready.\nPress Run (⌘⏎) to execute practice.py and see output here.";
    kind = "idle";
  } else if (exitCode !== 0) {
    body = stderr.trim() || `(exit ${exitCode}, no stderr)`;
    kind = "err";
  } else if (stdout.trim()) {
    body = stdout.replace(/\n$/, "");
    kind = "out";
  } else {
    body = `(exit 0 — no output)`;
    kind = "out";
  }

  return (
    <section className="term">
      <header className="term-bar">
        <div className="term-dots" aria-hidden>
          <span />
          <span />
          <span />
        </div>
        <span className="term-title">Terminal</span>
        <button
          type="button"
          className="term-run"
          onClick={onRun}
          disabled={running}
        >
          {running ? "Running…" : "Run ⌘⏎"}
        </button>
      </header>
      <div className="term-body">
        <div className="term-line muted">$ python practice.py</div>
        <pre className={`term-out ${kind}`}>{body}</pre>
        {ran && exitCode !== null && !running ? (
          <div className={`term-exit ${exitCode === 0 ? "ok" : "bad"}`}>
            process exited {exitCode}
          </div>
        ) : null}
      </div>
    </section>
  );
}
