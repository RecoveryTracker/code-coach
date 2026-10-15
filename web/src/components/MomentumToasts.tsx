/**
 * The little rewards that appear after a success: "+20 XP", "Combo x1.4", "Lucky! x3 (+40)",
 * "Quest done: ...", and a LEVEL UP card with confetti.
 *
 * They sit bottom-centre above the footer, never take clicks (so they cannot sit on a Check
 * button), and go by themselves after about 2.5 seconds (the level-up card, 4 - and it
 * dismisses on a click or Escape). At most three show at once. Everything moves with CSS
 * animation, not requestAnimationFrame, and a reader who asked for reduced motion gets the
 * same words with no confetti and no bounce.
 */

import { useEffect } from "react";
import type { CSSProperties, ReactNode } from "react";
import { dismissToast, useMomentum } from "../lib/momentum";
import type { Toast } from "../lib/momentumView";

/** Fixed pieces, so the confetti is the same every time and nothing is random in a render. */
const CONFETTI = Array.from({ length: 28 }, (_, i) => ({
  x: ((i * 37) % 100) - 50,
  delay: ((i * 53) % 40) / 100,
  hue: (i * 47) % 360,
  spin: ((i * 71) % 360) - 180,
}));

function ToastItem({ t }: { t: Toast }): ReactNode {
  useEffect(() => {
    const id = window.setTimeout(() => dismissToast(t.id), t.ms);
    return () => window.clearTimeout(id);
  }, [t.id, t.ms]);

  if (t.kind === "level") {
    return (
      <div className="mt-card" role="button" tabIndex={0} onClick={() => dismissToast(t.id)} onKeyDown={(e) => { if (e.key === "Escape" || e.key === "Enter") dismissToast(t.id); }} title="Click to dismiss">
        <div className="mt-confetti" aria-hidden="true">
          {CONFETTI.map((c, i) => (
            <span
              key={i}
              style={{
                "--x": `${c.x * 3}px`,
                "--d": `${c.delay}s`,
                "--h": c.hue,
                "--r": `${c.spin}deg`,
              } as CSSProperties}
            />
          ))}
        </div>
        <div className="mt-card-kicker">LEVEL UP</div>
        <div className="mt-card-level">{t.text}</div>
        <div className="mt-card-title">{t.sub}</div>
      </div>
    );
  }
  return (
    <div className={`mt-toast ${t.kind}`}>
      {t.text}
    </div>
  );
}

export function MomentumToasts(): ReactNode {
  const { toasts } = useMomentum();
  const hasLevel = toasts.some((t) => t.kind === "level");
  useEffect(() => {
    if (!hasLevel) return;
    const key = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      for (const t of toasts) if (t.kind === "level") dismissToast(t.id);
    };
    document.addEventListener("keydown", key);
    return () => document.removeEventListener("keydown", key);
  }, [hasLevel, toasts]);
  return (
    <div className="mt-stack" aria-live="polite" aria-atomic="false" role="status">
      {toasts.filter((t) => t.kind === "level").map((t) => (
        <ToastItem key={t.id} t={t} />
      ))}
      <div className="mt-row">
        {toasts.filter((t) => t.kind !== "level").map((t) => (
          <ToastItem key={t.id} t={t} />
        ))}
      </div>
    </div>
  );
}
