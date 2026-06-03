import type { StoreState } from "./store";
import { computeScore } from "./scoring";
import { PARTICIPANTS } from "./data";
import { getPrediction } from "./store";

export interface Row {
  id: string;
  name: string;
  points: number;
  played: number; // partite con risultato per cui aveva un pronostico
  exact: number; // risultati esatti azzeccati
  outcomes: number; // 1X2 azzeccati
  scorerHits: number; // marcatori azzeccati (validi)
  perfect: number; // esatto + marcatore (10)
}

export function computeStandings(s: StoreState): Row[] {
  const resultIds = Object.keys(s.results).map(Number);
  const rows: Row[] = PARTICIPANTS.map((p) => ({
    id: p.id,
    name: p.name,
    points: 0,
    played: 0,
    exact: 0,
    outcomes: 0,
    scorerHits: 0,
    perfect: 0,
  }));
  const byId = new Map(rows.map((r) => [r.id, r]));

  for (const mid of resultIds) {
    const result = s.results[mid];
    for (const p of PARTICIPANTS) {
      const pred = getPrediction(s, mid, p.id);
      if (!pred) continue;
      const b = computeScore(pred, result);
      const row = byId.get(p.id)!;
      row.played++;
      row.points += b.total;
      if (b.correctOutcome) row.outcomes++;
      if (b.exactScore) row.exact++;
      if (!b.voided) row.scorerHits += b.scorerHits;
      if (b.pointsExactBonus === 10) row.perfect++;
    }
  }

  return rows.sort(
    (a, b) =>
      b.points - a.points ||
      b.perfect - a.perfect ||
      b.exact - a.exact ||
      b.scorerHits - a.scorerHits ||
      a.name.localeCompare(b.name),
  );
}
