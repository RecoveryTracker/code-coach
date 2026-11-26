/**
 * How each language's name is written on screen, in one place.
 *
 * Every mode used to carry its own little map, and each one was missing
 * whichever language arrived after it was written - so a TypeScript puzzle
 * was labelled "typescript" on one screen and "TypeScript" on the next.
 */

export const LANGUAGE_NAMES: Record<string, string> = {
  python: "Python",
  javascript: "JavaScript",
  typescript: "TypeScript",
  dart: "Dart",
  c: "C",
  cpp: "C++",
  rust: "Rust",
  ruby: "Ruby",
  sql: "SQL",
  postgresql: "PostgreSQL",
  go: "Go",
};

/** Short tags for tight spaces such as a list heading: "Py", "TS". */
export const LANGUAGE_TAGS: Record<string, string> = {
  python: "Py",
  javascript: "JS",
  typescript: "TS",
  dart: "Dart",
  c: "C",
  cpp: "C++",
  rust: "Rs",
  ruby: "Rb",
  sql: "SQL",
};

export function languageName(id: string): string {
  return LANGUAGE_NAMES[id] ?? id;
}

export function languageTag(id: string): string {
  return LANGUAGE_TAGS[id] ?? id;
}
