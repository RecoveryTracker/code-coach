/** The program of a Gotchas card, coloured: shared by the quiz card and My traps. */

import { useMemo } from "react";

import { tokenize } from "../lib/codeColors";
import type { Syntax } from "../lib/codeColors";

/** The program, coloured, as real text in a <pre> (selectable, readable by a screen reader). */
export function CodeBlock({
  code,
  label,
  syntax,
  compact = false,
}: {
  code: string;
  label: string;
  syntax?: Syntax;
  compact?: boolean;
}) {
  const runs = useMemo(() => tokenize(code, syntax), [code, syntax]);
  return (
    <pre className={`gq-code${compact ? " compact" : ""}`} tabIndex={0} aria-label={`${label} code`}>
      <code>
        {runs.map((r, i) => (
          <span key={i} className={`tk-${r.kind}`}>
            {r.text}
          </span>
        ))}
      </code>
    </pre>
  );
}
