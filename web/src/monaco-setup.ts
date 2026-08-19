/**
 * Bundle Monaco locally instead of the loader's default jsdelivr CDN, so the
 * editor works offline and never depends on a third-party host at runtime.
 * Import this ONCE, before anything renders an <Editor>.
 *
 * Importing "monaco-editor" wholesale pulls in a grammar for every language it
 * has ever supported — abap, clojure, solidity, powerquery and eighty more —
 * which made a 4MB bundle, and in dev meant that many separate module
 * requests. We teach eight languages, so we import eight grammars.
 */
import * as monaco from "monaco-editor/esm/vs/editor/editor.api";
import editorWorker from "monaco-editor/esm/vs/editor/editor.worker?worker";
import { loader } from "@monaco-editor/react";

// Syntax highlighting, one import per language we actually offer. `cpp`
// registers both C and C++; `javascript` and `typescript` come together.
import "monaco-editor/esm/vs/basic-languages/python/python.contribution";
import "monaco-editor/esm/vs/basic-languages/dart/dart.contribution";
import "monaco-editor/esm/vs/basic-languages/javascript/javascript.contribution";
import "monaco-editor/esm/vs/basic-languages/typescript/typescript.contribution";
import "monaco-editor/esm/vs/basic-languages/sql/sql.contribution";
import "monaco-editor/esm/vs/basic-languages/cpp/cpp.contribution";
import "monaco-editor/esm/vs/basic-languages/rust/rust.contribution";

self.MonacoEnvironment = {
  // No per-language workers: the drills are typing practice, so tokenisation
  // and diffing from the core worker is all the editor needs.
  getWorker: () => new editorWorker(),
};

loader.config({ monaco });
