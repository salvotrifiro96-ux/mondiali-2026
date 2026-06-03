"""Logica di punteggio del fantamondiale 2026.

Regole:
  - 1X2 corretto: +2
  - ogni marcatore azzeccato: +1 (le doppiette contano, intersezione di multiset)
  - risultato esatto senza marcatori: +5 ; con almeno un marcatore: +10 (cumulativo)
  - se il 1X2 è sbagliato, TUTTO va a 0 (i marcatori si annullano).
"""

from __future__ import annotations

from dataclasses import dataclass

POINTS = {
    "outcome": 2,
    "per_scorer": 1,
    "exact_score": 5,
    "exact_score_with_scorer": 10,
}


def outcome(home: int, away: int) -> str:
    if home > away:
        return "1"
    if home < away:
        return "2"
    return "X"


def _scorer_key(s: dict) -> str:
    return f"{s['team']}|||{s['name']}"


def count_scorer_hits(predicted: list[dict], actual: list[dict]) -> int:
    """Numero di marcatori azzeccati, contando le doppiette."""
    need: dict[str, int] = {}
    for s in actual:
        k = _scorer_key(s)
        need[k] = need.get(k, 0) + 1
    hits = 0
    used: dict[str, int] = {}
    for s in predicted:
        k = _scorer_key(s)
        have = used.get(k, 0)
        if have < need.get(k, 0):
            hits += 1
            used[k] = have + 1
    return hits


@dataclass
class ScoreBreakdown:
    total: int
    correct_outcome: bool
    exact_score: bool
    scorer_hits: int
    points_outcome: int
    points_scorers: int
    points_exact_bonus: int
    voided: bool


def compute_score(pred: dict, result: dict) -> ScoreBreakdown:
    """pred/result: {home:int, away:int, scorers:[{team,name}]}."""
    correct = outcome(pred["home"], pred["away"]) == outcome(result["home"], result["away"])
    exact = pred["home"] == result["home"] and pred["away"] == result["away"]
    hits = count_scorer_hits(pred.get("scorers", []), result.get("scorers", []))

    if not correct:
        return ScoreBreakdown(
            total=0,
            correct_outcome=False,
            exact_score=False,
            scorer_hits=hits,
            points_outcome=0,
            points_scorers=0,
            points_exact_bonus=0,
            voided=hits > 0,
        )

    p_outcome = POINTS["outcome"]
    p_scorers = hits * POINTS["per_scorer"]
    if exact:
        p_exact = POINTS["exact_score_with_scorer"] if hits > 0 else POINTS["exact_score"]
    else:
        p_exact = 0

    return ScoreBreakdown(
        total=p_outcome + p_scorers + p_exact,
        correct_outcome=True,
        exact_score=exact,
        scorer_hits=hits,
        points_outcome=p_outcome,
        points_scorers=p_scorers,
        points_exact_bonus=p_exact,
        voided=False,
    )
