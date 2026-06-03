import type { Match, ScorerRef } from "../lib/types";
import { flag } from "../lib/flags";
import { formatDate, STAGE_SHORT } from "../lib/data";
import { store, useStore } from "../lib/store";
import ScorerPicker from "./ScorerPicker";

function Stepper({ value, onChange }: { value: number; onChange: (n: number) => void }) {
  return (
    <div className="flex items-center gap-2">
      <button
        className="h-8 w-8 rounded-lg bg-white/5 border border-white/10 text-lg leading-none hover:bg-white/10 disabled:opacity-30"
        onClick={() => onChange(Math.max(0, value - 1))}
        disabled={value <= 0}
      >
        −
      </button>
      <span className="w-7 text-center text-2xl font-display font-bold tabular-nums">{value}</span>
      <button
        className="h-8 w-8 rounded-lg bg-white/5 border border-white/10 text-lg leading-none hover:bg-white/10"
        onClick={() => onChange(Math.min(15, value + 1))}
      >
        +
      </button>
    </div>
  );
}

export default function ResultCard({ match }: { match: Match }) {
  const s = useStore();
  const result = s.results[match.id];
  const entered = !!result;

  const update = (patch: Partial<{ home: number; away: number; scorers: ScorerRef[] }>) => {
    store.setResult({
      matchId: match.id,
      home: result?.home ?? 0,
      away: result?.away ?? 0,
      scorers: result?.scorers ?? [],
      ...patch,
    });
  };

  return (
    <div
      className={`glass p-4 sm:p-5 ${entered ? "border-wc-lime/40" : ""}`}
    >
      <div className="mb-3 flex items-center justify-between text-xs text-wc-muted">
        <span className="chip bg-white/5 border border-white/10">
          {match.group ? `Girone ${match.group}` : STAGE_SHORT[match.stage]} · #{match.id}
        </span>
        <span>{formatDate(match.date)}</span>
      </div>

      <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-2">
        <div className="flex flex-col items-center gap-1 text-center">
          <span className="text-3xl">{flag(match.home)}</span>
          <span className="text-sm font-semibold">{match.home}</span>
        </div>
        <div className="flex items-center gap-3">
          <Stepper value={result?.home ?? 0} onChange={(n) => update({ home: n })} />
          <span className="text-wc-muted">:</span>
          <Stepper value={result?.away ?? 0} onChange={(n) => update({ away: n })} />
        </div>
        <div className="flex flex-col items-center gap-1 text-center">
          <span className="text-3xl">{flag(match.away)}</span>
          <span className="text-sm font-semibold">{match.away}</span>
        </div>
      </div>

      <div className="mt-4">
        <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-wc-muted">
          Marcatori ufficiali
        </div>
        <ScorerPicker
          match={match}
          value={result?.scorers ?? []}
          onChange={(scorers) => update({ scorers })}
        />
      </div>

      <div className="mt-4 flex items-center justify-between">
        <span className={`chip ${entered ? "bg-wc-lime/20 text-wc-lime" : "bg-white/5 text-wc-muted"}`}>
          {entered ? "● Partita conteggiata" : "○ non inserita"}
        </span>
        {entered && (
          <button className="btn-ghost text-sm text-wc-pink" onClick={() => store.removeResult(match.id)}>
            🗑 Azzera
          </button>
        )}
      </div>
    </div>
  );
}
