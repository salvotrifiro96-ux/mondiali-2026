import { useState } from "react";
import ScorerPicker from "./ScorerPicker";
import type { Match, ScorerRef } from "../lib/types";
import { flag } from "../lib/flags";
import { STAGE_SHORT, formatDate, formatKickoff, isPlayable } from "../lib/data";
import { store, useStore, getPrediction, emptyPrediction } from "../lib/store";
import { computeScore, outcome } from "../lib/scoring";

interface Props {
  match: Match;
  userId: string;
}

function Stepper({
  value,
  onChange,
  disabled,
}: {
  value: number;
  onChange: (n: number) => void;
  disabled?: boolean;
}) {
  return (
    <div className="flex items-center gap-2">
      <button
        className="h-8 w-8 rounded-lg bg-white/5 border border-white/10 text-lg leading-none hover:bg-white/10 disabled:opacity-30"
        onClick={() => onChange(Math.max(0, value - 1))}
        disabled={disabled || value <= 0}
      >
        −
      </button>
      <span className="w-7 text-center text-2xl font-display font-bold tabular-nums">{value}</span>
      <button
        className="h-8 w-8 rounded-lg bg-white/5 border border-white/10 text-lg leading-none hover:bg-white/10 disabled:opacity-30"
        onClick={() => onChange(Math.min(15, value + 1))}
        disabled={disabled}
      >
        +
      </button>
    </div>
  );
}

export default function MatchCard({ match, userId }: Props) {
  const s = useStore();
  const pred = getPrediction(s, match.id, userId) ?? emptyPrediction(match.id, userId);
  const result = s.results[match.id];
  const playable = isPlayable(match);
  const [open, setOpen] = useState(false);

  const save = (patch: Partial<typeof pred>) => {
    store.setPrediction({ ...pred, ...patch, updatedAt: new Date().toISOString() });
  };
  const setScorers = (scorers: ScorerRef[]) => save({ scorers });

  const out = outcome(pred.home, pred.away);
  const hasPred = !!getPrediction(s, match.id, userId);
  const breakdown = result ? computeScore(pred, result) : null;

  return (
    <div className="glass p-4 sm:p-5 transition hover:border-white/20">
      {/* header */}
      <div className="mb-3 flex items-center justify-between text-xs text-wc-muted">
        <div className="flex items-center gap-2">
          <span className="chip bg-white/5 border border-white/10">
            {match.group ? `Girone ${match.group}` : STAGE_SHORT[match.stage]}
          </span>
          <span className="chip bg-white/5 border border-white/10">#{match.id}</span>
        </div>
        <div className="text-right leading-tight">
          <div>{formatDate(match.date)} · {formatKickoff(match.kickoff)}</div>
          <div className="truncate max-w-[180px] opacity-80">{match.venue}</div>
        </div>
      </div>

      {/* teams + score */}
      <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-2">
        <div className="flex flex-col items-center gap-1 text-center">
          <span className="text-4xl drop-shadow">{flag(match.home)}</span>
          <span className="text-sm font-semibold leading-tight">{match.home}</span>
        </div>

        <div className="flex flex-col items-center gap-2">
          {playable ? (
            <div className="flex items-center gap-3">
              <Stepper value={pred.home} onChange={(n) => save({ home: n })} />
              <span className="text-wc-muted">:</span>
              <Stepper value={pred.away} onChange={(n) => save({ away: n })} />
            </div>
          ) : (
            <span className="chip bg-white/5 border border-white/10 text-wc-muted">da definire</span>
          )}
          <OutcomeBadge out={out} active={playable && hasPred} />
        </div>

        <div className="flex flex-col items-center gap-1 text-center">
          <span className="text-4xl drop-shadow">{flag(match.away)}</span>
          <span className="text-sm font-semibold leading-tight">{match.away}</span>
        </div>
      </div>

      {/* scorers toggle */}
      {playable && (
        <div className="mt-4">
          <button
            onClick={() => setOpen((o) => !o)}
            className="btn-ghost w-full justify-between text-sm"
          >
            <span>
              ⚽ Marcatori{" "}
              {pred.scorers.length > 0 && (
                <span className="ml-1 chip bg-wc-grad text-white">{pred.scorers.length}</span>
              )}
            </span>
            <span className={`transition ${open ? "rotate-180" : ""}`}>▾</span>
          </button>
          {open && (
            <div className="mt-3">
              <ScorerHint home={pred.home} away={pred.away} count={pred.scorers.length} />
              <div className="mt-2">
                <ScorerPicker match={match} value={pred.scorers} onChange={setScorers} />
              </div>
            </div>
          )}
        </div>
      )}

      {/* result + points */}
      {result && (
        <div className="mt-4 flex items-center justify-between rounded-2xl bg-black/30 border border-white/10 px-4 py-3">
          <div className="text-sm">
            <div className="text-wc-muted text-xs uppercase tracking-wide">Risultato finale</div>
            <div className="font-display text-lg font-bold">
              {match.home} {result.home}–{result.away} {match.away}
            </div>
          </div>
          {breakdown && <PointsBadge total={breakdown.total} voided={breakdown.voided} />}
        </div>
      )}
    </div>
  );
}

function OutcomeBadge({ out, active }: { out: "1" | "X" | "2"; active: boolean }) {
  const label = out === "1" ? "1 · Casa" : out === "2" ? "2 · Ospite" : "X · Pari";
  return (
    <span
      className={`chip border ${
        active
          ? "bg-wc-grad text-white border-transparent shadow-glow"
          : "bg-white/5 border-white/10 text-wc-muted"
      }`}
    >
      {label}
    </span>
  );
}

function PointsBadge({ total, voided }: { total: number; voided: boolean }) {
  return (
    <div className="text-right">
      <div
        className={`font-display text-2xl font-bold ${
          total > 0 ? "text-wc-gold" : "text-wc-muted"
        }`}
      >
        +{total}
      </div>
      <div className="text-[10px] uppercase tracking-wide text-wc-muted">
        {voided ? "marcatori annullati" : "punti"}
      </div>
    </div>
  );
}

function ScorerHint({ home, away, count }: { home: number; away: number; count: number }) {
  const goals = home + away;
  if (goals === 0) return null;
  const diff = count - goals;
  return (
    <p className="text-xs text-wc-muted">
      Hai pronosticato <b className="text-wc-ink">{goals}</b> gol · marcatori scelti:{" "}
      <b className={diff === 0 ? "text-wc-lime" : "text-wc-pink"}>{count}</b>
      {diff !== 0 && (
        <span> ({diff > 0 ? `${diff} di troppo` : `mancano ${-diff}`})</span>
      )}
    </p>
  );
}
