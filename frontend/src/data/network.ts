import type { Station, TrackSection } from "../types";

export const DIVISION = "Jaipur (JP)";
export const OPERATING_DATE = "2026-09-05";
export const CLOCK = "14:42";

export const STATIONS: Station[] = [
  { code: "BKI", name: "Bandikui Jn", km: 0 },
  { code: "JP", name: "Jaipur Jn", km: 88 },
  { code: "GADJ", name: "Gandhinagar Jaipur", km: 95 },
  { code: "FL", name: "Phulera Jn", km: 139 },
  { code: "KSG", name: "Kishangarh", km: 187 },
  { code: "AII", name: "Ajmer Jn", km: 223 },
  { code: "MJ", name: "Marwar Jn", km: 321 },
];

export const STATION_X: Record<string, number> = {
  BKI: 56,
  JP: 210,
  GADJ: 360,
  FL: 520,
  KSG: 670,
  AII: 820,
  MJ: 974,
};

export const TRACK_Y: Record<"UP" | "DN", number> = {
  UP: 78,
  DN: 128,
};

const SEGMENTS: Array<[string, string, string, string, string]> = [
  ["T-11", "JP-BKI", "BKI", "JP", "UP"],
  ["T-12", "JP-BKI", "JP", "BKI", "DN"],
  ["T-01", "JP-AII", "JP", "GADJ", "UP"],
  ["T-02", "JP-AII", "GADJ", "JP", "DN"],
  ["T-03", "JP-AII", "GADJ", "FL", "UP"],
  ["T-04", "JP-AII", "FL", "GADJ", "DN"],
  ["T-05", "JP-AII", "FL", "KSG", "UP"],
  ["T-06", "JP-AII", "KSG", "FL", "DN"],
  ["T-07", "JP-AII", "KSG", "AII", "UP"],
  ["T-08", "JP-AII", "AII", "KSG", "DN"],
  ["T-21", "AII-MJ", "AII", "MJ", "UP"],
  ["T-22", "AII-MJ", "MJ", "AII", "DN"],
];

function kmOf(code: string): number {
  return STATIONS.find((s) => s.code === code)?.km ?? 0;
}

export const SECTIONS: TrackSection[] = SEGMENTS.map(([id, corridor, from, to, track]) => ({
  id,
  corridor,
  from,
  to,
  track: track as "UP" | "DN",
  kmFrom: kmOf(from),
  kmTo: kmOf(to),
  label: `${from}–${to} ${track}`,
}));

export function sectionById(id: string): TrackSection | undefined {
  return SECTIONS.find((s) => s.id === id);
}

export function stationByCode(code: string): Station | undefined {
  return STATIONS.find((s) => s.code === code);
}

export function corridorSections(corridor: string): TrackSection[] {
  return SECTIONS.filter((s) => s.corridor === corridor);
}
