"""Test della logica di punteggio. Esegui: python -m core.test_scoring"""

from .scoring import compute_score, count_scorer_hits, outcome


def _s(team, name):
    return {"team": team, "name": name}


def run():
    checks = []

    def expect(label, got, want):
        ok = got == want
        checks.append((label, ok, got, want))

    # outcome base
    expect("outcome 2-1", outcome(2, 1), "1")
    expect("outcome 0-0", outcome(0, 0), "X")
    expect("outcome 1-3", outcome(1, 3), "2")

    A, B = "Argentina", "Netherlands"

    # 1X2 giusto, niente marcatori, non esatto
    expect(
        "1X2 ok no marcatori",
        compute_score({"home": 2, "away": 1, "scorers": []},
                      {"home": 3, "away": 0, "scorers": []}).total,
        2,
    )

    # risultato esatto senza marcatori
    expect(
        "esatto senza marcatori",
        compute_score({"home": 2, "away": 1, "scorers": []},
                      {"home": 2, "away": 1, "scorers": []}).total,
        2 + 5,
    )

    # 1X2 + 2 marcatori giusti, non esatto
    expect(
        "1X2 + 2 marcatori",
        compute_score(
            {"home": 3, "away": 1, "scorers": [_s(A, "Messi"), _s(A, "Alvarez")]},
            {"home": 2, "away": 0, "scorers": [_s(A, "Messi"), _s(A, "Alvarez")]},
        ).total,
        2 + 2,
    )

    # esatto + marcatori = bonus 10 cumulativo
    b = compute_score(
        {"home": 2, "away": 1, "scorers": [_s(A, "Messi"), _s(B, "Depay")]},
        {"home": 2, "away": 1, "scorers": [_s(A, "Messi"), _s(B, "Depay")]},
    )
    expect("esatto + 2 marcatori totale", b.total, 2 + 2 + 10)
    expect("esatto + marcatori bonus", b.points_exact_bonus, 10)

    # esempio dell'utente: 5-5 con tutti i marcatori ma finisce 3-2 -> 0 punti
    z = compute_score(
        {"home": 5, "away": 5, "scorers": [_s(A, "Messi")] * 5 + [_s(B, "Depay")] * 5},
        {"home": 3, "away": 2, "scorers": [_s(A, "Messi")] * 3 + [_s(B, "Depay")] * 2},
    )
    expect("5-5 -> 3-2 = 0", z.total, 0)
    expect("5-5 -> 3-2 voided", z.voided, True)

    # doppietta: predetto Messi x2, reale Messi x2 -> 2 hit
    expect(
        "doppietta",
        count_scorer_hits([_s(A, "Messi"), _s(A, "Messi")],
                          [_s(A, "Messi"), _s(A, "Messi")]),
        2,
    )
    # predetto x2 ma reale x1 -> 1 hit
    expect(
        "doppietta parziale",
        count_scorer_hits([_s(A, "Messi"), _s(A, "Messi")], [_s(A, "Messi")]),
        1,
    )

    failed = [c for c in checks if not c[1]]
    for label, ok, got, want in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {label}  got={got} want={want}")
    print(f"\n{len(checks) - len(failed)}/{len(checks)} passati")
    return len(failed) == 0


if __name__ == "__main__":
    import sys
    sys.exit(0 if run() else 1)
