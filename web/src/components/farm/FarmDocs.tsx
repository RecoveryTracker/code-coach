/** The Docs window: the commands (and the parts of the language) you have so far, in the language you are on. */

import type { FarmOverview } from "../../types";
import { FEATURE_UNLOCKS, signature, spellValue } from "./farmShared";

export function FarmDocs({ overview, language }: { overview: FarmOverview; language: string }) {
  const features = new Set(overview.features);
  return (
    <div className="fm-scroll fm-docs">
      <p className="fm-needs">
        Language you have:{" "}
        {Object.keys(FEATURE_UNLOCKS).map((f) => (
          <span key={f} className={`fm-feature${features.has(f) ? " on" : ""}`} title={`From ${FEATURE_UNLOCKS[f]}`}>
            {f}
          </span>
        ))}
      </p>
      {Object.entries(overview.names ?? {}).map(([group, members]) => (
        <p key={group} className="fm-values">
          <span className="fm-needs">{group}: </span>
          {members.map((m) => (
            <code key={m}>{spellValue(group, m, language)}</code>
          ))}
        </p>
      ))}
      {overview.functions
        .slice()
        .sort((a, b) => Number(b.unlocked) - Number(a.unlocked))
        .map((f) => (
          <div key={f.py} className={`fm-fn${f.unlocked ? "" : " locked"}`}>
            <code>{signature(f, language)}</code>
            <span>{f.unlocked ? f.doc : `needs ${f.unlock}`}</span>
          </div>
        ))}
    </div>
  );
}
