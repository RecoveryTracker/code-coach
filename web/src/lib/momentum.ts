/**
 * Momentum on the client: one call to make at a success, and a small store the strip
 * and the toasts read.
 *
 * A mode reports a real success with `award(kind, key)` and carries on. It never waits
 * for the answer, never sees an error, and a server that is down, slow or confused
 * costs the mode nothing: this file swallows every failure. `kind` is one of the
 * server's priced kinds (code_coach/momentum/rules.py XP) and `key` is the stable id
 * of the thing done (a page, a problem, a step), so doing it again the same day pays
 * nothing. The client sends no amounts.
 */

import { useSyncExternalStore } from "react";
import {
  dismiss,
  enqueue,
  toastsForAward,
  toastsForChest,
} from "./momentumView";
import type {
  AwardResult,
  ChestResult,
  MomentumSummary,
  Toast,
} from "./momentumView";

export interface MomentumState {
  summary: MomentumSummary | null;
  toasts: Toast[];
}

let state: MomentumState = { summary: null, toasts: [] };
const listeners = new Set<() => void>();
let counter = 0;

function nextId(): number {
  counter += 1;
  return counter;
}

function set(next: MomentumState): void {
  state = next;
  listeners.forEach((l) => l());
}

function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => {
    listeners.delete(listener);
  };
}

function snapshot(): MomentumState {
  return state;
}

/** The latest summary and the toasts on screen. */
export function useMomentum(): MomentumState {
  return useSyncExternalStore(subscribe, snapshot, snapshot);
}

async function call<T>(path: string, method: "GET" | "POST", body?: unknown): Promise<T | null> {
  const res = await fetch(path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!res.ok) return null;
  return (await res.json()) as T;
}

/** Report a success. Fire and forget: it cannot throw, block, or fail the caller. */
export function award(kind: string, key: string): void {
  try {
    void call<AwardResult>("/api/momentum/award", "POST", { kind, key })
      .then((r) => {
        if (!r || !r.ok) return;
        set({
          summary: r,
          toasts: enqueue(state.toasts, toastsForAward(r, nextId)),
        });
      })
      .catch(() => {
        /* the server being away is not the mode's problem */
      });
  } catch {
    /* same */
  }
}

/** Read where you stand (when the app opens, and whenever the strip wants fresh numbers). */
export async function refresh(): Promise<void> {
  try {
    const r = await call<MomentumSummary>("/api/momentum", "GET");
    if (r && r.ok) set({ ...state, summary: r });
  } catch {
    /* quiet */
  }
}

/** Open today's chest. */
export async function claimChest(): Promise<void> {
  try {
    const r = await call<ChestResult>("/api/momentum/chest", "POST");
    if (!r) return;
    if (r.ok) {
      set({ summary: r, toasts: enqueue(state.toasts, toastsForChest(r, nextId)) });
    } else {
      await refresh();
    }
  } catch {
    /* quiet */
  }
}

export function dismissToast(id: number): void {
  set({ ...state, toasts: dismiss(state.toasts, id) });
}
