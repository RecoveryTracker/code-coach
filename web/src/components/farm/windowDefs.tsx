/** What each window is called and looks like - the menu and the windows' title bars both read this. */

import type { ReactNode } from "react";

import { CodeIcon, DocsIcon, OutputIcon, PlaybookIcon, ResearchIcon } from "./FarmIcons";
import type { WinId } from "./useFarmWindows";

export type WindowDef = { title: string; hint: string; icon: ReactNode };

export const WINDOW_DEFS: Record<WinId, WindowDef> = {
  code: { title: "Code", hint: "Your program, and Run", icon: <CodeIcon /> },
  output: { title: "Output", hint: "What your program prints, and its errors", icon: <OutputIcon /> },
  research: { title: "Research", hint: "Spend what you harvest on unlocks", icon: <ResearchIcon /> },
  docs: { title: "Docs", hint: "The commands, and what you can use so far", icon: <DocsIcon /> },
  playbook: { title: "Playbook", hint: "Tips and snippets to add to your code", icon: <PlaybookIcon /> },
};
