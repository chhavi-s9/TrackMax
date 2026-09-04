import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { loadLiveOverlay } from "../api/client";
import { ALERTS, CONFLICTS, CURRENT_PLAN, METRICS, RECOMMENDED_PLAN, REPORTS, WEATHER_NOW } from "../data/demo";
import type {
  AlertRow,
  AssetRow,
  Conflict,
  LiveBlock,
  LiveTrain,
  PlanOption,
  ReportRow,
  SelectedEntity,
  WeatherKind,
  WeatherState,
} from "../types";

interface OpsState {
  live: boolean;
  selected: SelectedEntity | null;
  select: (next: SelectedEntity | null) => void;
  trains: LiveTrain[];
  blocks: LiveBlock[];
  assets: AssetRow[];
  conflicts: Conflict[];
  reports: ReportRow[];
  alerts: AlertRow[];
  weather: WeatherState;
  setWeatherType: (type: WeatherKind) => void;
  currentPlan: PlanOption;
  recommendedPlan: PlanOption;
  accepted: boolean;
  acceptRecommended: () => void;
  metrics: typeof METRICS;
}

const OpsContext = createContext<OpsState | null>(null);

export function OpsProvider({ children }: { children: ReactNode }) {
  const [live, setLive] = useState(false);
  const [selected, setSelected] = useState<SelectedEntity | null>(null);
  const [trains, setTrains] = useState<LiveTrain[]>([]);
  const [blocks, setBlocks] = useState<LiveBlock[]>([]);
  const [assets, setAssets] = useState<AssetRow[]>([]);
  const [accepted, setAccepted] = useState(false);
  const [weather, setWeather] = useState<WeatherState>(WEATHER_NOW);

  useEffect(() => {
    let cancelled = false;
    loadLiveOverlay().then((data) => {
      if (cancelled) return;
      setLive(data.live);
      setTrains(data.trains);
      setBlocks(data.blocks);
      setAssets(data.assets);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const value = useMemo<OpsState>(() => {
    const displayBlocks = accepted
      ? blocks.map((b) =>
          b.id === "BLK-T02"
            ? {
                ...b,
                start: RECOMMENDED_PLAN.start,
                end: RECOMMENDED_PLAN.end,
                status: "PLANNED" as const,
                weatherRisk: "Low" as const,
                affectedTrainIds: ["G-JP-01"],
              }
            : b,
        )
      : blocks;

    const displayTrains = accepted
      ? trains.map((t) =>
          t.id === "19707" || t.id === "12413"
            ? { ...t, status: "On Time" as const, delayMin: 0, speedKmh: t.id === "19707" ? 78 : 84, impact: "Clear of T-02 after revision" }
            : t,
        )
      : trains;

    const displayConflicts = accepted ? [] : CONFLICTS;

    return {
      live,
      selected,
      select: setSelected,
      trains: displayTrains,
      blocks: displayBlocks,
      assets,
      conflicts: displayConflicts,
      reports: REPORTS,
      alerts: accepted ? ALERTS.filter((a) => a.id !== "AL-1") : ALERTS,
      weather,
      setWeatherType: (type) => setWeather((w) => ({ ...w, type })),
      currentPlan: accepted
        ? { ...RECOMMENDED_PLAN, id: "current", label: "Current plan", suggested: false }
        : CURRENT_PLAN,
      recommendedPlan: RECOMMENDED_PLAN,
      accepted,
      acceptRecommended: () => {
        setAccepted(true);
        setSelected({ kind: "block", id: "BLK-T02" });
      },
      metrics: {
        ...METRICS,
        conflicts: displayConflicts.length,
        trainsAffected: accepted ? 1 : METRICS.trainsAffected,
        divisionStatus: accepted ? "Normal" : METRICS.divisionStatus,
        activeBlocks: accepted ? 0 : METRICS.activeBlocks,
      },
    };
  }, [accepted, assets, blocks, live, selected, trains, weather]);

  return <OpsContext.Provider value={value}>{children}</OpsContext.Provider>;
}

export function useOps(): OpsState {
  const ctx = useContext(OpsContext);
  if (!ctx) throw new Error("useOps must be used inside OpsProvider");
  return ctx;
}
