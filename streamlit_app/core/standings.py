"""Classifica calcolata da pronostici + risultati."""

from __future__ import annotations

from . import data, db
from .scoring import compute_score


def compute_standings() -> list[dict]:
    results = db.all_results()
    preds = db.all_predictions()

    rows = {
        p["id"]: {
            "id": p["id"],
            "name": p["name"],
            "points": 0,
            "played": 0,
            "exact": 0,
            "outcomes": 0,
            "scorer_hits": 0,
            "perfect": 0,
        }
        for p in data.PARTICIPANTS
    }

    for pred in preds:
        res = results.get(pred["match_id"])
        if not res:
            continue
        row = rows.get(pred["user_id"])
        if row is None:
            continue
        b = compute_score(pred, res)
        row["played"] += 1
        row["points"] += b.total
        if b.correct_outcome:
            row["outcomes"] += 1
        if b.exact_score:
            row["exact"] += 1
        row["scorer_hits"] += b.scorer_hits
        if b.exact_score and b.scorer_hits > 0:
            row["perfect"] += 1

    out = list(rows.values())
    out.sort(key=lambda r: (-r["points"], -r["exact"], -r["scorer_hits"], r["name"]))
    return out
