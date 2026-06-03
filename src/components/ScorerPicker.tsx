import { useMemo, useState } from "react";
import type { Match, ScorerRef, Player } from "../lib/types";
import { scorerPool } from "../lib/data";
import { flag } from "../lib/flags";

interface Props {
  match: Match;
  value: ScorerRef[];
  onChange: (next: ScorerRef[]) => void;
  disabled?: boolean;
}

const POS_COLOR: Record<string, string> = {
  GK: "bg-wc-muted/30 text-wc-muted",
  DF: "bg-wc-blue/25 text-wc-cyan",
  MF: "bg-wc-lime/20 text-wc-lime",
  FW: "bg-wc-magenta/25 text-wc-pink",
};

export default function ScorerPicker({ match, value, onChange, disabled }: Props) {
  const pool = useMemo(() => scorerPool(match), [match]);
  const [q, setQ] = useState("");
  const [team, setTeam] = useState<string>("all");

  const counts = useMemo(() => {
    const m = new Map<string, number>();
    for (const s of value) m.set(`${s.team}|||${s.name}`, (m.get(`${s.team}|||${s.name}`) ?? 0) + 1);
    return m;
  }, [value]);

  const add = (t: string, p: Player) => {
    if (disabled) return;
    onChange([...value, { team: t, name: p.name }]);
  };
  const removeOne = (ref: ScorerRef) => {
    if (disabled) return;
    const i = value.findIndex((s) => s.team === ref.team && s.name === ref.name);
    if (i >= 0) {
      const next = value.slice();
      next.splice(i, 1);
      onChange(next);
    }
  };

  const filtered = pool
    .filter((g) => team === "all" || g.team === team)
    .map((g) => ({
      team: g.team,
      players: g.players
        .filter((p) => !q || p.name.toLowerCase().includes(q.toLowerCase()))
        .sort((a, b) => {
          const order = { FW: 0, MF: 1, DF: 2, GK: 3 } as Record<string, number>;
          if (order[a.position] !== order[b.position]) return order[a.position] - order[b.position];
          return b.goals - a.goals;
        }),
    }));

  return (
    <div className="space-y-3">
      {/* selezionati */}
      {value.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {[...counts.entries()].map(([key, n]) => {
            const [t, name] = key.split("|||");
            return (
              <button
                key={key}
                onClick={() => removeOne({ team: t, name })}
                disabled={disabled}
                className="chip bg-wc-grad text-white shadow-glow animate-pop group"
                title="Rimuovi un gol"
              >
                <span>{flag(t)}</span>
                <span className="max-w-[120px] truncate">{name}</span>
                {n > 1 && <span className="rounded-full bg-black/30 px-1.5">×{n}</span>}
                <span className="opacity-70 group-hover:opacity-100">✕</span>
              </button>
            );
          })}
        </div>
      )}

      {/* filtri */}
      <div className="flex gap-2">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Cerca marcatore…"
          disabled={disabled}
          className="flex-1 rounded-xl bg-black/30 border border-white/10 px-3 py-2 text-sm
            outline-none focus:border-wc-cyan/60 placeholder:text-wc-muted"
        />
        <div className="flex rounded-xl bg-black/30 border border-white/10 p-0.5 text-xs">
          {["all", match.home, match.away].map((t) => (
            <button
              key={t}
              onClick={() => setTeam(t)}
              disabled={disabled}
              className={`px-2.5 py-1.5 rounded-lg font-semibold transition ${
                team === t ? "bg-white/10 text-wc-ink" : "text-wc-muted hover:text-wc-ink"
              }`}
            >
              {t === "all" ? "Tutti" : flag(t)}
            </button>
          ))}
        </div>
      </div>

      {/* lista */}
      <div className="max-h-60 overflow-y-auto rounded-xl border border-white/10 bg-black/20 divide-y divide-white/5">
        {filtered.map((g) => (
          <div key={g.team}>
            <div className="sticky top-0 z-10 flex items-center gap-2 bg-wc-card/90 backdrop-blur px-3 py-1.5 text-xs font-bold uppercase tracking-wide text-wc-muted">
              <span>{flag(g.team)}</span> {g.team}
            </div>
            {g.players.map((p) => {
              const key = `${g.team}|||${p.name}`;
              const n = counts.get(key) ?? 0;
              return (
                <button
                  key={key}
                  onClick={() => add(g.team, p)}
                  disabled={disabled}
                  className={`flex w-full items-center gap-2 px-3 py-2 text-left text-sm transition hover:bg-white/5 ${
                    n > 0 ? "bg-wc-magenta/10" : ""
                  }`}
                >
                  <span className="w-6 text-center text-xs text-wc-muted">{p.number ?? "–"}</span>
                  <span className={`chip ${POS_COLOR[p.position] ?? "bg-white/10"} px-1.5 py-0.5`}>
                    {p.position}
                  </span>
                  <span className="flex-1 truncate">{p.name}</span>
                  {p.goals > 0 && (
                    <span className="text-xs text-wc-gold" title="Gol in nazionale">
                      ⚽{p.goals}
                    </span>
                  )}
                  <span className="text-xs text-wc-muted truncate max-w-[90px]">{p.club}</span>
                  {n > 0 && (
                    <span className="chip bg-wc-grad text-white">×{n}</span>
                  )}
                  <span className="text-wc-cyan font-bold">＋</span>
                </button>
              );
            })}
          </div>
        ))}
        {filtered.every((g) => g.players.length === 0) && (
          <div className="px-3 py-6 text-center text-sm text-wc-muted">Nessun giocatore trovato</div>
        )}
      </div>
    </div>
  );
}
