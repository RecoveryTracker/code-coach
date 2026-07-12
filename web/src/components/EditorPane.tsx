import Editor, { type OnMount } from "@monaco-editor/react";
import { useRef } from "react";

type Props = {
  /** Intentional buffer content (day load / reset). Not updated on each keystroke. */
  code: string;
  /** Bump to force-replace editor contents (day change or Reset). */
  revision: number;
  onChange: (value: string) => void;
  /** Run program — wired as ⌘/Ctrl+Enter inside Monaco (it swallows window keys). */
  onRun: () => void;
};

const EDITOR_OPTIONS = {
  fontSize: 14,
  fontFamily: '"SF Mono", Menlo, Monaco, Consolas, ui-monospace, monospace',
  minimap: { enabled: false },
  scrollBeyondLastLine: false,
  wordWrap: "on" as const,
  tabSize: 4,
  automaticLayout: true,
  padding: { top: 12, bottom: 12 },
  renderLineHighlight: "line" as const,
  cursorBlinking: "smooth" as const,
  smoothScrolling: true,
  // This is a typing trainer — the student must type every character.
  // Auto-closing would insert the final ) or " before it is typed, so the
  // coach "completes" a line early (and stray auto-closed chars like `print(i))`
  // break the exact-match check so a finished line never advances).
  autoClosingBrackets: "never" as const,
  autoClosingQuotes: "never" as const,
  autoClosingOvertype: "never" as const,
  autoSurround: "never" as const,
  autoIndent: "none" as const,
  acceptSuggestionOnEnter: "off" as const,
};

/**
 * Uncontrolled while typing: no live `value` prop, so coach re-scores cannot
 * overwrite in-progress keystrokes with a stale buffer.
 * `key={revision}` remounts only when the app intentionally replaces code.
 */
export function EditorPane({ code, revision, onChange, onRun }: Props) {
  const onChangeRef = useRef(onChange);
  const onRunRef = useRef(onRun);
  onChangeRef.current = onChange;
  onRunRef.current = onRun;

  const handleMount: OnMount = (editor, monaco) => {
    // Monaco owns focus while typing — register run here, not only on window.
    editor.addAction({
      id: "code-coach.run",
      label: "Run program",
      keybindings: [
        monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter,
      ],
      run: () => {
        onRunRef.current();
      },
    });
    editor.focus();
  };

  return (
    <section className="iae-pane">
      <div className="iae-pane-header">
        <span>Editor</span>
        <span style={{ textTransform: "none", letterSpacing: 0, fontWeight: 500 }}>
          practice.py
        </span>
      </div>
      <div className="iae-pane-body flush">
        <Editor
          key={revision}
          height="100%"
          defaultLanguage="python"
          theme="vs-dark"
          defaultValue={code}
          onMount={handleMount}
          onChange={(v) => onChangeRef.current(v ?? "")}
          options={EDITOR_OPTIONS}
        />
      </div>
    </section>
  );
}
