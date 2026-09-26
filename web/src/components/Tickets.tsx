/**
 * Tickets: one small team codebase and the queue of work against it.
 *
 * Each ticket - a bug report, a feature request, a refactor, a change of
 * rules - starts from the project as it stands after every earlier one.
 * Running the checks runs the whole file against two lists: what the
 * ticket asks for, and everything that already worked. A fix that breaks
 * something old fails the ticket, which is the lesson this screen exists
 * to teach.
 *
 * Drafts are kept per ticket in this browser, so leaving mid-ticket and
 * coming back finds your edits. "Reset to start" puts the ticket's own
 * starting file back.
 */

import { useCallback, useEffect, useMemo, useState } from "react";

import "../styles/tickets.css";

// ── Types and requests ───────────────────────────────────────
//
// Kept here so this screen stands on its own; they mirror the
// /api/tickets routes and can move to types.ts / api.ts unchanged.

export type TicketKind = "bug" | "feature" | "refactor" | "change";

export type TicketInfo = {
  id: string;
  title: string;
  kind: TicketKind;
  report: string;
  start: string;
  hint: string;
  /** The functions this ticket adds or changes. */
  new: string[];
  /** Every function checked once this ticket is done. */
  checks: string[];
  done: number;
  last: string;
};

export type TicketProject = {
  id: string;
  title: string;
  language: string;
  story: string;
  tickets: TicketInfo[];
};

export type TicketList = { projects: TicketProject[] };

export type TicketCaseResult = {
  args: unknown[];
  want: unknown;
  got: unknown;
  error: string;
  passed: boolean;
  changed: boolean;
};

export type TicketFunctionResult = {
  name: string;
  params: string[];
  new: boolean;
  passed: boolean;
  broke: string;
  count: number;
  total: number;
  results: TicketCaseResult[];
};

export type TicketCheck = {
  passed: boolean;
  broke: string;
  stdout: string;
  functions: TicketFunctionResult[];
  new_passed: boolean;
  kept_passed: boolean;
  lesson: string;
  done: number;
};

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export function fetchTickets(): Promise<TicketList> {
  return request("/api/tickets");
}

export function checkTicket(
  projectId: string,
  ticketId: string,
  code: string,
): Promise<TicketCheck> {
  return request("/api/tickets/check", {
    method: "POST",
    body: JSON.stringify({ project_id: projectId, ticket_id: ticketId, code }),
  });
}

export function fetchTicketAnswer(
  projectId: string,
  ticketId: string,
): Promise<{ after: string }> {
  const q = new URLSearchParams({ project_id: projectId, ticket_id: ticketId });
  return request(`/api/tickets/answer?${q}`);
}

// ── Local memory ─────────────────────────────────────────────

/** Same spelling as LAST_KEYS.tickets, for the session queue. */
const LAST_KEY = "code-coach:tickets-last";
const DRAFT_KEY = "code-coach:ticket-drafts";

function readDrafts(): Record<string, string> {
  try {
    const raw = JSON.parse(localStorage.getItem(DRAFT_KEY) ?? "{}");
    return raw && typeof raw === "object" ? raw : {};
  } catch {
    return {};
  }
}

function writeDrafts(all: Record<string, string>): void {
  try {
    localStorage.setItem(DRAFT_KEY, JSON.stringify(all));
  } catch {
    /* a blocked store only costs the draft */
  }
}

function readLast(): string {
  try {
    return localStorage.getItem(LAST_KEY) ?? "";
  } catch {
    return "";
  }
}

// ── Showing values ───────────────────────────────────────────

function asValue(value: unknown, language: string): string {
  const py = language === "python";
  if (value === null || value === undefined) return py ? "None" : "null";
  if (typeof value === "boolean") return py ? (value ? "True" : "False") : String(value);
  if (typeof value === "string") {
    if (py && !value.includes("'")) return `'${value}'`;
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return `[${value.map((v) => asValue(v, language)).join(", ")}]`;
  if (typeof value === "object") {
    const pairs = Object.entries(value as Record<string, unknown>).map(([k, v]) =>
      py ? `'${k}': ${asValue(v, language)}` : `${/^[A-Za-z_$][\w$]*$/.test(k) ? k : JSON.stringify(k)}: ${asValue(v, language)}`,
    );
    return `{${pairs.join(", ")}}`;
  }
  return String(value);
}

function asCall(name: string, args: unknown[], language: string): string {
  return `${name}(${args.map((a) => asValue(a, language)).join(", ")})`;
}

const KIND_LABEL: Record<TicketKind, string> = {
  bug: "Bug",
  feature: "Feature",
  refactor: "Refactor",
  change: "Change of rules",
};

const LANGUAGE_LABEL: Record<string, string> = {
  python: "Python",
  javascript: "JavaScript",
};

// ── One function's result ────────────────────────────────────

function FunctionResult({ fn, language }: { fn: TicketFunctionResult; language: string }) {
  const [open, setOpen] = useState(!fn.passed);
  const failing = fn.results.filter((r) => !r.passed);
  return (
    <li className={`ticket-fn${fn.passed ? " ok" : " bad"}`}>
      <button type="button" className="ticket-fn-head" onClick={() => setOpen(!open)}>
        <span className="ticket-fn-mark" aria-hidden="true">
          {fn.passed ? "✓" : "✗"}
        </span>
        <code>{fn.name}</code>
        <span className="ticket-fn-count">
          {fn.broke ? "did not run" : `${fn.count} of ${fn.total}`}
        </span>
      </button>
      {open && fn.broke ? <pre className="wb-stderr">{fn.broke}</pre> : null}
      {open && !fn.broke && failing.length ? (
        <ul className="kata-cases">
          {failing.map((c, i) => (
            <li key={i} className="kata-case bad">
              <code className="mono">{asCall(fn.name, c.args, language)}</code>
              <span className="kata-case-got">
                {c.error
                  ? `raised ${c.error}`
                  : c.changed
                    ? asValue(c.got, language) === asValue(c.want, language)
                      ? "changed what it was given - the answer is right, the damage is not"
                      : `changed what it was given, and gave ${asValue(c.got, language)}`
                    : `gave ${asValue(c.got, language)}, wanted ${asValue(c.want, language)}`}
              </span>
            </li>
          ))}
        </ul>
      ) : null}
    </li>
  );
}

// ── The screen ───────────────────────────────────────────────

export default function Tickets() {
  const [list, setList] = useState<TicketList | null>(null);
  const [projectId, setProjectId] = useState("");
  const [ticketId, setTicketId] = useState("");
  const [drafts, setDrafts] = useState<Record<string, string>>(readDrafts);
  const [result, setResult] = useState<TicketCheck | null>(null);
  const [running, setRunning] = useState(false);
  const [hint, setHint] = useState(false);
  const [answer, setAnswer] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    let alive = true;
    fetchTickets()
      .then((data) => {
        if (!alive) return;
        setList(data);
        const last = readLast();
        const home =
          data.projects.find((p) => p.tickets.some((t) => t.id === last)) ?? data.projects[0];
        if (!home) return;
        setProjectId(home.id);
        const first =
          home.tickets.find((t) => t.id === last) ??
          home.tickets.find((t) => !t.done) ??
          home.tickets[0];
        if (first) setTicketId(first.id);
      })
      .catch((e: unknown) => setError(e instanceof Error ? e.message : String(e)));
    return () => {
      alive = false;
    };
  }, []);

  const proj = useMemo(
    () => list?.projects.find((p) => p.id === projectId) ?? null,
    [list, projectId],
  );
  const tick = useMemo(
    () => proj?.tickets.find((t) => t.id === ticketId) ?? null,
    [proj, ticketId],
  );
  const index = proj && tick ? proj.tickets.indexOf(tick) : -1;
  const code = tick ? (drafts[tick.id] ?? tick.start) : "";

  useEffect(() => {
    if (!tick) return;
    setResult(null);
    setHint(false);
    setAnswer("");
    setError("");
    try {
      localStorage.setItem(LAST_KEY, tick.id);
    } catch {
      /* same */
    }
  }, [tick]);

  const setCode = (next: string) => {
    if (!tick) return;
    const all = { ...drafts, [tick.id]: next };
    setDrafts(all);
    writeDrafts(all);
  };

  const reset = () => {
    if (!tick) return;
    const all = { ...drafts };
    delete all[tick.id];
    setDrafts(all);
    writeDrafts(all);
    setResult(null);
  };

  const pickProject = (id: string) => {
    const p = list?.projects.find((x) => x.id === id);
    if (!p) return;
    setProjectId(p.id);
    const first = p.tickets.find((t) => !t.done) ?? p.tickets[0];
    if (first) setTicketId(first.id);
  };

  const run = useCallback(async () => {
    if (!proj || !tick || running) return;
    setRunning(true);
    setError("");
    try {
      const got = await checkTicket(proj.id, tick.id, code);
      setResult(got);
      if (got.passed) {
        setList((was) =>
          was
            ? {
                projects: was.projects.map((p) =>
                  p.id !== proj.id
                    ? p
                    : {
                        ...p,
                        tickets: p.tickets.map((t) =>
                          t.id === tick.id
                            ? { ...t, done: got.done, last: new Date().toISOString() }
                            : t,
                        ),
                      },
                ),
              }
            : was,
        );
      }
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setRunning(false);
    }
  }, [proj, tick, code, running]);

  const showAnswer = async () => {
    if (!proj || !tick) return;
    if (answer) {
      setAnswer("");
      return;
    }
    try {
      setAnswer((await fetchTicketAnswer(proj.id, tick.id)).after);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  if (error && !list) return <div className="lessons-empty">Could not load these: {error}</div>;
  if (!list || !proj || !tick) return <div className="lessons-empty">Loading…</div>;

  const next = proj.tickets[index + 1] ?? null;
  const indent = proj.language === "python" ? "    " : "  ";
  const asked = result?.functions.filter((f) => f.new) ?? [];
  const kept = result?.functions.filter((f) => !f.new) ?? [];

  return (
    <div className="lessons-wrap">
      <nav className="lessons-list">
        <h2>Tickets</h2>
        <p className="lessons-intro">
          One small codebase and the team&apos;s queue of work. Each ticket starts where the
          last one finished, and is checked on what it asks for and on everything that
          already worked.
        </p>
        <div className="ticket-projects" role="tablist" aria-label="Project">
          {list.projects.map((p) => (
            <button
              key={p.id}
              type="button"
              role="tab"
              aria-selected={p.id === proj.id}
              className={`ticket-project${p.id === proj.id ? " on" : ""}`}
              onClick={() => pickProject(p.id)}
            >
              {p.title}
              <span className="ticket-project-lang">
                {LANGUAGE_LABEL[p.language] ?? p.language}
              </span>
            </button>
          ))}
        </div>
        {proj.tickets.map((t, i) => (
          <button
            key={t.id}
            type="button"
            className={`lessons-pick${t.id === tick.id ? " on" : ""}`}
            onClick={() => setTicketId(t.id)}
          >
            <span className="lessons-pick-name">
              <span className={`ticket-done${t.done ? " yes" : ""}`} aria-hidden="true">
                {t.done ? "✓" : `${i + 1}`}
              </span>
              {t.title}
            </span>
            <span className="lessons-pick-blurb">
              {KIND_LABEL[t.kind]}
              {t.done ? ` · done ${t.done}×` : ""}
              {drafts[t.id] !== undefined && drafts[t.id] !== t.start ? " · draft" : ""}
            </span>
          </button>
        ))}
      </nav>

      <article className="lessons-open wb">
        <header>
          <h3>
            <span className={`ticket-kind ticket-kind-${tick.kind}`}>{KIND_LABEL[tick.kind]}</span>
            {tick.title}
            <span className="predict-lang">{LANGUAGE_LABEL[proj.language] ?? proj.language}</span>
          </h3>
        </header>
        {index === 0 ? <p className="lessons-blurb">{proj.story}</p> : null}
        <blockquote className="ticket-report">{tick.report}</blockquote>
        <p className="ticket-scope">
          Asks for:{" "}
          {tick.new.map((n, i) => (
            <span key={n}>
              {i ? ", " : ""}
              <code>{n}</code>
            </span>
          ))}
          <span className="ticket-scope-rest">
            {" "}· must keep working: {tick.checks.filter((c) => !tick.new.includes(c)).join(", ")}
          </span>
        </p>

        <section className="hunt-panel">
          <h4 className="hunt-panel-head">The project</h4>
          <textarea
            className={`wb-code ticket-code${result ? (result.passed ? " ok" : " bad") : ""}`}
            value={code}
            onChange={(e) => setCode(e.target.value)}
            spellCheck={false}
            rows={Math.min(40, Math.max(18, code.split("\n").length + 2))}
            aria-label="The project file"
            onKeyDown={(e) => {
              if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
                e.preventDefault();
                void run();
                return;
              }
              if (e.key === "Tab" && !e.shiftKey && !e.ctrlKey && !e.altKey) {
                e.preventDefault();
                const box = e.currentTarget;
                const { selectionStart: s, selectionEnd: end } = box;
                setCode(code.slice(0, s) + indent + code.slice(end));
                requestAnimationFrame(() => {
                  box.selectionStart = box.selectionEnd = s + indent.length;
                });
              }
            }}
          />
          <div className="wb-actions">
            <button
              type="button"
              className="ws-btn primary"
              disabled={running}
              onClick={() => void run()}
            >
              {running ? "Running…" : "Run checks (Ctrl+Enter)"}
            </button>
            <button type="button" className="ws-btn" onClick={() => setHint(!hint)}>
              Hint
            </button>
            <button
              type="button"
              className="ws-btn"
              onClick={reset}
              disabled={code === tick.start}
            >
              Reset to start
            </button>
            <button type="button" className="ws-btn" onClick={() => void showAnswer()}>
              {answer ? "Hide the solution" : "Show a solution"}
            </button>
          </div>
          {hint ? <p className="wb-answer">{tick.hint}</p> : null}
          {answer ? (
            <div className="kata-answer">
              <p className="wb-walkthrough-note">One way to do it - the whole file:</p>
              <pre className="wb-stderr">{answer}</pre>
              <button type="button" className="ws-btn" onClick={() => setCode(answer)}>
                Put it in the box
              </button>
            </div>
          ) : null}
        </section>

        {error ? <p className="wb-verdict bad">{error}</p> : null}

        {result ? (
          result.broke ? (
            <section className="hunt-panel">
              <p className="wb-verdict bad">The file did not run:</p>
              <pre className="wb-stderr">{result.broke}</pre>
            </section>
          ) : (
            <>
              <section className="hunt-panel">
                <p className={result.passed ? "wb-verdict ok" : "wb-verdict bad"}>
                  {result.passed
                    ? "Ticket done - everything it asks, and nothing broken."
                    : !result.new_passed && !result.kept_passed
                      ? "Not yet - and something that used to work is broken."
                      : !result.kept_passed
                        ? "The ticket works, but something that used to work is broken."
                        : "Not yet - the ticket's own checks are failing."}
                </p>
                <h4 className="hunt-panel-head">What the ticket asks</h4>
                <ul className="ticket-fns">
                  {asked.map((f) => (
                    <FunctionResult key={`${f.name}:${f.passed}`} fn={f} language={proj.language} />
                  ))}
                </ul>
                <h4 className="hunt-panel-head">What must keep working</h4>
                <ul className="ticket-fns">
                  {kept.map((f) => (
                    <FunctionResult key={`${f.name}:${f.passed}`} fn={f} language={proj.language} />
                  ))}
                </ul>
              </section>
              {result.passed ? (
                <section className="hunt-panel case-step-done">
                  <p className="kata-bug">
                    <strong>The lesson:</strong> {result.lesson}
                  </p>
                  {next ? (
                    <button
                      type="button"
                      className="ws-btn primary"
                      onClick={() => setTicketId(next.id)}
                    >
                      Next ticket: {next.title}
                    </button>
                  ) : (
                    <p className="wb-prompt">That was the last ticket on this project.</p>
                  )}
                </section>
              ) : null}
              {result.stdout.trim() ? (
                <>
                  <p className="wb-walkthrough-note">What your code printed:</p>
                  <pre className="wb-stderr">{result.stdout}</pre>
                </>
              ) : null}
            </>
          )
        ) : null}
      </article>
    </div>
  );
}
