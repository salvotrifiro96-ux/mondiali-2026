import { useSyncExternalStore } from "react";
import type { Prediction, MatchResult, ScorerRef } from "./types";

const KEY_PRED = "wc26.predictions";
const KEY_RES = "wc26.results";
const KEY_USER = "wc26.currentUser";

export interface StoreState {
  predictions: Prediction[];
  results: Record<number, MatchResult>;
}

function load<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : fallback;
  } catch {
    return fallback;
  }
}

let state: StoreState = {
  predictions: load<Prediction[]>(KEY_PRED, []),
  results: load<Record<number, MatchResult>>(KEY_RES, {}),
};

const listeners = new Set<() => void>();
function emit() {
  for (const l of listeners) l();
}
function persist() {
  localStorage.setItem(KEY_PRED, JSON.stringify(state.predictions));
  localStorage.setItem(KEY_RES, JSON.stringify(state.results));
}

export const store = {
  getState: () => state,
  subscribe(cb: () => void) {
    listeners.add(cb);
    return () => listeners.delete(cb);
  },
  setPrediction(p: Prediction) {
    const others = state.predictions.filter(
      (x) => !(x.matchId === p.matchId && x.userId === p.userId),
    );
    state = { ...state, predictions: [...others, p] };
    persist();
    emit();
  },
  setResult(r: MatchResult) {
    state = { ...state, results: { ...state.results, [r.matchId]: r } };
    persist();
    emit();
  },
  removeResult(matchId: number) {
    const next = { ...state.results };
    delete next[matchId];
    state = { ...state, results: next };
    persist();
    emit();
  },
};

export function useStore(): StoreState {
  return useSyncExternalStore(store.subscribe, store.getState, store.getState);
}

// helper di lettura
export function getPrediction(
  s: StoreState,
  matchId: number,
  userId: string,
): Prediction | undefined {
  return s.predictions.find((p) => p.matchId === matchId && p.userId === userId);
}

export function emptyPrediction(matchId: number, userId: string): Prediction {
  return { matchId, userId, home: 0, away: 0, scorers: [], updatedAt: "" };
}

export const sameScorer = (a: ScorerRef, b: ScorerRef) =>
  a.team === b.team && a.name === b.name;

// utente corrente (persistito)
export function loadCurrentUser(): string {
  return localStorage.getItem(KEY_USER) ?? "";
}
export function saveCurrentUser(id: string) {
  localStorage.setItem(KEY_USER, id);
}
