/**
 * Which skin the app wears, remembered per browser.
 *
 * The palettes live in styles/skins.css. This file only knows the
 * names, which one is chosen, and how to put it on the page. Original
 * is the absence of a skin rather than a skin of its own: choosing it
 * removes the attribute, so every colour falls back to the value it
 * had before skins existed. That is what keeps it exact.
 *
 * Remembered in localStorage rather than in the progress file, because
 * it is a preference about this screen, not a fact about what you have
 * learned - two people sharing a copy of the app should each get their
 * own look without overwriting each other's.
 */

import type { Monaco } from "@monaco-editor/react";
import { useEffect, useState } from "react";

export type SkinId =
  | "original"
  | "dark"
  | "purple"
  | "light"
  | "aurora"
  | "arcade";

export type Skin = {
  id: SkinId;
  name: string;
  hint: string;
  /** Light background, so the editor wants a light theme under it. */
  light: boolean;
};

export const SKINS: Skin[] = [
  {
    id: "original",
    name: "Original",
    hint: "The look it has always had.",
    light: false,
  },
  {
    id: "dark",
    name: "Dark",
    hint: "Deeper and more neutral — near-black, plain greys.",
    light: false,
  },
  {
    id: "purple",
    name: "Purple",
    hint: "Dark, in violet and lavender.",
    light: false,
  },
  {
    id: "light",
    name: "Light",
    hint: "The ordinary daytime look.",
    light: true,
  },
  {
    id: "aurora",
    name: "Northern Lights",
    hint: "A night sky, with the aurora across the top.",
    light: false,
  },
  {
    id: "arcade",
    name: "Arcade",
    hint: "Bright primaries — red, yellow, blue and green on a sky-blue day.",
    light: true,
  },
];

const KEY = "code-coach:skin";
const EVENT = "code-coach:skin-change";

function isSkin(value: unknown): value is SkinId {
  return SKINS.some((s) => s.id === value);
}

/** The saved skin, or Original when there is none or it is unreadable. */
export function savedSkin(): SkinId {
  try {
    const raw = localStorage.getItem(KEY);
    return isSkin(raw) ? raw : "original";
  } catch {
    // A private window or blocked storage costs the preference and
    // nothing else.
    return "original";
  }
}

/** Put a skin on the page, remember it, and tell anyone listening. */
export function applySkin(id: SkinId): void {
  const root = document.documentElement;
  if (id === "original") root.removeAttribute("data-skin");
  else root.setAttribute("data-skin", id);
  try {
    localStorage.setItem(KEY, id);
  } catch {
    /* see savedSkin */
  }
  window.dispatchEvent(new CustomEvent(EVENT, { detail: id }));
}

/** The current skin, kept up to date when it changes anywhere. */
export function useSkin(): SkinId {
  const [skin, setSkin] = useState<SkinId>(savedSkin);
  useEffect(() => {
    const on = (e: Event) => setSkin((e as CustomEvent<SkinId>).detail);
    window.addEventListener(EVENT, on);
    return () => window.removeEventListener(EVENT, on);
  }, []);
  return skin;
}

/**
 * One of a skin's role colours, read from the stylesheet.
 *
 * Asked of the CSS rather than written out again here: a small element
 * carrying the skin's attribute resolves the skin's --r-* variables, so
 * the editor theme and the picker's swatches are drawn from exactly the
 * values the app uses. A second list of hex codes in this file would be
 * right until the first time someone tuned a skin.
 */
export function skinColor(id: SkinId, role: string): string {
  const probe = document.createElement("span");
  probe.setAttribute("data-skin", id);
  probe.style.display = "none";
  document.body.appendChild(probe);
  const value = getComputedStyle(probe).getPropertyValue(`--r-${role}`).trim();
  probe.remove();
  return value;
}

/** Monaco wants six-digit hex; anything else is left to its default. */
function hex(value: string): string | undefined {
  return /^#[0-9a-f]{6}$/i.test(value) ? value : undefined;
}

/**
 * Register an editor theme for every skin, and say which to use.
 *
 * Original keeps vs-dark untouched, for the same reason it keeps
 * everything else. The others take their base from whether the skin is
 * light, and their surface colours from the skin itself, so the editor
 * does not sit in the page as a black box on a light skin or a grey one
 * on Northern Lights.
 */
export function defineEditorThemes(monaco: Monaco): void {
  for (const skin of SKINS) {
    if (skin.id === "original") continue;
    const colors: Record<string, string> = {};
    const set = (key: string, role: string) => {
      const value = hex(skinColor(skin.id, role));
      if (value) colors[key] = value;
    };
    set("editor.background", "bg-panel");
    set("editorGutter.background", "bg-panel");
    set("editor.lineHighlightBackground", "bg-elevated");
    set("editorLineNumber.foreground", "text-dim");
    set("editorLineNumber.activeForeground", "text-muted");
    set("editorCursor.foreground", "accent");
    set("editor.selectionBackground", "accent-soft");
    set("editorWidget.background", "bg-elevated");
    set("editorWidget.border", "border");
    monaco.editor.defineTheme(`cc-${skin.id}`, {
      base: skin.light ? "vs" : "vs-dark",
      inherit: true,
      rules: [],
      colors,
    });
  }
}

export function editorThemeFor(id: SkinId): string {
  return id === "original" ? "vs-dark" : `cc-${id}`;
}
