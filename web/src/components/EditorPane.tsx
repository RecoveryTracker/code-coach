import Editor, { type OnMount } from "@monaco-editor/react";
import { useEffect, useRef } from "react";

type Props = {
  /** Intentional buffer content (day load / reset). Not updated on each keystroke. */
  code: string;
  /** Bump to force-replace editor contents (day change or Reset). */
  revision: number;
  onChange: (value: string) => void;
  /** Run program — wired as ⌘/Ctrl+Enter inside Monaco (it swallows window keys). */
  onRun: () => void;
  /** Monaco language id — follows the language setting. */
  language?: string;
  /** Shown in the pane header. */
  fileName?: string;
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
  // Input goes through the classic hidden textarea rather than the browser's
  // EditContext API. Monaco 0.55 turns EditContext on by default, which marks
  // that textarea readonly and leaves it there purely for IME — typing keeps
  // working because Monaco writes to its own model, and paste stops, because
  // that path needs the clipboard event to land in a writable field. Nothing
  // here needs EditContext, and Ctrl+V is not optional.
  editContext: false,
};

/**
 * Where the cursor was when the editor was last torn down, and the text it
 * was in. Module level because a takeover screen unmounts this component, so
 * a ref would not outlive it — and coming back to the top of the file every
 * time is exactly the thing being fixed.
 */
let lastPlace: { value: string; line: number; column: number } | null = null;

/**
 * Uncontrolled while typing: no live `value` prop, so coach re-scores cannot
 * overwrite in-progress keystrokes with a stale buffer.
 *
 * `revision` is what pushes new content in. It used to be a React `key`, which
 * tore down and rebuilt the whole editor on every lesson change — that's what
 * made switching classes feel sluggish, since the API round trip is ~20ms and
 * the remount was the rest. Setting the model value keeps the same instance.
 */
export function EditorPane({
  code,
  revision,
  onChange,
  onRun,
  language = "python",
  fileName = "practice.py",
}: Props) {
  const onChangeRef = useRef(onChange);
  const onRunRef = useRef(onRun);
  const editorRef = useRef<Parameters<OnMount>[0] | null>(null);
  const codeRef = useRef(code);
  onChangeRef.current = onChange;
  onRunRef.current = onRun;
  codeRef.current = code;

  // Deliberately keyed on `revision` alone: `code` changes on every keystroke
  // and re-applying it here would fight the person typing.
  useEffect(() => {
    const editor = editorRef.current;
    if (!editor) return;
    if (editor.getValue() === codeRef.current) return;
    editor.setValue(codeRef.current);
    editor.setPosition({ lineNumber: 1, column: 1 });
    editor.focus();
  }, [revision]);

  const handleMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;

    // Paste, done by hand. See the note at the top of this file: Monaco's own
    // handling was not applying it, and the event carries everything needed.
    const container = editor.getContainerDomNode();
    const onPaste = (event: ClipboardEvent) => {
      const text = event.clipboardData?.getData("text/plain");
      // Nothing usable — an image, say. Leave it to Monaco rather than
      // swallowing the event and making it worse.
      if (!text) return;
      // One cursor only. With several, Monaco splits the pasted lines
      // between them, and that is worth more than anything we do here.
      const selections = editor.getSelections();
      if (!selections || selections.length !== 1) return;
      const selection = selections[0];
      event.preventDefault();
      event.stopPropagation();

      // Where the caret belongs afterwards: the end of what was inserted.
      // executeEdits moves markers but not the caret, so without passing this
      // the cursor stayed at the start of the paste and the next thing typed
      // went in front of it.
      const pasted = text.split(/\r\n|\r|\n/);
      const endLine = selection.startLineNumber + pasted.length - 1;
      const endColumn =
        pasted.length === 1
          ? selection.startColumn + text.length
          : pasted[pasted.length - 1].length + 1;

      editor.executeEdits(
        "clipboard-paste",
        [{ range: selection, text, forceMoveMarkers: true }],
        [new monaco.Selection(endLine, endColumn, endLine, endColumn)],
      );
      editor.pushUndoStop();
      // executeEdits does not scroll, so a long paste can land out of sight.
      editor.revealPositionInCenterIfOutsideViewport({
        lineNumber: endLine,
        column: endColumn,
      });
    };
    container.addEventListener("paste", onPaste, true);

    // Put the cursor back where it was, but only if this is the same text it
    // was left in — a different lesson should start at the top.
    if (lastPlace && editor.getValue() === lastPlace.value) {
      editor.setPosition({
        lineNumber: lastPlace.line,
        column: lastPlace.column,
      });
      editor.revealPositionInCenterIfOutsideViewport({
        lineNumber: lastPlace.line,
        column: lastPlace.column,
      });
    }

    // Kept up to date as it moves. Reading it on dispose was too late — the
    // editor is already going and the position reads back empty.
    editor.onDidChangeCursorPosition((e) => {
      lastPlace = {
        value: editor.getValue(),
        line: e.position.lineNumber,
        column: e.position.column,
      };
    });

    editor.onDidDispose(() =>
      container.removeEventListener("paste", onPaste, true),
    );

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
          {fileName}
        </span>
      </div>
      <div className="iae-pane-body flush">
        <Editor
          height="100%"
          language={language}
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
