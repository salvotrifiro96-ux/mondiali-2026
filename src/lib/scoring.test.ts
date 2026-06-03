import { describe, it, expect } from "vitest";
import { computeScore, countScorerHits, outcome } from "./scoring";
import type { ScorerRef } from "./types";

const s = (team: string, name: string): ScorerRef => ({ team, name });

describe("outcome", () => {
  it("classifica 1 / X / 2", () => {
    expect(outcome(2, 0)).toBe("1");
    expect(outcome(1, 1)).toBe("X");
    expect(outcome(0, 3)).toBe("2");
  });
});

describe("countScorerHits", () => {
  it("conta i marcatori in comune", () => {
    const pred = [s("Argentina", "Messi"), s("Argentina", "Álvarez")];
    const act = [s("Argentina", "Messi"), s("Brazil", "Vinícius")];
    expect(countScorerHits(pred, act)).toBe(1);
  });

  it("gestisce le doppiette (multiset)", () => {
    const pred = [s("Argentina", "Messi"), s("Argentina", "Messi")];
    const act = [s("Argentina", "Messi"), s("Argentina", "Messi")];
    expect(countScorerHits(pred, act)).toBe(2);
  });

  it("non premia una doppietta prevista se segna una sola volta", () => {
    const pred = [s("Argentina", "Messi"), s("Argentina", "Messi")];
    const act = [s("Argentina", "Messi")];
    expect(countScorerHits(pred, act)).toBe(1);
  });
});

describe("computeScore", () => {
  it("1X2 corretto ma risultato non esatto, nessun marcatore", () => {
    const r = computeScore({ home: 2, away: 0, scorers: [] }, { home: 3, away: 1, scorers: [] });
    expect(r.total).toBe(2);
    expect(r.correctOutcome).toBe(true);
    expect(r.exactScore).toBe(false);
  });

  it("1X2 corretto + 2 marcatori (non esatto)", () => {
    const pred = { home: 2, away: 1, scorers: [s("Argentina", "Messi"), s("Argentina", "Álvarez")] };
    const act = { home: 3, away: 1, scorers: [s("Argentina", "Messi"), s("Argentina", "Álvarez"), s("Argentina", "Di María")] };
    const r = computeScore(pred, act);
    expect(r.total).toBe(2 + 2); // 1X2 + 2 marcatori
    expect(r.pointsExactBonus).toBe(0);
  });

  it("risultato esatto senza marcatori = 7 (2 + 5)", () => {
    const r = computeScore({ home: 2, away: 1, scorers: [] }, { home: 2, away: 1, scorers: [] });
    expect(r.exactScore).toBe(true);
    expect(r.total).toBe(2 + 5);
  });

  it("risultato esatto + 1 marcatore = 2 + 1 + 10 = 13", () => {
    const pred = { home: 2, away: 0, scorers: [s("Brazil", "Vinícius")] };
    const act = { home: 2, away: 0, scorers: [s("Brazil", "Vinícius"), s("Brazil", "Rodrygo")] };
    const r = computeScore(pred, act);
    expect(r.exactScore).toBe(true);
    expect(r.scorerHits).toBe(1);
    expect(r.total).toBe(2 + 1 + 10);
  });

  it("ESEMPIO UTENTE: 5-5 con tutti i marcatori ma finisce 3-2 -> 0 punti", () => {
    const allScorers = [
      s("Argentina", "Messi"),
      s("Argentina", "Álvarez"),
      s("Argentina", "Lautaro"),
      s("Netherlands", "Depay"),
      s("Netherlands", "Gakpo"),
    ];
    const pred = { home: 5, away: 5, scorers: allScorers };
    const act = { home: 3, away: 2, scorers: allScorers };
    const r = computeScore(pred, act);
    expect(r.total).toBe(0);
    expect(r.correctOutcome).toBe(false);
    expect(r.voided).toBe(true); // marcatori azzeccati ma annullati
    expect(r.scorerHits).toBe(5);
  });

  it("perfetto: risultato esatto + tutti i marcatori", () => {
    const sc = [s("Spain", "Yamal"), s("Spain", "Morata")];
    const r = computeScore({ home: 2, away: 0, scorers: sc }, { home: 2, away: 0, scorers: sc });
    expect(r.total).toBe(2 + 2 + 10);
  });
});
