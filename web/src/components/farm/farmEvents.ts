/**
 * What the drone did, for the HUD: which events are new (each is played once, by
 * remembering the highest `n` seen), the short line each becomes, the "+N" it
 * adds to an item counter, and what the drone is doing right now.
 *
 * Pure functions on purpose (tests/test_farm_layout.py reads this file, and the
 * hook below only keeps the state).
 */

import { useEffect, useRef, useState } from "react";

import type { FarmEvent, FarmSnapshot } from "../../types";
import { itemName } from "./farmShared";

/** The events newer than `seen`. `seen` null means first load: nothing is replayed. */
export function diffEvents(events: FarmEvent[], seen: number | null): { fresh: FarmEvent[]; seen: number } {
  if (events.length === 0) return { fresh: [], seen: seen ?? 0 };
  const top = events.reduce((m, e) => Math.max(m, e.n), 0);
  if (seen === null) return { fresh: [], seen: top };
  // A farm that started over counts from the beginning again: do not wait for it to pass the old number.
  if (top < seen) return { fresh: [], seen: top };
  return { fresh: events.filter((e) => e.n > seen).sort((a, b) => a.n - b.n), seen: top };
}

/** One short line for the action log. */
export function eventLine(e: FarmEvent): string {
  const at = `(${e.x},${e.y})`;
  const plant = e.e ? itemName(e.e) : "plant";
  switch (e.k) {
    case "harvest": {
      if (!e.ok) return `Nothing ripe at ${at}`;
      const got = Object.entries(e.items ?? {})
        .filter(([, n]) => n > 0)
        .map(([item, n]) => `${itemName(item)} +${n.toLocaleString()}`)
        .join(", ");
      return `Harvested ${got || plant} at ${at}`;
    }
    case "plant":
      return e.ok ? `Planted ${plant} ${at}` : `Could not plant ${plant} ${at}`;
    case "till":
      return e.ok ? `Tilled ${at}` : `Could not till ${at}`;
    case "water":
      return e.ok ? `Watered ${at}` : `No water to use at ${at}`;
    case "fertilize":
      return e.ok ? `Fertilized ${at}` : `No fertilizer to use at ${at}`;
    case "swap":
      return e.ok ? `Swapped ${at}` : `Could not swap ${at}`;
    case "hat":
      return "Changed hat";
    case "unlock":
      return e.ok ? "Unlocked something" : "Could not unlock";
    default:
      return "";
  }
}

/** The "+N" each item counter gets from these events (ok harvests only). */
export function bumpsFor(events: FarmEvent[]): Record<string, number> {
  const out: Record<string, number> = {};
  for (const e of events) {
    if (e.k !== "harvest" || !e.ok) continue;
    for (const [item, n] of Object.entries(e.items ?? {})) {
      if (n > 0) out[item] = (out[item] ?? 0) + n;
    }
  }
  return out;
}

/** What the program's own drone (0) is doing, from its latest event within a second of farm time. */
export function droneDoing(snap: FarmSnapshot | undefined, running: boolean): string {
  const events = snap?.events ?? [];
  let latest: FarmEvent | null = null;
  for (const e of events) if (e.d === 0 && (!latest || e.n > latest.n)) latest = e;
  if (latest && snap && snap.time - latest.t <= 1.0 && snap.time - latest.t >= -0.05) {
    const plant = latest.e ? itemName(latest.e) : "";
    switch (latest.k) {
      case "harvest":
        return latest.ok ? `Harvesting ${plant}`.trim() : "Harvest: nothing ripe";
      case "plant":
        return latest.ok ? `Planting ${plant}`.trim() : "Planting failed";
      case "till":
        return "Tilling";
      case "water":
        return "Watering";
      case "fertilize":
        return "Fertilizing";
      case "swap":
        return "Swapping";
      case "hat":
        return "Changing hat";
      case "unlock":
        return "Unlocking";
    }
  }
  return running ? "Moving" : "";
}

export type LogEntry = { ev: FarmEvent; at: number };
export type Pop = { id: number; amount: number };

const LOG_KEEP = 5;
const LOG_LIFE_MS = 15000;
const POP_LIFE_MS = 1500;

/**
 * Follows the snapshots' events. `epoch` changes when the screen moves to another farm (or the
 * farm starts over): that farm's existing events are not replayed.
 */
export function useFarmEvents(snap: FarmSnapshot | undefined, epoch: number) {
  const seen = useRef<number | null>(null);
  const lastEpoch = useRef(epoch);
  const popId = useRef(0);
  const [log, setLog] = useState<LogEntry[]>([]);
  const [pops, setPops] = useState<Record<string, Pop>>({});

  useEffect(() => {
    if (lastEpoch.current !== epoch) {
      lastEpoch.current = epoch;
      seen.current = null;
      setLog([]);
      setPops({});
    }
    const events = snap?.events;
    if (!events) return;
    const got = diffEvents(events, seen.current);
    seen.current = got.seen;
    if (got.fresh.length === 0) return;
    const now = Date.now();
    setLog((was) => [...was, ...got.fresh.map((ev) => ({ ev, at: now }))].slice(-LOG_KEEP));
    const bumps = bumpsFor(got.fresh);
    const items = Object.keys(bumps);
    if (items.length) {
      const made: Record<string, Pop> = {};
      for (const item of items) {
        popId.current += 1;
        made[item] = { id: popId.current, amount: bumps[item] };
      }
      setPops((was) => ({ ...was, ...made }));
      window.setTimeout(() => {
        setPops((was) => {
          const next = { ...was };
          for (const item of items) if (next[item]?.id === made[item].id) delete next[item];
          return next;
        });
      }, POP_LIFE_MS);
    }
  }, [snap, epoch]);

  // Old lines go on their own.
  const any = log.length > 0;
  useEffect(() => {
    if (!any) return;
    const id = window.setInterval(() => {
      const cut = Date.now() - LOG_LIFE_MS;
      setLog((was) => (was.some((l) => l.at < cut) ? was.filter((l) => l.at >= cut) : was));
    }, 1000);
    return () => window.clearInterval(id);
  }, [any]);

  return { log, pops };
}
