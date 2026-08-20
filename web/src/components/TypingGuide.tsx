import { useEffect, useState } from "react";

import { fetchTypingGuide } from "../api";
import type { TypingGuide as Guide } from "../types";

/**
 * The teaching half of the trainer: which finger owns which key, why, the
 * technique that actually changes your speed, and the questions people ask.
 *
 * The hand diagram is drawn from the same finger assignments the drills use,
 * so what you're taught here and what the keyboard highlights during a run
 * can't drift apart.
 */

/** Left to right across the hand, so the diagram reads like a hand looks. */
const LEFT_ORDER = ["lp", "lr", "lm", "li"];
const RIGHT_ORDER = ["ri", "rm", "rr", "rp"];

/** How far each finger sits below the knuckle line, in rem — pinkies short,
 * middle fingers long. Purely so the drawing reads as a hand. */
const FINGER_LENGTH: Record<string, number> = {
  lp: 2.2,
  lr: 3.4,
  lm: 3.9,
  li: 3.2,
  ri: 3.2,
  rm: 3.9,
  rr: 3.4,
  rp: 2.2,
};

export default function TypingGuidePanel() {
  const [guide, setGuide] = useState<Guide | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [openFinger, setOpenFinger] = useState<string | null>(null);
  const [openQuestion, setOpenQuestion] = useState<number | null>(0);

  useEffect(() => {
    fetchTypingGuide()
      .then(setGuide)
      .catch((e: Error) => setError(e.message));
  }, []);

  if (error) {
    return <div className="typing-error">Couldn't load the guide: {error}</div>;
  }
  if (!guide) return <div className="typing-loading">Loading…</div>;

  const byId = Object.fromEntries(guide.fingers.map((f) => [f.finger, f]));

  const hand = (order: string[], label: string) => (
    <div className="tg-hand">
      <div className="tg-hand-label">{label} hand</div>
      <div className="tg-fingers">
        {order.map((id) => {
          const finger = byId[id];
          if (!finger) return null;
          const open = openFinger === id;
          return (
            <button
              key={id}
              type="button"
              className={`tg-finger tk-finger-${id} ${open ? "open" : ""}`}
              style={{ height: `${FINGER_LENGTH[id]}rem` }}
              onClick={() => setOpenFinger(open ? null : id)}
              title={finger.note}
            >
              <span className="tg-finger-home">
                {finger.home === "space" ? "␣" : finger.home}
              </span>
              <span className="tg-finger-keys">
                {finger.keys.join("").slice(0, 8)}
              </span>
            </button>
          );
        })}
      </div>
      <div className="tg-palm" />
    </div>
  );

  const openDetail = openFinger ? byId[openFinger] : null;

  return (
    <div className="typing-guide">
      <section className="tg-section">
        <h3>Which finger, and why</h3>
        <p className="tg-lede">
          Your fingers rest on <strong>a s d f</strong> and{" "}
          <strong>j k l ;</strong>. Every other key is a reach out from there
          and a return back. Tap a finger to see what it owns.
        </p>
        <div className="tg-hands">
          {hand(LEFT_ORDER, "Left")}
          {hand(RIGHT_ORDER, "Right")}
        </div>
        <div className="tg-thumb-row">
          <button
            type="button"
            className={`tg-thumb tk-finger-th ${
              openFinger === "th" ? "open" : ""
            }`}
            onClick={() => setOpenFinger(openFinger === "th" ? null : "th")}
          >
            thumb — space
          </button>
        </div>

        {openDetail ? (
          <div className="tg-detail">
            <h4>{openDetail.name}</h4>
            <p className="tg-detail-keys">
              rests on <code>{openDetail.home}</code> · owns{" "}
              {openDetail.keys
                .map((k) => (k === " " ? "space" : k))
                .join("  ")}
            </p>
            <p>{openDetail.note}</p>
          </div>
        ) : (
          <p className="tg-hint">Pick a finger above.</p>
        )}

        <div className="tg-homerow">
          {guide.home_row.map((k) => (
            <div
              key={k.char}
              className={`tg-homekey tk-finger-${k.finger} ${
                k.anchor ? "anchor" : ""
              }`}
              title={k.name}
            >
              {k.char}
              {k.anchor && <span className="tg-bump" />}
            </div>
          ))}
        </div>
        <p className="tg-caption">
          Home position. The two marked keys have a raised bump — find them by
          feel and everything else falls into place.
        </p>
      </section>

      <section className="tg-section">
        <h3>Technique</h3>
        <div className="tg-tips">
          {guide.tips.map((tip) => (
            <div className="tg-tip" key={tip.title}>
              <h4>{tip.title}</h4>
              <p>{tip.body}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="tg-section">
        <h3>Questions</h3>
        <div className="tg-faq">
          {guide.faq.map((item, i) => (
            <div className={`tg-q ${openQuestion === i ? "open" : ""}`} key={i}>
              <button
                type="button"
                onClick={() => setOpenQuestion(openQuestion === i ? null : i)}
              >
                {item.question}
                <span className="tg-caret">{openQuestion === i ? "−" : "+"}</span>
              </button>
              {openQuestion === i && <p>{item.answer}</p>}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
