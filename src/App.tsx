import { useMemo, useState } from "react";
import { MATCHES, PARTICIPANTS, GROUPS, DATA_UPDATED, STAGE_LABEL } from "./lib/data";
import { loadCurrentUser, saveCurrentUser, useStore, getPrediction } from "./lib/store";
import type { Stage } from "./lib/types";
import MatchCard from "./components/MatchCard";
import ResultCard from "./components/ResultCard";
import Leaderboard from "./components/Leaderboard";

type Tab = "predict" | "standings" | "results";

const STAGES: Stage[] = [
  "group",
  "round_of_32",
  "round_of_16",
  "quarter_final",
  "semi_final",
  "third_place",
  "final",
];

export default function App() {
  const [tab, setTab] = useState<Tab>("predict");
  const [user, setUser] = useState<string>(loadCurrentUser());
  const [stage, setStage] = useState<Stage>("group");
  const [group, setGroup] = useState<string>("all");
  const [query, setQuery] = useState("");
  const s = useStore();

  const pickUser = (id: string) => {
    setUser(id);
    saveCurrentUser(id);
  };

  const matches = useMemo(() => {
    return MATCHES.filter((m) => m.stage === stage)
      .filter((m) => stage !== "group" || group === "all" || m.group === group)
      .filter(
        (m) =>
          !query ||
          m.home.toLowerCase().includes(query.toLowerCase()) ||
          m.away.toLowerCase().includes(query.toLowerCase()),
      );
  }, [stage, group, query]);

  const predCount = user ? MATCHES.filter((m) => getPrediction(s, m.id, user)).length : 0;

  return (
    <div className="mx-auto max-w-5xl px-4 pb-20 pt-6 sm:pt-10">
      <header className="mb-6">
        <div className="flex items-center justify-between gap-4">
          <div>
            <div className="mb-1 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.2em] text-wc-muted">
              <span>🇨🇦 🇲🇽 🇺🇸</span> Canada · Mexico · USA
            </div>
            <h1 className="font-display text-4xl font-bold leading-none sm:text-5xl">
              <span className="gradient-text">MONDIALE 2026</span>
            </h1>
            <p className="mt-1 text-sm text-wc-muted">
              Pronostici tra amici · 1X2 · Risultato esatto · Marcatori
            </p>
          </div>
          <div className="hidden text-6xl animate-floaty sm:block">⚽</div>
        </div>
      </header>

      <div className="glass mb-5 p-4">
        <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-wc-muted">Chi sei?</div>
        <div className="flex flex-wrap gap-2">
          {PARTICIPANTS.map((p) => (
            <button
              key={p.id}
              onClick={() => pickUser(p.id)}
              className={`btn text-sm ${user === p.id ? "btn-grad" : "btn-ghost"}`}
            >
              {p.name}
            </button>
          ))}
          {user && (
            <span className="ml-auto self-center text-xs text-wc-muted">
              {predCount}/{MATCHES.length} pronostici
            </span>
          )}
        </div>
      </div>

      <div className="mb-5 flex gap-1 rounded-2xl bg-black/30 p-1">
        {(
          [
            ["predict", "🎯 Pronostici"],
            ["standings", "🏆 Classifica"],
            ["results", "📝 Risultati"],
          ] as [Tab, string][]
        ).map(([t, label]) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`flex-1 rounded-xl px-3 py-2.5 text-sm font-semibold transition ${
              tab === t ? "bg-wc-grad text-white shadow-glow" : "text-wc-muted hover:text-wc-ink"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === "standings" && <Leaderboard currentUser={user} />}

      {(tab === "predict" || tab === "results") && (
        <>
          {tab === "predict" && !user && (
            <div className="glass mb-4 p-4 text-center text-sm text-wc-pink">
              Seleziona il tuo nome qui sopra per inserire i pronostici.
            </div>
          )}

          <div className="mb-4 space-y-3">
            <div className="flex flex-wrap gap-1.5">
              {STAGES.map((st) => (
                <button
                  key={st}
                  onClick={() => setStage(st)}
                  className={`chip border ${
                    stage === st
                      ? "bg-wc-grad text-white border-transparent"
                      : "bg-white/5 border-white/10 text-wc-muted hover:text-wc-ink"
                  }`}
                >
                  {STAGE_LABEL[st]}
                </button>
              ))}
            </div>

            {stage === "group" && (
              <div className="flex flex-wrap gap-1.5">
                <GroupChip active={group === "all"} onClick={() => setGroup("all")} label="Tutti" />
                {Object.keys(GROUPS).map((g) => (
                  <GroupChip key={g} active={group === g} onClick={() => setGroup(g)} label={g} />
                ))}
              </div>
            )}

            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Cerca squadra…"
              className="w-full rounded-xl bg-black/30 border border-white/10 px-3 py-2 text-sm outline-none focus:border-wc-cyan/60 placeholder:text-wc-muted"
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            {matches.map((m) =>
              tab === "predict" ? (
                <MatchCard key={m.id} match={m} userId={user || "salvo"} />
              ) : (
                <ResultCard key={m.id} match={m} />
              ),
            )}
          </div>
          {matches.length === 0 && (
            <div className="glass p-8 text-center text-wc-muted">Nessuna partita per questi filtri.</div>
          )}
        </>
      )}

      <footer className="mt-10 text-center text-xs text-wc-muted">
        Dati: {DATA_UPDATED} · fonte Wikipedia · {MATCHES.length} partite · {PARTICIPANTS.length} giocatori
      </footer>
    </div>
  );
}

function GroupChip({ active, onClick, label }: { active: boolean; onClick: () => void; label: string }) {
  return (
    <button
      onClick={onClick}
      className={`chip border ${
        active ? "bg-white/15 border-white/20 text-wc-ink" : "bg-white/5 border-white/10 text-wc-muted"
      }`}
    >
      {label}
    </button>
  );
}
