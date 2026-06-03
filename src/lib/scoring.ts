import type { Prediction, MatchResult, ScorerRef } from "./types";

export const POINTS = {
  outcome: 2, // azzeccare 1X2
  perScorer: 1, // ogni marcatore azzeccato
  exactScore: 5, // risultato esatto (senza marcatori)
  exactScoreWithScorer: 10, // risultato esatto + almeno un marcatore
} as const;

export type Outcome = "1" | "X" | "2";

export function outcome(home: number, away: number): Outcome {
  if (home > away) return "1";
  if (home < away) return "2";
  return "X";
}

const scorerKey = (s: ScorerRef) => `${s.team}|||${s.name}`;

/** Numero di marcatori azzeccati, contando le doppiette (intersezione di multiset). */
export function countScorerHits(
  predicted: ScorerRef[],
  actual: ScorerRef[],
): number {
  const need = new Map<string, number>();
  for (const s of actual) need.set(scorerKey(s), (need.get(scorerKey(s)) ?? 0) + 1);
  let hits = 0;
  const used = new Map<string, number>();
  for (const s of predicted) {
    const k = scorerKey(s);
    const have = used.get(k) ?? 0;
    if (have < (need.get(k) ?? 0)) {
      hits++;
      used.set(k, have + 1);
    }
  }
  return hits;
}

export interface ScoreBreakdown {
  total: number;
  correctOutcome: boolean;
  exactScore: boolean;
  scorerHits: number;
  pointsOutcome: number;
  pointsScorers: number;
  pointsExactBonus: number;
  /** true quando i punti marcatori sono stati annullati per 1X2 sbagliato */
  voided: boolean;
}

/**
 * Regole:
 *  - 1X2 corretto: +2
 *  - ogni marcatore azzeccato: +1
 *  - risultato esatto senza marcatori: +5 ; con almeno un marcatore: +10
 *  - se il 1X2 è sbagliato, TUTTO va a 0 (i marcatori si annullano).
 */
export function computeScore(
  pred: Pick<Prediction, "home" | "away" | "scorers">,
  result: Pick<MatchResult, "home" | "away" | "scorers">,
): ScoreBreakdown {
  const correctOutcome = outcome(pred.home, pred.away) === outcome(result.home, result.away);
  const exactScore = pred.home === result.home && pred.away === result.away;
  const scorerHits = countScorerHits(pred.scorers, result.scorers);

  if (!correctOutcome) {
    return {
      total: 0,
      correctOutcome: false,
      exactScore: false,
      scorerHits,
      pointsOutcome: 0,
      pointsScorers: 0,
      pointsExactBonus: 0,
      voided: scorerHits > 0,
    };
  }

  const pointsOutcome = POINTS.outcome;
  const pointsScorers = scorerHits * POINTS.perScorer;
  const pointsExactBonus = exactScore
    ? scorerHits > 0
      ? POINTS.exactScoreWithScorer
      : POINTS.exactScore
    : 0;

  return {
    total: pointsOutcome + pointsScorers + pointsExactBonus,
    correctOutcome: true,
    exactScore,
    scorerHits,
    pointsOutcome,
    pointsScorers,
    pointsExactBonus,
    voided: false,
  };
}
