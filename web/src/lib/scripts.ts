/**
 * Named script library — works in Free mode and coach mode.
 * Stored in localStorage; optional download as .py
 */

export type SavedScript = {
  id: string;
  name: string;
  code: string;
  updatedAt: number;
  source: "free" | "lesson" | "unknown";
};

const LIBRARY_KEY = "code-coach:script-library";

function uid(): string {
  return `scr-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 7)}`;
}

export function listScripts(): SavedScript[] {
  try {
    const raw = localStorage.getItem(LIBRARY_KEY);
    if (!raw) return [];
    const arr = JSON.parse(raw) as SavedScript[];
    return Array.isArray(arr)
      ? arr.sort((a, b) => b.updatedAt - a.updatedAt)
      : [];
  } catch {
    return [];
  }
}

function writeAll(scripts: SavedScript[]) {
  localStorage.setItem(LIBRARY_KEY, JSON.stringify(scripts));
}

export function saveScript(
  name: string,
  code: string,
  source: SavedScript["source"] = "unknown",
  existingId?: string,
): SavedScript {
  const scripts = listScripts();
  const trimmed = name.trim() || `script-${new Date().toISOString().slice(0, 10)}`;
  if (existingId) {
    const i = scripts.findIndex((s) => s.id === existingId);
    if (i >= 0) {
      scripts[i] = {
        ...scripts[i],
        name: trimmed,
        code,
        updatedAt: Date.now(),
        source,
      };
      writeAll(scripts);
      return scripts[i];
    }
  }
  // Upsert by name
  const byName = scripts.findIndex(
    (s) => s.name.toLowerCase() === trimmed.toLowerCase(),
  );
  if (byName >= 0) {
    scripts[byName] = {
      ...scripts[byName],
      code,
      updatedAt: Date.now(),
      source,
    };
    writeAll(scripts);
    return scripts[byName];
  }
  const entry: SavedScript = {
    id: uid(),
    name: trimmed,
    code,
    updatedAt: Date.now(),
    source,
  };
  scripts.unshift(entry);
  writeAll(scripts);
  return entry;
}

export function loadScript(id: string): SavedScript | null {
  return listScripts().find((s) => s.id === id) ?? null;
}

export function deleteScript(id: string): void {
  writeAll(listScripts().filter((s) => s.id !== id));
}

export function downloadScript(name: string, code: string): void {
  const safe = name.replace(/[^\w.-]+/g, "_") || "script";
  const blob = new Blob([code], { type: "text/x-python" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = safe.endsWith(".py") ? safe : `${safe}.py`;
  a.click();
  URL.revokeObjectURL(url);
}
