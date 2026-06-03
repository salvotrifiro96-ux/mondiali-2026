"""Scraping autonomo dei risultati reali (punteggio + marcatori) da Wikipedia.

Sorgente: pagine "2026 FIFA World Cup Group A".."Group L" — ogni footballbox
contiene punteggio e marcatori una volta che la partita è stata giocata.

Strategia:
  - per ogni footballbox "giocato" (punteggio numerico) estrae casa/trasferta,
    gol e marcatori per lato;
  - matcha la coppia (casa, trasferta) con le nostre fixture per ricavare match_id
    (fase a gironi: identificazione univoca);
  - mappa i nomi dei marcatori sulle rose (squads.json) per far funzionare lo scoring;
  - fa upsert nella tabella results (idempotente).
"""

from __future__ import annotations

import html as _html
import re
import unicodedata
from datetime import datetime, timezone

import requests

from . import data, db

GROUP_URL = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_Group_{g}"
_HEADERS = {"User-Agent": "mondiali2026-fantamondiale/1.0 (personal project)"}
_TABLE_RE = re.compile(r'<table class="fevent">.*?</table>', re.S)
_FHOME_RE = re.compile(r'<th class="fhome".*?<a [^>]*>([^<]+)</a>', re.S)
_FAWAY_RE = re.compile(r'<th class="faway".*?<a [^>]*>([^<]+)</a>', re.S)
_FSCORE_RE = re.compile(r'<th class="fscore">(.*?)</th>', re.S)
_SCORE_NUMS_RE = re.compile(r"(\d+)\s*[–\-:]\s*(\d+)")
_HGOAL_RE = re.compile(r'<td class="fhgoal">(.*?)</td>', re.S)
_AGOAL_RE = re.compile(r'<td class="fagoal">(.*?)</td>', re.S)
_LI_RE = re.compile(r"<li>(.*?)</li>", re.S)
_NAME_TITLE_RE = re.compile(r'<a [^>]*title="([^"]+)"')
_TAG_RE = re.compile(r"<[^>]+>")
_MINUTE_RE = re.compile(r"\d{1,3}(?:&#43;\d+|\+\d+)?(?:&#39;|&#8242;|′|')")
_OWNGOAL_RE = re.compile(r"o\.?\s?g\.?", re.I)


def _clean(text: str) -> str:
    return _html.unescape(_TAG_RE.sub("", text)).strip()


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\([^)]*\)", "", s)  # rimuove disambiguazioni "(footballer)"
    return re.sub(r"\s+", " ", s).strip().lower()


def _build_squad_index(team: str) -> dict[str, str]:
    """norm(nome completo) -> nome ufficiale; più indice per cognome univoco."""
    players = data.squad_for(team)
    full = {}
    by_surname: dict[str, list[str]] = {}
    for p in players:
        name = p["name"]
        full[_norm(name)] = name
        surname = _norm(name).split(" ")[-1]
        by_surname.setdefault(surname, []).append(name)
    # cognomi univoci
    surname_idx = {s: names[0] for s, names in by_surname.items() if len(names) == 1}
    return {"full": full, "surname": surname_idx}


def _parse_li(li_html: str) -> tuple[str | None, int]:
    """Ritorna (nome_marcatore, numero_gol) da un <li>. None se autogol/ignoto."""
    if _OWNGOAL_RE.search(li_html):
        return None, 0
    m = _NAME_TITLE_RE.search(li_html)
    if m:
        name = m.group(1)
    else:
        name = _clean(li_html.split("<span", 1)[0])
    name = re.sub(r"\([^)]*\)", "", name).strip()
    if not name:
        return None, 0
    goals = len(_MINUTE_RE.findall(li_html)) or 1
    return name, goals


def _map_scorers(team: str, raw: list[tuple[str, int]]) -> tuple[list[dict], list[str]]:
    idx = _build_squad_index(team)
    scorers: list[dict] = []
    unmatched: list[str] = []
    for name, goals in raw:
        key = _norm(name)
        official = idx["full"].get(key) or idx["surname"].get(key.split(" ")[-1])
        if official:
            scorers.extend({"team": team, "name": official} for _ in range(goals))
        else:
            unmatched.append(name)
    return scorers, unmatched


def _parse_box(table_html: str) -> dict | None:
    home_m = _FHOME_RE.search(table_html)
    away_m = _FAWAY_RE.search(table_html)
    score_m = _FSCORE_RE.search(table_html)
    if not (home_m and away_m and score_m):
        return None
    nums = _SCORE_NUMS_RE.search(_clean(score_m.group(1)))
    if not nums:
        return None  # non ancora giocata (es. "Match 1")
    home = _clean(home_m.group(1))
    away = _clean(away_m.group(1))
    hg, ag = int(nums.group(1)), int(nums.group(2))

    def _scorers_from(td_re):
        td = td_re.search(table_html)
        out = []
        if td:
            for li in _LI_RE.findall(td.group(1)):
                n, g = _parse_li(li)
                if n:
                    out.append((n, g))
        return out

    return {
        "home": home,
        "away": away,
        "home_goals": hg,
        "away_goals": ag,
        "home_scorers_raw": _scorers_from(_HGOAL_RE),
        "away_scorers_raw": _scorers_from(_AGOAL_RE),
    }


def _fixture_lookup() -> dict[tuple[str, str], int]:
    return {(m["home"], m["away"]): m["id"] for m in data.matches()}


def fetch_played(groups: str = "ABCDEFGHIJKL") -> list[dict]:
    """Scarica e parsa le partite giocate dalle pagine dei gironi."""
    out = []
    for g in groups:
        url = GROUP_URL.format(g=g)
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=20)
            resp.raise_for_status()
        except requests.RequestException:
            continue
        for table in _TABLE_RE.findall(resp.text):
            box = _parse_box(table)
            if box:
                out.append(box)
    return out


def refresh_results(groups: str = "ABCDEFGHIJKL") -> dict:
    """Scarica i risultati giocati e aggiorna il DB. Ritorna un report."""
    lookup = _fixture_lookup()
    played = fetch_played(groups)
    updated, skipped, unmatched_scorers = [], [], []

    for box in played:
        mid = lookup.get((box["home"], box["away"])) or lookup.get((box["away"], box["home"]))
        if mid is None:
            skipped.append(f'{box["home"]} vs {box["away"]} (fixture non trovata)')
            continue
        hs, hu = _map_scorers(box["home"], box["home_scorers_raw"])
        as_, au = _map_scorers(box["away"], box["away_scorers_raw"])
        unmatched_scorers.extend(hu + au)
        db.save_result(mid, box["home_goals"], box["away_goals"], hs + as_)
        updated.append(mid)

    report = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "played_found": len(played),
        "updated": sorted(updated),
        "skipped": skipped,
        "unmatched_scorers": sorted(set(unmatched_scorers)),
    }
    db.set_meta("last_scrape", report["ts"])
    db.set_meta("last_scrape_count", str(len(updated)))
    return report


if __name__ == "__main__":
    import json
    db.init_db()
    print(json.dumps(refresh_results(), indent=2, ensure_ascii=False))
