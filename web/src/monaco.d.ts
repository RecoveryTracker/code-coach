/**
 * Monaco's package exports don't publish types for its deep ESM paths, but
 * those paths are how you import one language instead of all ninety. Vite
 * resolves them fine; this is purely so `tsc --noEmit` agrees.
 */

declare module "monaco-editor/esm/vs/editor/editor.api" {
  export * from "monaco-editor";
}

// Side-effect imports: each one registers a single language's grammar.
declare module "monaco-editor/esm/vs/basic-languages/*";
