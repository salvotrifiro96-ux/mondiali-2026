export type Position = "GK" | "DF" | "MF" | "FW";

export interface Player {
  name: string;
  number: number | null;
  position: Position;
  club: string;
  goals: number;
}

export type Stage =
  | "group"
  | "round_of_32"
  | "round_of_16"
  | "quarter_final"
  | "semi_final"
  | "third_place"
  | "final";

export interface Match {
  id: number;
  stage: Stage;
  group: string | null;
  date: string | null;
  kickoff: string;
  home: string;
  away: string;
  venue: string;
  confirmed: boolean;
}

export interface FixturesData {
  lastUpdated: string;
  source: string;
  groups: Record<string, string[]>;
  matches: Match[];
}

export interface SquadsData {
  lastUpdated: string;
  source: string;
  squads: Record<string, Player[]>;
}

/** A scorer reference: which team + player name (names can repeat across teams). */
export interface ScorerRef {
  team: string;
  name: string;
}

/** A user's prediction for a single match. */
export interface Prediction {
  matchId: number;
  userId: string;
  home: number;
  away: number;
  scorers: ScorerRef[];
  updatedAt: string;
}

/** The official final result of a match (entered by admin). */
export interface MatchResult {
  matchId: number;
  home: number;
  away: number;
  scorers: ScorerRef[];
}

export interface Participant {
  id: string;
  name: string;
}
