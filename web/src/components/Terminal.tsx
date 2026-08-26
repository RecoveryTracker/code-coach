type Props = {
  stdout: string;
  stderr: string;
  exitCode: number | null;
  ran: boolean;
  running: boolean;
  onRun: () => void;
  /** Which language Run will actually execute. */
  language: string;
};

/**
 * The command the server really runs, per language.
 *
 * Not decoration. This panel used to print `$ python practice.py` whatever you
 * were writing, so a Dart type error arrived underneath a line claiming Python
 * had run it. Naming the real command also explains itself: the compiled
 * languages visibly compile first, and TypeScript type-checks before Node ever
 * sees the file, which is most of the reason those take longer and why the
 * error you get back is a compiler's rather than a runtime's.
 */
const RUN_COMMANDS: Record<string, { file: string; command: string }> = {
  python: { file: "practice.py", command: "python practice.py" },
  javascript: { file: "practice.js", command: "node practice.js" },
  typescript: {
    file: "practice.ts",
    command: "tsc practice.ts && node practice.js",
  },
  dart: { file: "practice.dart", command: "dart run practice.dart" },
  c: {
    file: "practice.c",
    command: "gcc -std=c17 practice.c -lm && ./practice",
  },
  cpp: {
    file: "practice.cpp",
    command: "g++ -std=c++17 practice.cpp && ./practice",
  },
  rust: { file: "practice.rs", command: "rustc -O practice.rs && ./practice" },
  sql: { file: "practice.sql", command: "sqlite3 practice.db < practice.sql" },
};

/** Shared with the editor's filename tab, so the two always agree. */
export function runCommandFor(language: string) {
  return RUN_COMMANDS[language] ?? RUN_COMMANDS.python;
}

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
  language,
}: Props) {
  const { file, command } = runCommandFor(language);
  let body: string;
  let kind: "idle" | "out" | "err" = "idle";

  if (running) {
    body = `Running ${command} …`;
    kind = "out";
  } else if (!ran || exitCode === null) {
    body =
      `Terminal ready.\nPress Run (⌘⏎) to execute ${file} and see output here.`;
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
        <div className="term-line muted">$ {command}</div>
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
