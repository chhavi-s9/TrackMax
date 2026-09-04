export type EntityKind =
  | "train"
  | "station"
  | "section"
  | "block"
  | "conflict"
  | "asset"
  | "report"
  | "alert";

export type TrackDir = "UP" | "DN";

export type BlockStatus = "PLANNED" | "ACTIVE" | "COMPLETED" | "CONFLICT" | "APPROVED";

export type TrainRunStatus = "On Time" | "Delayed" | "Held" | "Cancelled";

export type WeatherKind = "NORMAL" | "HEAVY_RAIN" | "HEATWAVE" | "FOG" | "THUNDERSTORM";

export interface SelectedEntity {
  kind: EntityKind;
  id: string;
}

export interface Station {
  code: string;
  name: string;
  km: number;
}

export interface TrackSection {
  id: string;
  corridor: string;
  from: string;
  to: string;
  track: TrackDir;
  kmFrom: number;
  kmTo: number;
  label: string;
}

export interface LiveTrain {
  id: string;
  number: string;
  name: string;
  type: string;
  priority: string;
  status: TrainRunStatus;
  delayMin: number;
  sectionId: string;
  from: string;
  to: string;
  nextStation: string;
  direction: TrackDir;
  progress: number;
  speedKmh: number;
  eta: string;
  route: string;
  impact: string;
}

export interface LiveBlock {
  id: string;
  code: string;
  sectionId: string;
  corridor: string;
  track: TrackDir | "BOTH";
  department: string;
  maintenanceType: string;
  start: string;
  end: string;
  date: string;
  status: BlockStatus;
  affectedTrainIds: string[];
  recommendation?: string;
  weatherRisk?: "Low" | "High";
}

export interface Conflict {
  id: string;
  type: string;
  sectionId: string;
  trainId: string;
  blockId: string;
  time: string;
  summary: string;
}

export interface AssetRow {
  id: string;
  assetId: string;
  type: string;
  location: string;
  section: string;
  status: string;
  assignment: string;
  availability: string;
  department: string;
  condition: number;
}

export interface ReportRow {
  id: string;
  reportId: string;
  blockId: string;
  section: string;
  maintenanceType: string;
  planned: string;
  actual: string;
  weather: string;
  assetsAffected: string;
  trainsAffected: string;
  delay: string;
  completion: string;
  analysis: string;
  department: string;
  supervisor: string;
  remarks: string;
}

export interface AlertRow {
  id: string;
  severity: "info" | "warning" | "critical";
  time: string;
  location: string;
  message: string;
  actionTo: string;
  actionLabel: string;
}

export interface WeatherState {
  section: string;
  type: WeatherKind;
  severity: number;
  rainfall: number;
  temperature: number;
  visibility: number;
  window: string;
  description: string;
}

export interface PlanOption {
  id: string;
  label: string;
  start: string;
  end: string;
  weatherRisk: "Low" | "High";
  trainConflicts: number;
  note: string;
  suggested?: boolean;
}
