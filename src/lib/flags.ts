// Mappa nome squadra (come nei dati) -> codice ISO-2 per generare l'emoji bandiera.
const ISO2: Record<string, string> = {
  "Czech Republic": "CZ",
  Mexico: "MX",
  "South Africa": "ZA",
  "South Korea": "KR",
  "Bosnia and Herzegovina": "BA",
  Canada: "CA",
  Qatar: "QA",
  Switzerland: "CH",
  Brazil: "BR",
  Haiti: "HT",
  Morocco: "MA",
  Australia: "AU",
  Paraguay: "PY",
  Turkey: "TR",
  "United States": "US",
  "Curaçao": "CW",
  Ecuador: "EC",
  Germany: "DE",
  "Ivory Coast": "CI",
  Japan: "JP",
  Netherlands: "NL",
  Sweden: "SE",
  Tunisia: "TN",
  Belgium: "BE",
  Egypt: "EG",
  Iran: "IR",
  "New Zealand": "NZ",
  "Cape Verde": "CV",
  "Saudi Arabia": "SA",
  Spain: "ES",
  Uruguay: "UY",
  France: "FR",
  Iraq: "IQ",
  Norway: "NO",
  Senegal: "SN",
  Algeria: "DZ",
  Argentina: "AR",
  Austria: "AT",
  Jordan: "JO",
  Colombia: "CO",
  "DR Congo": "CD",
  Portugal: "PT",
  Uzbekistan: "UZ",
  Croatia: "HR",
  Ghana: "GH",
  Panama: "PA",
};

// Bandiere delle nazioni costitutive UK (subdivision flag emoji)
const SPECIAL: Record<string, string> = {
  England: "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
  Scotland: "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
  Wales: "🏴󠁧󠁢󠁷󠁬󠁳󠁿",
};

function iso2ToEmoji(code: string): string {
  return code
    .toUpperCase()
    .replace(/./g, (c) => String.fromCodePoint(127397 + c.charCodeAt(0)));
}

/** Emoji bandiera per una squadra. Fallback: pallone. */
export function flag(team: string): string {
  if (SPECIAL[team]) return SPECIAL[team];
  const code = ISO2[team];
  return code ? iso2ToEmoji(code) : "⚽️";
}
