/**
 * Bundle Monaco locally instead of the loader's default jsdelivr CDN, so the
 * editor works offline and never depends on a third-party host at runtime.
 * Import this ONCE, before anything renders an <Editor>.
 */
import * as monaco from "monaco-editor";
import editorWorker from "monaco-editor/esm/vs/editor/editor.worker?worker";
import { loader } from "@monaco-editor/react";

self.MonacoEnvironment = {
  // Python has no dedicated language worker; the core editor worker covers
  // tokenization/diff. Everything else falls back to it too.
  getWorker: () => new editorWorker(),
};

loader.config({ monaco });
