import type { AssetRow, LiveBlock, LiveTrain } from "../types";
import { ASSETS, BLOCKS, TRAINS } from "../data/demo";

const TIMEOUT_MS = 1800;

async function getJson<T>(path: string): Promise<T | null> {
  try {
    const res = await fetch(path, { signal: AbortSignal.timeout(TIMEOUT_MS) });
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

export async function postJson<T>(path: string, body: unknown): Promise<T | null> {
  try {
    const res = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(8000),
    });
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

export async function probeApi(): Promise<boolean> {
  const health = await getJson<{ status: string }>("/health");
  return health?.status === "ok";
}

interface ApiTrain {
  id: number;
  train_number: string;
  train_name: string;
  train_type: string;
  priority: string;
  operating_status: string;
}

interface ApiBlock {
  id: number;
  block_code: string;
  section: string;
  start_time: string;
  end_time: string;
  status: string;
  block_type: string;
}

interface ApiAsset {
  id: number;
  asset_code: string;
  asset_type: string;
  name: string;
  section: string;
  location: string | null;
  status: string;
  department_id: number;
  condition_score: number;
}

function hhmm(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso.slice(11, 16);
  return d.toISOString().slice(11, 16);
}

export async function loadLiveOverlay(): Promise<{
  live: boolean;
  trains: LiveTrain[];
  blocks: LiveBlock[];
  assets: AssetRow[];
}> {
  const [apiOk, trains, blocks, assets] = await Promise.all([
    probeApi(),
    getJson<ApiTrain[]>("/api/trains"),
    getJson<ApiBlock[]>("/api/blocks"),
    getJson<ApiAsset[]>("/api/assets"),
  ]);

  if (!apiOk) {
    return { live: false, trains: TRAINS, blocks: BLOCKS, assets: ASSETS };
  }

  const mergedTrains = TRAINS.map((t) => {
    const hit = trains?.find((row) => row.train_number === t.number);
    if (!hit) return t;
    return { ...t, name: hit.train_name, type: hit.train_type, priority: hit.priority };
  });

  const mergedBlocks = BLOCKS.map((b) => {
    const hit = blocks?.find((row) => row.block_code === b.code);
    if (!hit) return b;
    return {
      ...b,
      start: hhmm(hit.start_time) || b.start,
      end: hhmm(hit.end_time) || b.end,
    };
  });

  const mergedAssets =
    assets && assets.length
      ? assets.map((a) => ({
          id: String(a.id),
          assetId: a.asset_code,
          type: a.asset_type,
          location: a.location ?? a.name,
          section: a.section,
          status: a.status,
          assignment: "—",
          availability: a.status === "OPERATIONAL" ? "Available" : a.status.replaceAll("_", " "),
          department: String(a.department_id),
          condition: a.condition_score,
        }))
      : ASSETS;

  return { live: true, trains: mergedTrains, blocks: mergedBlocks, assets: mergedAssets };
}

export interface RescheduleResult {
  original?: { start?: string; end?: string };
  new?: { start?: string; end?: string };
  reason?: string;
  weather_condition?: string;
}

export async function requestReschedule(section: string, weather: string, date: string) {
  return postJson<RescheduleResult>("/api/weather/reschedule", {
    section,
    date,
    weather,
  });
}
