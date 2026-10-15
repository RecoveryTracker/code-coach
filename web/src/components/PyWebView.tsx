/**
 * The preview for a Web (Python) step: a "Try it" panel for the learner's app.
 *
 * The app runs on the server in a process of its own (code_coach/canvas/pyweb),
 * serving on 127.0.0.1. This panel is the browser's stand-in: it asks Code
 * Coach to make one request - a method, a path, headers, a body - and shows
 * the app's real answer: the status line, every header, and the body as text
 * (and, for HTML, drawn in a sandboxed frame with no scripts). Redirects are
 * never followed for you; the Follow button takes the hop. Cookies the app
 * sets are kept here, like a browser's, and sent back on the next request.
 *
 * Mount it with a new `key` to Run again: unmounting stops the session, and so
 * does the page going away. A session the server ended (idle for two minutes)
 * is started again by the next Send, which says so - the app's memory is gone.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { requestPyWeb, startPyWeb, stopPyWeb } from "../api";
import type { PyWebResponse, PyWebRoute, PyWebSend } from "../types";

type Props = {
  stepId: string;
  /** The program, as it was when Run was pressed. */
  code: string;
  /** Lines the program printed, and tracebacks of routes that failed. */
  onLog: (lines: string[]) => void;
  /** The program could not start or died: what to tell the learner. */
  onError: (text: string) => void;
};

type Method = PyWebSend["method"];
const METHODS: Method[] = ["GET", "POST", "PUT", "DELETE"];
const REDIRECTS = new Set([301, 302, 303, 307, 308]);
const SENDS_BODY = new Set<string>(["POST", "PUT", "PATCH"]);
const MAX_HISTORY = 6;

type Past = { method: Method; path: string; status: number };

/** The text of a failed request: the server's own reason when it gave one. */
function reason(e: unknown): string {
  const text = e instanceof Error ? e.message : String(e);
  try {
    const detail = (JSON.parse(text) as { detail?: unknown }).detail;
    if (typeof detail === "string") return detail;
  } catch {
    /* not JSON: show it as it is */
  }
  return text;
}

/** A route pattern as something to send: <int:id> -> 1, <name> -> example. */
function example(pattern: string): string {
  return pattern.replace(/<int:[^>]+>/g, "1").replace(/<[^>]+>/g, "example");
}

function statusClass(status: number): string {
  if (status >= 200 && status < 300) return "ok";
  if (status >= 300 && status < 400) return "redirect";
  if (status >= 400 && status < 500) return "client";
  if (status >= 500) return "server";
  return "error";
}

/** Name=value pairs of a Set-Cookie header, and whether it deletes the cookie. */
function parseSetCookie(line: string): { name: string; value: string; gone: boolean } {
  const parts = line.split(";").map((p) => p.trim());
  const eq = parts[0].indexOf("=");
  const name = eq < 0 ? parts[0] : parts[0].slice(0, eq);
  let value = eq < 0 ? "" : parts[0].slice(eq + 1);
  if (value.length >= 2 && value.startsWith('"') && value.endsWith('"')) value = value.slice(1, -1);
  let gone = false;
  for (const attr of parts.slice(1)) {
    const [key, val = ""] = attr.split("=");
    const k = key.trim().toLowerCase();
    if (k === "max-age" && Number(val) <= 0) gone = true;
    if (k === "expires" && Date.parse(val) < Date.now()) gone = true;
  }
  return { name, value, gone };
}

/** The header value, case-insensitively. */
function header(res: PyWebResponse, name: string): string {
  const found = res.headers.find(([k]) => k.toLowerCase() === name.toLowerCase());
  return found ? found[1] : "";
}

export default function PyWebView({ stepId, code, onLog, onError }: Props) {
  const logRef = useRef(onLog);
  const errorRef = useRef(onError);
  logRef.current = onLog;
  errorRef.current = onError;

  const [state, setState] = useState<"starting" | "running" | "failed">("starting");
  const [routes, setRoutes] = useState<PyWebRoute[]>([]);
  const [method, setMethod] = useState<Method>("GET");
  const [path, setPath] = useState("/");
  const [bodyKind, setBodyKind] = useState<"form" | "json">("form");
  const [bodyText, setBodyText] = useState("");
  const [sending, setSending] = useState(false);
  const [result, setResult] = useState<PyWebResponse | null>(null);
  const [asked, setAsked] = useState("");
  const [tab, setTab] = useState<"text" | "rendered">("text");
  const [jar, setJar] = useState<Record<string, string>>({});
  const [history, setHistory] = useState<Past[]>([]);
  const [note, setNote] = useState("");

  const sessionRef = useRef("");
  const jarRef = useRef<Record<string, string>>({});
  const codeRef = useRef(code);
  codeRef.current = code;

  /** Bumped when the panel goes away or starts the app again: an answer for an older one is dropped. */
  const generation = useRef(0);

  /** Start the app (the first time, and again when the server ended the session). */
  const start = useCallback(async (): Promise<boolean> => {
    const mine = ++generation.current;
    setState("starting");
    try {
      const first = await startPyWeb(stepId, codeRef.current);
      if (mine !== generation.current) {
        if (first.session) stopPyWeb(first.session); // unmounted or replaced while it started
        return false;
      }
      sessionRef.current = first.session;
      if (first.logs.length) logRef.current(first.logs);
      if (first.error || !first.session) {
        const where = first.error?.line ? `Line ${first.error.line}: ` : "";
        errorRef.current(where + (first.error?.message ?? "The app could not start."));
        setState("failed");
        return false;
      }
      setRoutes(first.routes);
      setState("running");
      return true;
    } catch (e: unknown) {
      if (mine === generation.current) {
        errorRef.current(reason(e));
        setState("failed");
      }
      return false;
    }
  }, [stepId]);

  useEffect(() => {
    sessionRef.current = "";
    jarRef.current = {};
    void start();
    const leave = () => {
      if (sessionRef.current) stopPyWeb(sessionRef.current);
    };
    window.addEventListener("pagehide", leave);
    window.addEventListener("beforeunload", leave);
    return () => {
      generation.current += 1;
      window.removeEventListener("pagehide", leave);
      window.removeEventListener("beforeunload", leave);
      if (sessionRef.current) stopPyWeb(sessionRef.current);
      sessionRef.current = "";
    };
  }, [start, code]);

  /** Make a request and show what came back. */
  const send = useCallback(
    async (wantMethod: Method, wantPath: string, body = "") => {
      if (!sessionRef.current) return;
      const headers: Record<string, string> = {};
      let payload = "";
      if (SENDS_BODY.has(wantMethod) && body) {
        if (bodyKind === "form") {
          const form = new URLSearchParams();
          for (const line of body.split("\n")) {
            const at = line.indexOf("=");
            if (!line.trim() || at < 0) continue;
            form.append(line.slice(0, at).trim(), line.slice(at + 1));
          }
          payload = form.toString();
          headers["Content-Type"] = "application/x-www-form-urlencoded";
        } else {
          payload = body;
          headers["Content-Type"] = "application/json";
        }
      } else if (SENDS_BODY.has(wantMethod)) {
        headers["Content-Type"] = bodyKind === "form" ? "application/x-www-form-urlencoded" : "application/json";
      }
      const cookies = Object.entries(jarRef.current).map(([k, v]) => `${k}=${v}`);
      if (cookies.length) headers["Cookie"] = cookies.join("; ");
      const sent: PyWebSend = { method: wantMethod, path: wantPath, headers, body: payload };
      setSending(true);
      setNote("");
      try {
        let got: PyWebResponse;
        try {
          got = await requestPyWeb(sessionRef.current, sent);
        } catch (e: unknown) {
          if (!reason(e).includes("No web session")) throw e;
          // The server let the idle session go: start the app again and ask once more.
          sessionRef.current = "";
          jarRef.current = {};
          setJar({});
          setNote("The app had been idle and was stopped, so it was started again - what it remembered is gone.");
          if (!(await start())) return;
          got = await requestPyWeb(sessionRef.current, sent);
        }
        if (got.logs.length) logRef.current(got.logs);
        if (got.error) errorRef.current(got.error);
        for (const [k, v] of got.headers) {
          if (k.toLowerCase() !== "set-cookie") continue;
          const c = parseSetCookie(v);
          if (c.gone) delete jarRef.current[c.name];
          else jarRef.current[c.name] = c.value;
        }
        setJar({ ...jarRef.current });
        setResult(got);
        setAsked(`${wantMethod} ${wantPath}`);
        setTab("text");
        setHistory((was) =>
          [{ method: wantMethod, path: wantPath, status: got.status }, ...was].slice(0, MAX_HISTORY),
        );
      } catch (e: unknown) {
        errorRef.current(reason(e));
      } finally {
        setSending(false);
      }
    },
    [bodyKind, start],
  );

  const follow = useCallback(() => {
    if (!result) return;
    const where = header(result, "Location");
    if (!where) return;
    let next: string;
    try {
      const url = new URL(where, "http://127.0.0.1");
      next = url.pathname + url.search;
    } catch {
      return;
    }
    const [wasMethod] = asked.split(" ");
    const keeps = result.status === 307 || result.status === 308;
    const again: Method = keeps ? (wasMethod as Method) : "GET";
    setMethod(again);
    setPath(next);
    void send(again, next, keeps ? bodyText : "");
  }, [result, asked, bodyText, send]);

  const showBody = SENDS_BODY.has(method);
  const contentType = result ? header(result, "Content-Type").toLowerCase() : "";
  const isHtml = contentType.startsWith("text/html");
  const location = result && REDIRECTS.has(result.status) ? header(result, "Location") : "";
  const text = useMemo(() => {
    if (!result) return "";
    if (result.binary) return `(binary data, ${result.body.length} base64 characters)`;
    return result.body;
  }, [result]);
  const cookieNames = Object.keys(jar);

  return (
    <div className="pyweb">
      <form
        className="pyweb-bar"
        onSubmit={(e) => {
          e.preventDefault();
          void send(method, path.startsWith("/") ? path : `/${path}`, bodyText);
        }}
      >
        <select
          aria-label="Method"
          className="pyweb-method"
          value={method}
          onChange={(e) => setMethod(e.target.value as Method)}
        >
          {METHODS.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
        <input
          aria-label="Path"
          className="pyweb-path"
          value={path}
          spellCheck={false}
          onChange={(e) => setPath(e.target.value)}
          placeholder="/"
        />
        <button type="submit" className="ws-btn primary" disabled={state !== "running" || sending}>
          {sending ? "Sending…" : "Send"}
        </button>
      </form>

      {showBody ? (
        <div className="pyweb-body">
          <div className="pyweb-kinds" role="group" aria-label="Body type">
            {(["form", "json"] as const).map((k) => (
              <button
                key={k}
                type="button"
                className={`canvas-file${bodyKind === k ? " on" : ""}`}
                aria-pressed={bodyKind === k}
                onClick={() => setBodyKind(k)}
              >
                {k === "form" ? "form" : "JSON"}
              </button>
            ))}
            <span className="canvas-file-note">
              {bodyKind === "form" ? "one name=value per line" : "a JSON body, Content-Type application/json"}
            </span>
          </div>
          <textarea
            aria-label="Request body"
            className="pyweb-text"
            rows={4}
            spellCheck={false}
            value={bodyText}
            onChange={(e) => setBodyText(e.target.value)}
            placeholder={bodyKind === "form" ? "title=Flask docs\nurl=https://flask.palletsprojects.com/" : '{"title": "Flask docs", "url": "https://flask.palletsprojects.com/"}'}
          />
        </div>
      ) : null}

      {routes.length > 0 ? (
        <div className="pyweb-chips" aria-label="Your routes">
          {routes.map((r) => (
            <button
              key={`${r.method} ${r.path}`}
              type="button"
              className="pyweb-chip"
              title="Fill in this route"
              onClick={() => {
                if ((METHODS as string[]).includes(r.method)) setMethod(r.method as Method);
                setPath(example(r.path));
              }}
            >
              {r.method} {r.path}
            </button>
          ))}
        </div>
      ) : null}

      {state === "starting" ? <p className="canvas-tip">Starting your app…</p> : null}
      {state === "failed" ? (
        <p className="canvas-tip">Your app is not running - the error is in the console. Fix it and press Run.</p>
      ) : null}
      {note ? <p className="canvas-tip">{note}</p> : null}

      {result ? (
        <div className="pyweb-result" aria-live="polite">
          <div className="pyweb-line">
            <span className={`pyweb-status ${statusClass(result.status)}`}>
              {result.status ? `${result.status} ${result.reason}` : "no answer"}
            </span>
            <span className="pyweb-asked">{asked}</span>
            <span className="pyweb-time">{Math.round(result.seconds * 1000)} ms</span>
            {location ? (
              <button type="button" className="ws-btn" onClick={follow} title="Make the second request, as a browser would">
                Follow → {location}
              </button>
            ) : null}
          </div>
          {result.headers.length > 0 ? (
            <table className="pyweb-headers">
              <tbody>
                {result.headers.map(([k, v], i) => (
                  <tr key={`${k}-${i}`}>
                    <th scope="row">{k}</th>
                    <td>{v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : null}
          <div className="pyweb-kinds" role="tablist" aria-label="Response body">
            <button
              type="button"
              role="tab"
              aria-selected={tab === "text"}
              className={`canvas-file${tab === "text" ? " on" : ""}`}
              onClick={() => setTab("text")}
            >
              Text
            </button>
            {isHtml ? (
              <button
                type="button"
                role="tab"
                aria-selected={tab === "rendered"}
                className={`canvas-file${tab === "rendered" ? " on" : ""}`}
                onClick={() => setTab("rendered")}
              >
                Rendered
              </button>
            ) : null}
            {result.truncated ? <span className="canvas-file-note">cut off at 1 MB</span> : null}
          </div>
          {tab === "rendered" && isHtml ? (
            <iframe className="pyweb-rendered" title="Rendered response" sandbox="" srcDoc={result.body} />
          ) : (
            <pre className="pyweb-text-out">{text === "" ? "(empty body)" : text}</pre>
          )}
        </div>
      ) : state === "running" ? (
        <p className="canvas-tip">Your app is running. Choose a method and a path, then Send.</p>
      ) : null}

      {cookieNames.length > 0 ? (
        <p className="canvas-tip">
          Cookies kept: {cookieNames.map((k) => `${k}=${jar[k]}`).join("; ")}{" "}
          <button
            type="button"
            className="canvas-link"
            onClick={() => {
              jarRef.current = {};
              setJar({});
            }}
          >
            Clear them
          </button>
        </p>
      ) : null}

      {history.length > 0 ? (
        <div className="pyweb-chips" aria-label="Recent requests">
          {history.map((h, i) => (
            <button
              key={`${i}-${h.method}-${h.path}`}
              type="button"
              className="pyweb-chip"
              title="Fill in this request again"
              onClick={() => {
                setMethod(h.method);
                setPath(h.path);
              }}
            >
              {h.method} {h.path} → {h.status || "—"}
            </button>
          ))}
        </div>
      ) : null}
    </div>
  );
}
