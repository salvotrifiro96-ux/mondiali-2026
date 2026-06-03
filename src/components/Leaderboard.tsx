import { useStore } from "../lib/store";
import { computeStandings } from "../lib/standings";

const MEDAL = ["🥇", "🥈", "🥉"];

export default function Leaderboard({ currentUser }: { currentUser: string }) {
  const s = useStore();
  const rows = computeStandings(s);
  const totalResults = Object.keys(s.results).length;
  const max = Math.max(1, rows[0]?.points ?? 1);

  return (
    <div className="glass p-5 sm:p-6">
      <div className="mb-5 flex items-end justify-between">
        <div>
          <h2 className="font-display text-2xl font-bold gradient-text">Classifica</h2>
          <p className="text-sm text-wc-muted">
            {totalResults} partite con risultato inserito
          </p>
        </div>
        <div className="text-4xl animate-floaty">🏆</div>
      </div>

      <div className="space-y-2">
        {rows.map((r, i) => {
          const me = r.id === currentUser;
          return (
            <div
              key={r.id}
              className={`relative overflow-hidden rounded-2xl border px-4 py-3 transition ${
                me ? "border-wc-cyan/50 bg-wc-cyan/5" : "border-white/10 bg-black/20"
              }`}
            >
              <div
                className="absolute inset-y-0 left-0 bg-wc-grad-soft"
                style={{ width: `${(r.points / max) * 100}%` }}
              />
              <div className="relative flex items-center gap-3">
                <div className="w-8 text-center text-xl font-display font-bold">
                  {MEDAL[i] ?? <span className="text-wc-muted">{i + 1}</span>}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold">{r.name}</span>
                    {me && <span className="chip bg-wc-cyan/20 text-wc-cyan">tu</span>}
                  </div>
                  <div className="mt-0.5 flex flex-wrap gap-x-3 gap-y-0.5 text-[11px] text-wc-muted">
                    <span>🎯 {r.exact} esatti</span>
                    <span>✅ {r.outcomes} 1X2</span>
                    <span>⚽ {r.scorerHits} marcatori</span>
                    {r.perfect > 0 && <span className="text-wc-gold">★ {r.perfect} perfetti</span>}
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-display text-2xl font-bold text-wc-gold tabular-nums">
                    {r.points}
                  </div>
                  <div className="text-[10px] uppercase tracking-wide text-wc-muted">punti</div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {totalResults === 0 && (
        <p className="mt-4 rounded-2xl bg-black/20 border border-white/10 px-4 py-6 text-center text-sm text-wc-muted">
          Nessun risultato ancora. Inserisci i risultati nella sezione{" "}
          <b className="text-wc-ink">Risultati</b> per far partire la classifica.
        </p>
      )}
    </div>
  );
}
