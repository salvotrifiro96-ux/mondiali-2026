import fixturesRaw from "../data/fixtures.json";
import squadsRaw from "../data/squads.json";
import type { FixturesData, SquadsData, Match, Player, Stage, Participant } from "./types";

const fixtures = fixturesRaw as FixturesData;
const squadsData = squadsRaw as SquadsData;

export const GROUPS = fixtures.groups;
export const MATCHES: Match[] = [...fixtures.matches].sort((a, b) => a.id - b.id);
export const SQUADS = squadsData.squads;
export const DATA_UPDATED = fixtures.lastUpdated;

// I 6 partecipanti del gruppo.
export const PARTICIPANTS: Participant[] = [
  { id: "salvo", name: "Salvo" },
  { id: "diego", name: "Diego" },
  { id: "andrea", name: "Andrea" },
  { id: "giovanni", name: "Giovanni" },
  { id: "carmelo", name: "Carmelo" },
  { id: "francesco", name: "Francesco" },
];

export const STAGE_LABEL: Record<Stage, string> = {
  group: "Fase a gironi",
  round_of_32: "Sedicesimi",
  round_of_16: "Ottavi",
  quarter_final: "Quarti",
  semi_final: "Semifinali",
  third_place: "Finale 3º posto",
  final: "Finale",
};

export const STAGE_SHORT: Record<Stage, string> = {
  group: "Gironi",
  round_of_32: "16esimi",
  round_of_16: "Ottavi",
  quarter_final: "Quarti",
  semi_final: "Semi",
  third_place: "3º posto",
  final: "Finale",
};

export function squadFor(team: string): Player[] {
  return SQUADS[team] ?? [];
}

/** Giocatori selezionabili come marcatori per una partita (entrambe le squadre). */
export function scorerPool(match: Match): { team: string; players: Player[] }[] {
  const out: { team: string; players: Player[] }[] = [];
  for (const team of [match.home, match.away]) {
    const players = squadFor(team);
    if (players.length) out.push({ team, players });
  }
  return out;
}

export function isPlayable(match: Match): boolean {
  // Marcatori disponibili solo se conosciamo le rose di entrambe le squadre.
  return squadFor(match.home).length > 0 && squadFor(match.away).length > 0;
}

const MONTHS_IT = [
  "gen", "feb", "mar", "apr", "mag", "giu",
  "lug", "ago", "set", "ott", "nov", "dic",
];

export function formatDate(iso: string | null): string {
  if (!iso) return "—";
  const [y, m, d] = iso.split("-").map(Number);
  return `${d} ${MONTHS_IT[m - 1]} ${y}`;
}

export function formatKickoff(k: string): string {
  // "1:00 p.m. UTC−6" -> "13:00 (UTC−6)" circa
  const m = k.match(/(\d{1,2}):(\d{2})\s*([ap])\.?m\.?\s*(UTC[−+]?\d+)?/i);
  if (!m) return k;
  let h = parseInt(m[1], 10);
  const min = m[2];
  const pm = m[3].toLowerCase() === "p";
  if (pm && h !== 12) h += 12;
  if (!pm && h === 12) h = 0;
  const tz = m[4] ? ` (${m[4]})` : "";
  return `${String(h).padStart(2, "0")}:${min}${tz}`;
}
