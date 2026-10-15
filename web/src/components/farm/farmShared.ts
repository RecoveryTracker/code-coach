/** Names, spellings and small formatters the Farm's windows share. */

import type { FarmFunction, FarmRun } from "../../types";

export const LANGUAGE_NAMES: Record<string, string> = {
  original: "Original",
  python: "Python",
  javascript: "JavaScript",
  dart: "Dart",
};
export const LANGUAGE_TIPS: Record<string, string> = {
  original: "The game's own language: Python's syntax, and every operation costs ticks, as in the game",
  python: "Real Python - only drone commands cost game time",
  javascript: "Real JavaScript (Node) - only drone commands cost game time",
  dart: "Real Dart - only drone commands cost game time",
};
export const EXTENSIONS: Record<string, string> = { original: ".py", python: ".py", javascript: ".js", dart: ".dart" };
export const FEATURE_UNLOCKS: Record<string, string> = {
  while: "Loops", if: "Speed", for: "Expand 2", operators: "Operators", variables: "Variables",
  functions: "Functions", lists: "Lists", dicts: "Dictionaries", import: "Import",
};

/** Items.Weird_Substance, spelled the way each language spells it. */
export function spellValue(group: string, member: string, language: string): string {
  const pascal = member.split("_").map((p) => p.charAt(0).toUpperCase() + p.slice(1)).join("");
  if (group === "Directions") return language === "dart" ? member.toLowerCase() : member;
  if (language === "javascript") return `${group}.${pascal}`;
  if (language === "dart") return `${group}.${pascal.charAt(0).toLowerCase()}${pascal.slice(1)}`;
  return `${group}.${member}`;
}

export function itemName(item: string): string {
  return item.replace(/_/g, " ");
}

export function costText(cost: Record<string, number> | null): string {
  if (!cost) return "";
  return Object.entries(cost)
    .map(([item, n]) => `${n.toLocaleString()} ${itemName(item)}`)
    .join(" + ");
}

/** How a function reads in the chosen language, with its parameters. */
export function signature(f: FarmFunction, language: string): string {
  const name = language === "javascript" ? f.js : language === "dart" ? f.dart : f.py;
  const params = f.params.map((p) => {
    const bare = p.replace(/=.*/, "").replace(/^\*/, language === "javascript" || language === "dart" ? "..." : "*");
    if (language === "python" || language === "original") return p;
    return p.includes("=") ? `${bare}?` : bare;
  });
  return `${name}(${params.join(", ")})`;
}

/** What the run is doing, in a few words (the HUD and the Output window both say it). */
export function runText(run: FarmRun | null, multiFile: boolean): string {
  if (!run) return "";
  if (run.status === "running") {
    return `running · ${run.commands} commands${run.drones && run.drones > 1 ? ` · ${run.drones} drones` : ""}`;
  }
  if (run.status === "error") {
    return `stopped with an error${run.line ? ` on line ${run.line}` : ""}${run.file && multiFile ? ` of ${run.file}` : ""}`;
  }
  return run.status;
}
