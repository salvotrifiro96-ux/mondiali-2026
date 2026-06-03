"""MONDIALE 2026 — Fantamondiale condiviso (Streamlit + SQLite)."""

from __future__ import annotations

import streamlit as st

from datetime import datetime, timezone

from core import data, db, scraper
from core.scoring import compute_score, outcome
from core.standings import compute_standings

st.set_page_config(page_title="MONDIALE 2026", page_icon="🏆", layout="wide")
db.init_db()

_AUTO_REFRESH_SECONDS = 1800  # 30 min


def _scrape_is_stale() -> bool:
    last = db.get_meta("last_scrape")
    if not last:
        return True
    try:
        dt = datetime.fromisoformat(last)
    except ValueError:
        return True
    return (datetime.now(timezone.utc) - dt).total_seconds() > _AUTO_REFRESH_SECONDS


def _maybe_auto_refresh():
    """Aggiorna i risultati in autonomia, max una volta per sessione e se 'stale'."""
    if st.session_state.get("_scrape_checked") or not _scrape_is_stale():
        return
    st.session_state["_scrape_checked"] = True
    try:
        with st.spinner("Aggiorno i risultati dal vivo…"):
            scraper.refresh_results()
    except Exception:  # rete assente / Wikipedia non raggiungibile: non bloccare l'app
        pass


_maybe_auto_refresh()

# ---------------------------------------------------------------- stile
st.markdown(
    """
    <style>
      .stApp {
        background-color: #0a0823;
        color: #e8e6ff;
        background-image:
          radial-gradient(1200px 600px at 10% -10%, rgba(255,45,142,.22), transparent 60%),
          radial-gradient(1000px 500px at 100% 0%, rgba(25,224,255,.18), transparent 55%),
          radial-gradient(900px 700px at 50% 120%, rgba(123,44,255,.22), transparent 60%);
        background-attachment: fixed;
      }
      .wc-title {
        font-size: 2.8rem; font-weight: 800; letter-spacing: -1px; line-height: 1;
        background: linear-gradient(120deg,#ff2d8e 0%,#7b2cff 45%,#19e0ff 100%);
        -webkit-background-clip: text; background-clip: text; color: transparent;
        margin: 0;
      }
      .wc-sub { color: #9a93c7; font-size: .95rem; margin-top: .25rem; }
      /* container nativi bordati -> stile glass */
      div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(26,19,64,.55); backdrop-filter: blur(14px);
        border: 1px solid rgba(255,255,255,.10) !important; border-radius: 22px;
        padding: 6px 18px 12px; margin-bottom: 8px;
      }
      .wc-card {
        background: rgba(26,19,64,.6); backdrop-filter: blur(14px);
        border: 1px solid rgba(255,255,255,.10); border-radius: 22px;
        padding: 16px 18px; margin-bottom: 14px;
      }
      .wc-match-teams { font-size: 1.15rem; font-weight: 700; }
      .wc-meta { color:#9a93c7; font-size:.82rem; }
      .wc-badge {
        display:inline-block; padding:2px 10px; border-radius:999px;
        font-size:.78rem; font-weight:700; border:1px solid rgba(255,255,255,.12);
      }
      .wc-badge-1 { background:rgba(67,245,155,.15); color:#43f59b; }
      .wc-badge-X { background:rgba(255,210,63,.15); color:#ffd23f; }
      .wc-badge-2 { background:rgba(47,107,255,.18); color:#7fa6ff; }
      .wc-pts { background:linear-gradient(120deg,#ff2d8e,#7b2cff); color:#fff;
        padding:3px 12px; border-radius:999px; font-weight:800; }
      .wc-pts-void { background:rgba(255,255,255,.08); color:#9a93c7;
        padding:3px 12px; border-radius:999px; font-weight:700; }
      .wc-rank { font-size:1.5rem; font-weight:800; }
      .stTabs [data-baseweb="tab-list"] { gap: 6px; }
      .stTabs [data-baseweb="tab"] { background: rgba(255,255,255,.05);
        border-radius: 14px; padding: 6px 16px; }
      .stTabs [aria-selected="true"] {
        background: linear-gradient(120deg,#ff2d8e,#7b2cff) !important; color:#fff !important; }

      /* PULSANTI: erano testo chiaro su sfondo bianco (invisibili) */
      div[data-testid="stButton"] > button,
      div[data-testid="stFormSubmitButton"] > button {
        border-radius: 14px; font-weight: 700;
        background: rgba(255,255,255,.07); color: #e8e6ff;
        border: 1px solid rgba(255,255,255,.16);
        transition: all .15s ease;
      }
      div[data-testid="stButton"] > button:hover,
      div[data-testid="stFormSubmitButton"] > button:hover {
        background: rgba(255,255,255,.16); color: #fff;
        border-color: rgba(255,255,255,.32);
      }
      button[data-testid="stBaseButton-secondary"] {
        background: rgba(255,255,255,.07) !important; color: #e8e6ff !important;
        border: 1px solid rgba(255,255,255,.16) !important;
      }
      button[data-testid="stBaseButton-secondary"]:hover {
        background: rgba(255,255,255,.16) !important; color: #fff !important;
      }
      div[data-testid="stButton"] > button p,
      div[data-testid="stFormSubmitButton"] > button p { color: inherit !important; }
      /* azioni primarie -> gradiente mondiale */
      button[data-testid="stBaseButton-primary"],
      button[kind="primary"] {
        background: linear-gradient(120deg,#ff2d8e,#7b2cff) !important;
        color: #fff !important; border: none !important;
        box-shadow: 0 10px 30px -12px rgba(255,45,142,.6);
      }
      button[data-testid="stBaseButton-primary"]:hover,
      button[kind="primary"]:hover { filter: brightness(1.08); color:#fff !important; }
      /* input numerici e select leggibili sul tema scuro */
      div[data-testid="stNumberInput"] input,
      div[data-baseweb="select"] > div {
        background: #120c30 !important; color: #e8e6ff !important;
        border-radius: 12px !important;
      }
      div[data-testid="stNumberInput"] button { background:#1a1340 !important; color:#e8e6ff !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

HOSTS = "🇲🇽 🇨🇦 🇺🇸"
ALL_MATCHES = data.matches()


# ---------------------------------------------------------------- helper UI
def _outcome_badge(home: int, away: int) -> str:
    o = outcome(home, away)
    label = {"1": "1 · Casa", "X": "X · Pari", "2": "2 · Trasferta"}[o]
    return f'<span class="wc-badge wc-badge-{o}">{label}</span>'


def _seed(key: str, value):
    if key not in st.session_state:
        st.session_state[key] = value


def _scorer_inputs(match: dict, prefix: str, home_goals: int, away_goals: int, saved: list[dict]):
    """Renderizza N selectbox per squadra (N = gol previsti). Ritorna lista scorers."""
    pool = {p["team"]: p["players"] for p in data.scorer_pool(match)}
    scorers: list[dict] = []
    if not pool:
        st.caption("Rose disponibili dopo il sorteggio della fase finale.")
        return scorers

    # pre-distribuzione dei marcatori salvati per squadra (in coda)
    saved_by_team: dict[str, list[str]] = {}
    for s in saved:
        saved_by_team.setdefault(s["team"], []).append(s["name"])

    for team, goals in ((match["home"], home_goals), (match["away"], away_goals)):
        players = pool.get(team, [])
        if not players or goals <= 0:
            continue
        names = [p["name"] for p in players]
        goals_by_name = {p["name"]: p.get("goals", 0) for p in players}
        club_by_name = {p["name"]: p.get("club", "") for p in players}

        def _fmt(n: str, _g=goals_by_name, _c=club_by_name) -> str:
            if n == "—":
                return "—"
            g = _g.get(n, 0)
            extra = f"  ⚽{g}" if g else ""
            club = f"  · {_c[n]}" if _c.get(n) else ""
            return f"{n}{extra}{club}"

        st.markdown(f"**{data.flag(team)} {team}** — marcatori")
        seeded = saved_by_team.get(team, [])
        cols = st.columns(min(goals, 3)) if goals > 1 else [st]
        for i in range(goals):
            default = seeded[i] if i < len(seeded) else "—"
            k = f"{prefix}_{team}_s{i}"
            _seed(k, default if default in names else "—")
            target = cols[i % len(cols)]
            choice = target.selectbox(
                f"Gol {i + 1}",
                options=["—"] + names,
                format_func=_fmt,
                key=k,
            )
            if choice and choice != "—":
                scorers.append({"team": team, "name": choice})
    return scorers


def _points_badge(pred: dict, result: dict) -> str:
    b = compute_score(pred, result)
    if b.total > 0:
        bits = [f"+{b.points_outcome} 1X2"]
        if b.points_scorers:
            bits.append(f"+{b.points_scorers} marc.")
        if b.points_exact_bonus:
            bits.append(f"+{b.points_exact_bonus} esatto")
        return f'<span class="wc-pts">{b.total} pt</span> <span class="wc-meta">{" · ".join(bits)}</span>'
    if b.voided:
        return '<span class="wc-pts-void">0 pt · marcatori annullati (1X2 errato)</span>'
    return '<span class="wc-pts-void">0 pt</span>'


def _match_header(match: dict):
    home, away = match["home"], match["away"]
    st.markdown(
        f'<div class="wc-match-teams">{data.flag(home)} {home} '
        f'<span class="wc-meta">vs</span> {away} {data.flag(away)}</div>',
        unsafe_allow_html=True,
    )
    meta = f'{data.format_date(match["date"])} · {data.format_kickoff(match["kickoff"])} · {match["venue"]}'
    tag = data.STAGE_SHORT[match["stage"]] + (f" · Girone {match['group']}" if match.get("group") else "")
    st.markdown(f'<div class="wc-meta">{tag} — {meta}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------- filtri
def _filter_matches() -> list[dict]:
    st.sidebar.markdown("### Filtri")
    stage_opts = ["Tutte"] + [data.STAGE_LABEL[s] for s in data.STAGE_ORDER
                              if any(m["stage"] == s for m in ALL_MATCHES)]
    stage_sel = st.sidebar.selectbox("Fase", stage_opts, index=1, key="flt_stage")

    group_sel = "Tutti"
    if stage_sel == data.STAGE_LABEL["group"]:
        group_sel = st.sidebar.selectbox(
            "Girone", ["Tutti"] + sorted(data.groups().keys()), key="flt_group"
        )

    query = st.sidebar.text_input("Cerca squadra", key="flt_query").strip().lower()

    label_to_stage = {v: k for k, v in data.STAGE_LABEL.items()}
    out = []
    for m in ALL_MATCHES:
        if stage_sel != "Tutte" and m["stage"] != label_to_stage[stage_sel]:
            continue
        if group_sel != "Tutti" and m.get("group") != group_sel:
            continue
        if query and query not in m["home"].lower() and query not in m["away"].lower():
            continue
        out.append(m)
    return out


# ---------------------------------------------------------------- viste
def view_pronostici(user_id: str, matches: list[dict]):
    st.caption(f"{len(matches)} partite — i pronostici si salvano col pulsante **Salva**.")
    results = db.all_results()

    for m in matches:
        with st.container(border=True):
            _match_header(m)
            saved = db.get_prediction(user_id, m["id"]) or {"home": 0, "away": 0, "scorers": []}
            prefix = f"pred_{user_id}_{m['id']}"

            c1, c2, c3 = st.columns([1, 1, 2])
            _seed(f"{prefix}_h", int(saved["home"]))
            _seed(f"{prefix}_a", int(saved["away"]))
            hg = c1.number_input(f"{data.flag(m['home'])} {m['home']}", min_value=0, max_value=20,
                                 step=1, key=f"{prefix}_h")
            ag = c2.number_input(f"{data.flag(m['away'])} {m['away']}", min_value=0, max_value=20,
                                 step=1, key=f"{prefix}_a")
            c3.markdown("&nbsp;", unsafe_allow_html=True)
            c3.markdown(_outcome_badge(hg, ag), unsafe_allow_html=True)

            scorers = _scorer_inputs(m, prefix, hg, ag, saved["scorers"])

            b1, b2, _ = st.columns([1, 1, 4])
            if b1.button("💾 Salva", key=f"{prefix}_save", type="primary"):
                db.save_prediction(user_id, m["id"], hg, ag, scorers)
                st.toast("Pronostico salvato!", icon="✅")
            if b2.button("🗑️", key=f"{prefix}_del", help="Cancella pronostico"):
                db.delete_prediction(user_id, m["id"])
                for kk in list(st.session_state.keys()):
                    if kk.startswith(prefix):
                        del st.session_state[kk]
                st.rerun()

            res = results.get(m["id"])
            if res:
                pred = {"home": hg, "away": ag, "scorers": scorers}
                st.markdown(
                    f'<div class="wc-meta">Risultato reale: {res["home"]}-{res["away"]}</div>'
                    + _points_badge(pred, res),
                    unsafe_allow_html=True,
                )


def view_classifica():
    rows = compute_standings()
    medals = ["🥇", "🥈", "🥉"]
    cols = st.columns(min(3, len(rows)))
    for i in range(min(3, len(rows))):
        r = rows[i]
        with cols[i]:
            st.markdown(
                f'<div class="wc-card" style="text-align:center">'
                f'<div class="wc-rank">{medals[i]} {r["name"]}</div>'
                f'<div class="wc-pts" style="font-size:1.4rem">{r["points"]} pt</div>'
                f'<div class="wc-meta" style="margin-top:8px">'
                f'{r["played"]} giocate · {r["exact"]} esatti · {r["scorer_hits"]} marcatori</div>'
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("#### Classifica completa")
    table = [
        {
            "#": i + 1,
            "Giocatore": r["name"],
            "Punti": r["points"],
            "Giocate": r["played"],
            "1X2": r["outcomes"],
            "Esatti": r["exact"],
            "Marcatori": r["scorer_hits"],
            "Perfetti": r["perfect"],
        }
        for i, r in enumerate(rows)
    ]
    st.dataframe(table, hide_index=True, use_container_width=True)
    n_res = len(db.all_results())
    st.caption(f"{n_res} risultati inseriti su {len(ALL_MATCHES)} partite.")


def view_risultati(matches: list[dict]):
    last = db.get_meta("last_scrape")
    count = db.get_meta("last_scrape_count") or "0"
    c1, c2 = st.columns([1, 2])
    if c1.button("🔄 Aggiorna risultati ora", type="primary", key="scrape_now"):
        with st.spinner("Scarico i risultati da Wikipedia…"):
            rep = scraper.refresh_results()
        st.session_state["_scrape_checked"] = True
        st.success(
            f"Trovate {rep['played_found']} partite giocate · "
            f"{len(rep['updated'])} risultati aggiornati."
        )
        if rep["unmatched_scorers"]:
            st.caption("Marcatori non riconosciuti: " + ", ".join(rep["unmatched_scorers"]))
        st.rerun()
    when = "mai" if not last else last.replace("T", " ")
    c2.caption(
        f"I risultati si aggiornano **da soli** (scraping Wikipedia, ogni ~30 min). "
        f"Ultimo aggiornamento: **{when}** · {count} risultati. "
        "Sotto puoi correggere a mano se serve."
    )
    st.divider()
    for m in matches:
        with st.container(border=True):
            _match_header(m)
            saved = db.get_result(m["id"]) or {"home": 0, "away": 0, "scorers": []}
            prefix = f"res_{m['id']}"

            c1, c2, c3 = st.columns([1, 1, 2])
            _seed(f"{prefix}_h", int(saved["home"]))
            _seed(f"{prefix}_a", int(saved["away"]))
            hg = c1.number_input(f"{data.flag(m['home'])} {m['home']}", min_value=0, max_value=20,
                                 step=1, key=f"{prefix}_h")
            ag = c2.number_input(f"{data.flag(m['away'])} {m['away']}", min_value=0, max_value=20,
                                 step=1, key=f"{prefix}_a")
            c3.markdown("&nbsp;", unsafe_allow_html=True)
            c3.markdown(_outcome_badge(hg, ag), unsafe_allow_html=True)

            scorers = _scorer_inputs(m, prefix, hg, ag, saved["scorers"])

            b1, b2, _ = st.columns([1, 1, 4])
            if b1.button("✅ Salva risultato", key=f"{prefix}_save", type="primary"):
                db.save_result(m["id"], hg, ag, scorers)
                st.toast("Risultato salvato!", icon="🎯")
            if b2.button("🗑️", key=f"{prefix}_del", help="Cancella risultato"):
                db.delete_result(m["id"])
                for kk in list(st.session_state.keys()):
                    if kk.startswith(prefix):
                        del st.session_state[kk]
                st.rerun()


# ---------------------------------------------------------------- header + sidebar
st.markdown(
    f'<p class="wc-title">MONDIALE 2026 {HOSTS}</p>'
    f'<p class="wc-sub">Fantamondiale tra amici · {len(ALL_MATCHES)} partite ufficiali · '
    f"dati aggiornati {data.format_date(data.data_updated()[:10] if data.data_updated() else None)}</p>",
    unsafe_allow_html=True,
)

st.sidebar.markdown("## 👤 Chi sei?")
names = [p["name"] for p in data.PARTICIPANTS]
sel_name = st.sidebar.selectbox("Giocatore", names, key="current_user_name")
user_id = next(p["id"] for p in data.PARTICIPANTS if p["name"] == sel_name)
st.sidebar.success(f"Stai giocando come **{sel_name}**")

with st.sidebar.expander("📏 Regole punteggio"):
    st.markdown(
        "- **1X2** azzeccato: **+2**\n"
        "- ogni **marcatore** giusto: **+1**\n"
        "- **risultato esatto**: **+5**\n"
        "- **risultato esatto + marcatori**: **+10** (cumulativo)\n"
        "- ⚠️ se sbagli l'**1X2**, **tutto a 0** (marcatori inclusi)"
    )

filtered = _filter_matches()

tab_pred, tab_rank, tab_res = st.tabs(["⚽ Pronostici", "🏆 Classifica", "🎯 Risultati"])
with tab_pred:
    view_pronostici(user_id, filtered)
with tab_rank:
    view_classifica()
with tab_res:
    view_risultati(filtered)
