"""Caricamento dati (fixture + rose) e helper di formattazione."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

def _resolve_data_dir() -> Path:
    here = Path(__file__).resolve()
    candidates = [
        here.parents[1] / "data",          # streamlit_app/data (self-contained / deploy)
        here.parents[2] / "src" / "data",  # progetto React (sviluppo locale)
    ]
    for c in candidates:
        if (c / "fixtures.json").exists():
            return c
    return candidates[0]


_DATA = _resolve_data_dir()

PARTICIPANTS = [
    {"id": "salvo", "name": "Salvo"},
    {"id": "diego", "name": "Diego"},
    {"id": "andrea", "name": "Andrea"},
    {"id": "giovanni", "name": "Giovanni"},
    {"id": "carmelo", "name": "Carmelo"},
    {"id": "francesco", "name": "Francesco"},
]

STAGE_LABEL = {
    "group": "Fase a gironi",
    "round_of_32": "Sedicesimi",
    "round_of_16": "Ottavi",
    "quarter_final": "Quarti",
    "semi_final": "Semifinali",
    "third_place": "Finale 3º posto",
    "final": "Finale",
}

STAGE_SHORT = {
    "group": "Gironi",
    "round_of_32": "16esimi",
    "round_of_16": "Ottavi",
    "quarter_final": "Quarti",
    "semi_final": "Semi",
    "third_place": "3º posto",
    "final": "Finale",
}

STAGE_ORDER = list(STAGE_LABEL.keys())

_MONTHS_IT = [
    "gen", "feb", "mar", "apr", "mag", "giu",
    "lug", "ago", "set", "ott", "nov", "dic",
]

_ISO2 = {
    "Czech Republic": "CZ", "Mexico": "MX", "South Africa": "ZA", "South Korea": "KR",
    "Bosnia and Herzegovina": "BA", "Canada": "CA", "Qatar": "QA", "Switzerland": "CH",
    "Brazil": "BR", "Haiti": "HT", "Morocco": "MA", "Australia": "AU", "Paraguay": "PY",
    "Turkey": "TR", "United States": "US", "Curaçao": "CW", "Ecuador": "EC",
    "Germany": "DE", "Ivory Coast": "CI", "Japan": "JP", "Netherlands": "NL",
    "Sweden": "SE", "Tunisia": "TN", "Belgium": "BE", "Egypt": "EG", "Iran": "IR",
    "New Zealand": "NZ", "Cape Verde": "CV", "Saudi Arabia": "SA", "Spain": "ES",
    "Uruguay": "UY", "France": "FR", "Iraq": "IQ", "Norway": "NO", "Senegal": "SN",
    "Algeria": "DZ", "Argentina": "AR", "Austria": "AT", "Jordan": "JO",
    "Colombia": "CO", "DR Congo": "CD", "Portugal": "PT", "Uzbekistan": "UZ",
    "Croatia": "HR", "Ghana": "GH", "Panama": "PA",
}

_SPECIAL = {
    "England": "🏴\U000e0067\U000e0062\U000e0065\U000e006e\U000e0067\U000e007f",
    "Scotland": "🏴\U000e0067\U000e0062\U000e0073\U000e0063\U000e0074\U000e007f",
    "Wales": "🏴\U000e0067\U000e0062\U000e0077\U000e006c\U000e0073\U000e007f",
}


def _iso2_to_emoji(code: str) -> str:
    return "".join(chr(127397 + ord(c)) for c in code.upper())


def flag(team: str) -> str:
    if team in _SPECIAL:
        return _SPECIAL[team]
    code = _ISO2.get(team)
    return _iso2_to_emoji(code) if code else "⚽️"


@lru_cache(maxsize=1)
def _fixtures() -> dict:
    return json.loads((_DATA / "fixtures.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _squads() -> dict:
    return json.loads((_DATA / "squads.json").read_text(encoding="utf-8"))


def groups() -> dict:
    return _fixtures()["groups"]


def matches() -> list[dict]:
    return sorted(_fixtures()["matches"], key=lambda m: m["id"])


def squads() -> dict:
    return _squads()["squads"]


def data_updated() -> str:
    return _fixtures().get("lastUpdated", "")


def squad_for(team: str) -> list[dict]:
    return squads().get(team, [])


def scorer_pool(match: dict) -> list[dict]:
    """[{team, players:[...]}] per entrambe le squadre, se rose note."""
    out = []
    for team in (match["home"], match["away"]):
        players = squad_for(team)
        if players:
            out.append({"team": team, "players": players})
    return out


def is_playable(match: dict) -> bool:
    return len(squad_for(match["home"])) > 0 and len(squad_for(match["away"])) > 0


def format_date(iso: str | None) -> str:
    if not iso:
        return "—"
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{d} {_MONTHS_IT[m - 1]} {y}"


def format_kickoff(k: str) -> str:
    m = re.search(r"(\d{1,2}):(\d{2})\s*([ap])\.?m\.?\s*(UTC[−+]?\d+)?", k, re.I)
    if not m:
        return k
    h = int(m.group(1))
    mn = m.group(2)
    pm = m.group(3).lower() == "p"
    if pm and h != 12:
        h += 12
    if not pm and h == 12:
        h = 0
    tz = f" ({m.group(4)})" if m.group(4) else ""
    return f"{h:02d}:{mn}{tz}"


def participant_name(uid: str) -> str:
    for p in PARTICIPANTS:
        if p["id"] == uid:
            return p["name"]
    return uid
