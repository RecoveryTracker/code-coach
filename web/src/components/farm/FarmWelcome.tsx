/**
 * The welcome-back card: a small, dismissible note over the scene when the Farm is opened after
 * half an hour or more away. It says how many tiles are ripe (or that the farm is quiet) and
 * offers one click to claim the day's welcome-back XP.
 *
 * It is calm on purpose: no clock, no count-down, nothing about what could be lost, and the
 * line under the count says the honest thing - the farm does not run while you are away. The
 * server decided there was an absence and works out the pay; this only shows the offer.
 *
 * Where it sits: on a wide screen at the top of the scene beside the Code window (clear of the
 * HUD above it and of the Run button and the Output window), on a narrow one just above the menu
 * along the bottom edge (the Code window's toolbar, with Run, is at the top there).
 */

import type { CSSProperties } from "react";
import { welcomeView } from "../../lib/momentumView";
import type { WelcomeBack } from "../../lib/momentumView";

type Props = {
  welcome: WelcomeBack;
  /** True when the Code window is full width (a narrow screen). */
  narrow: boolean;
  /** Left edge, on a wide screen: just right of the Code window. */
  left: number;
  /** Top edge, on a wide screen: just under the HUD. */
  top: number;
  /** Bottom edge, on a narrow screen: just above the menu. */
  bottom: number;
  onClaim: () => void;
  onDismiss: () => void;
};

export function FarmWelcome({ welcome, narrow, left, top, bottom, onClaim, onDismiss }: Props) {
  const v = welcomeView(welcome);
  const style: CSSProperties = narrow ? { left: 10, right: 10, bottom } : { left, top };
  return (
    <section className={`fm-welcome${narrow ? " narrow" : ""}`} style={style} aria-label={v.title}>
      <button type="button" className="fm-welcome-x" onClick={onDismiss} aria-label="Dismiss" title="Dismiss">
        ×
      </button>
      <h2 className="fm-welcome-title">{v.title}</h2>
      <p className="fm-welcome-body">{v.body}</p>
      <p className="fm-welcome-note">{v.note}</p>
      <div className="fm-welcome-actions">
        <button type="button" className="fm-btn primary" onClick={onClaim}>
          {v.claim}
        </button>
        <button type="button" className="fm-btn" onClick={onDismiss}>
          {v.dismiss}
        </button>
      </div>
    </section>
  );
}
