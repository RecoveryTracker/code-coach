/** Small icons drawn inline (no assets): the windows' glyphs and the items' coloured ones. */

import type { ReactNode } from "react";

function Glyph({ children, size = 18 }: { children: ReactNode; size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      focusable="false"
    >
      {children}
    </svg>
  );
}

export const CodeIcon = ({ size }: { size?: number }) => (
  <Glyph size={size}>
    <path d="M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16" />
  </Glyph>
);

export const OutputIcon = ({ size }: { size?: number }) => (
  <Glyph size={size}>
    <rect x="3" y="4" width="18" height="16" rx="2" />
    <path d="M7 10l3 2-3 2M12 15h5" />
  </Glyph>
);

export const ResearchIcon = ({ size }: { size?: number }) => (
  <Glyph size={size}>
    <circle cx="6" cy="6" r="2.2" />
    <circle cx="18" cy="12" r="2.2" />
    <circle cx="6" cy="18" r="2.2" />
    <path d="M8 6h4a3 3 0 013 3v1M8 18h4a3 3 0 003-3v-1" />
  </Glyph>
);

export const DocsIcon = ({ size }: { size?: number }) => (
  <Glyph size={size}>
    <path d="M4 5a2 2 0 012-2h13v16H6a2 2 0 00-2 2V5z" />
    <path d="M8 8h7M8 12h7" />
  </Glyph>
);

export const PlaybookIcon = ({ size }: { size?: number }) => (
  <Glyph size={size}>
    <path d="M12 3l2.6 5.6 6 .8-4.4 4.2 1.1 6-5.3-2.9-5.3 2.9 1.1-6L3.4 9.4l6-.8L12 3z" />
  </Glyph>
);

export const ResetIcon = ({ size }: { size?: number }) => (
  <Glyph size={size}>
    <path d="M3 12a9 9 0 109-9 9 9 0 00-6.4 2.7L3 8M3 3v5h5" />
  </Glyph>
);

export const MinimiseIcon = () => (
  <Glyph size={14}>
    <path d="M5 18h14" />
  </Glyph>
);

export const RestoreIcon = () => (
  <Glyph size={14}>
    <rect x="5" y="5" width="14" height="14" rx="1.5" />
  </Glyph>
);

export const CloseIcon = () => (
  <Glyph size={14}>
    <path d="M6 6l12 12M18 6L6 18" />
  </Glyph>
);

export const PlayIcon = () => (
  <Glyph size={14}>
    <path d="M7 4l13 8-13 8V4z" fill="currentColor" />
  </Glyph>
);

export const StopIcon = () => (
  <Glyph size={14}>
    <rect x="5" y="5" width="14" height="14" rx="2" fill="currentColor" />
  </Glyph>
);

/** One coloured glyph per item, in a 16 by 16 box. */
export function ItemIcon({ item, size = 16 }: { item: string; size?: number }) {
  let art: ReactNode;
  switch (item) {
    case "Hay":
      art = (
        <>
          <path d="M3 14L5 3M8 14V2M13 14L11 3" stroke="#e8c547" strokeWidth="2" strokeLinecap="round" />
          <rect x="2" y="9" width="12" height="2.4" rx="1" fill="#b98a2c" />
        </>
      );
      break;
    case "Wood":
      art = (
        <>
          <rect x="1.5" y="4" width="12" height="8" rx="2" fill="#8a5a2b" />
          <ellipse cx="12" cy="8" rx="2.6" ry="4" fill="#d3a468" />
          <ellipse cx="12" cy="8" rx="1" ry="1.8" fill="#8a5a2b" />
        </>
      );
      break;
    case "Carrot":
      art = (
        <>
          <path d="M3 4.5c2-2 8-2 10 0L8.6 15c-.3.6-1 .6-1.2 0L3 4.5z" fill="#f08a24" />
          <path d="M6 4l-1-3M8 4V1M10 4l1-3" stroke="#5fbf5a" strokeWidth="1.6" strokeLinecap="round" />
        </>
      );
      break;
    case "Pumpkin":
      art = (
        <>
          <ellipse cx="8" cy="9.5" rx="6.4" ry="5" fill="#e8721c" />
          <path d="M8 4.6c-1.6 1.6-1.6 7.2 0 9.8M8 4.6c1.6 1.6 1.6 7.2 0 9.8" stroke="#a84a0c" strokeWidth="1" fill="none" />
          <rect x="7" y="2" width="2" height="3" rx="1" fill="#4f8f3a" />
        </>
      );
      break;
    case "Power":
      art = <path d="M9.5 1L3 9h4l-1 6 7-8.5H9l.5-5.5z" fill="#ffd93b" />;
      break;
    case "Cactus":
      art = (
        <>
          <rect x="6" y="2" width="4" height="13" rx="2" fill="#4caf6a" />
          <path d="M6 9H4V6M10 8h2V5" stroke="#4caf6a" strokeWidth="2.2" strokeLinecap="round" fill="none" />
        </>
      );
      break;
    case "Bone":
      art = (
        <path
          d="M3.6 5.4a1.8 1.8 0 112.4-1.6L11 9a1.8 1.8 0 111.6 2.4 1.8 1.8 0 11-2.6 1.6L5 7.2a1.8 1.8 0 01-1.4-1.8z"
          fill="#efe8d6"
        />
      );
      break;
    case "Gold":
      art = (
        <>
          <circle cx="8" cy="8" r="6.3" fill="#e9b81f" />
          <circle cx="8" cy="8" r="3.8" fill="none" stroke="#a97c0c" strokeWidth="1.2" />
        </>
      );
      break;
    case "Weird_Substance":
      art = (
        <>
          <path d="M6 2h4v4l3.5 6.4A1.6 1.6 0 0112.1 15H3.9a1.6 1.6 0 01-1.4-2.6L6 6V2z" fill="#9b5de5" />
          <circle cx="7" cy="11" r="1.1" fill="#e0c3ff" />
          <circle cx="10" cy="12.2" r=".8" fill="#e0c3ff" />
        </>
      );
      break;
    case "Water":
      art = <path d="M8 1.5C5.5 5 3.5 7.2 3.5 9.8a4.5 4.5 0 009 0C12.5 7.2 10.5 5 8 1.5z" fill="#4aa8ff" />;
      break;
    case "Fertilizer":
      art = (
        <>
          <path d="M4 5h8l1.5 9h-11L4 5z" fill="#7a8f3a" />
          <path d="M5 5l1-3h4l1 3" fill="#a3b95a" />
          <circle cx="8" cy="10" r="1.6" fill="#3f4d1c" />
        </>
      );
      break;
    default:
      art = <circle cx="8" cy="8" r="5.5" fill="#8b98a8" />;
  }
  return (
    <svg
      className="fm-item-icon"
      width={size}
      height={size}
      viewBox="0 0 16 16"
      aria-hidden="true"
      focusable="false"
    >
      {art}
    </svg>
  );
}
