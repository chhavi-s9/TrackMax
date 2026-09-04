import { SECTIONS, STATION_X, STATIONS, TRACK_Y } from "../data/network";
import { useOps } from "../state/OpsContext";
import type { LiveBlock, LiveTrain, SelectedEntity } from "../types";

const W = 1030;
const H = 210;

function blockFill(status: LiveBlock["status"]): string {
  if (status === "CONFLICT" || status === "ACTIVE") return "#c81e1e";
  if (status === "PLANNED" || status === "APPROVED") return "#c9a227";
  return "#2f8f63";
}

function xOf(code: string): number {
  return STATION_X[code];
}

function sectionGeom(sectionId: string): { x1: number; x2: number; y: number } | null {
  const sec = SECTIONS.find((s) => s.id === sectionId);
  if (!sec) return null;
  const x1 = Math.min(xOf(sec.from), xOf(sec.to));
  const x2 = Math.max(xOf(sec.from), xOf(sec.to));
  return { x1, x2, y: TRACK_Y[sec.track] };
}

function trainPoint(train: LiveTrain): { x: number; y: number } | null {
  const g = sectionGeom(train.sectionId);
  if (!g) return null;
  const sec = SECTIONS.find((s) => s.id === train.sectionId);
  if (!sec) return null;
  const goingRight = xOf(sec.to) > xOf(sec.from);
  const t = goingRight ? train.progress : 1 - train.progress;
  return { x: g.x1 + (g.x2 - g.x1) * t, y: g.y };
}

function isSelected(sel: SelectedEntity | null, kind: SelectedEntity["kind"], id: string) {
  return sel?.kind === kind && sel.id === id;
}

export function CorridorDiagram() {
  const { trains, blocks, conflicts, selected, select } = useOps();

  const pick = (next: SelectedEntity) => () => select(next);

  return (
    <div className="diagram-wrap">
      <div className="diagram-legend">
        <span>
          <i className="swatch green" /> Available
        </span>
        <span>
          <i className="swatch amber" /> Planned block
        </span>
        <span>
          <i className="swatch red" /> Active / conflict
        </span>
        <span>
          <i className="swatch blue" /> Train
        </span>
        <span>Jaipur division · BKI — JP — GADJ — FL — KSG — AII — MJ</span>
      </div>
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Jaipur division track schematic">
        <text x="12" y={TRACK_Y.UP + 4} fill="#8d99a6" fontSize="11">
          UP
        </text>
        <text x="12" y={TRACK_Y.DN + 4} fill="#8d99a6" fontSize="11">
          DN
        </text>

        {SECTIONS.map((sec) => {
          const x1 = xOf(sec.from);
          const x2 = xOf(sec.to);
          const y = TRACK_Y[sec.track];
          const left = Math.min(x1, x2);
          const width = Math.abs(x2 - x1);
          const active = isSelected(selected, "section", sec.id);
          return (
            <g key={sec.id}>
              <line x1={x1} y1={y} x2={x2} y2={y} stroke="#2f8f63" strokeWidth="3" />
              <rect
                x={left}
                y={y - 10}
                width={width}
                height="20"
                fill="transparent"
                role="button"
                tabIndex={0}
                aria-label={`Section ${sec.id} ${sec.label}`}
                onClick={pick({ kind: "section", id: sec.id })}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") pick({ kind: "section", id: sec.id })();
                }}
                style={{ cursor: "pointer" }}
                stroke={active ? "#c81e1e" : "transparent"}
                strokeWidth={active ? 1 : 0}
              />
            </g>
          );
        })}

        {blocks
          .filter((b) => b.status !== "COMPLETED")
          .map((b) => {
            const g = sectionGeom(b.sectionId);
            if (!g) return null;
            const pad = 6;
            const active = isSelected(selected, "block", b.id);
            return (
              <g key={b.id} onClick={(e) => { e.stopPropagation(); pick({ kind: "block", id: b.id })(); }} style={{ cursor: "pointer" }}>
                <rect
                  x={g.x1 + pad}
                  y={g.y - 6}
                  width={g.x2 - g.x1 - pad * 2}
                  height="12"
                  fill={blockFill(b.status)}
                  stroke={active ? "#e6edf3" : "transparent"}
                  strokeWidth={active ? 1 : 0}
                />
                <text
                  x={(g.x1 + g.x2) / 2}
                  y={g.y - 10}
                  textAnchor="middle"
                  fill="#dce3ea"
                  fontSize="10"
                  fontFamily="Consolas, monospace"
                >
                  {b.sectionId} {b.start}–{b.end}
                </text>
              </g>
            );
          })}

        {STATIONS.map((st) => {
          const x = xOf(st.code);
          const active = isSelected(selected, "station", st.code);
          return (
            <g key={st.code} onClick={(e) => { e.stopPropagation(); pick({ kind: "station", id: st.code })(); }} style={{ cursor: "pointer" }}>
              <line x1={x} y1={TRACK_Y.UP - 14} x2={x} y2={TRACK_Y.DN + 14} stroke={active ? "#c81e1e" : "#3a4654"} />
              <rect x={x - 16} y={TRACK_Y.UP - 36} width="32" height="16" fill="#141c26" stroke={active ? "#c81e1e" : "#2a3340"} />
              <text x={x} y={TRACK_Y.UP - 24} textAnchor="middle" fill="#e6edf3" fontSize="11" fontWeight="700">
                {st.code}
              </text>
              <text x={x} y={TRACK_Y.DN + 32} textAnchor="middle" fill="#8d99a6" fontSize="10">
                {st.name}
              </text>
            </g>
          );
        })}

        {trains.map((train) => {
          const p = trainPoint(train);
          if (!p) return null;
          const active = isSelected(selected, "train", train.id);
          const dir = train.direction === "UP" ? 1 : -1;
          return (
            <g
              key={train.id}
              transform={`translate(${p.x}, ${p.y})`}
              onClick={(e) => {
                e.stopPropagation();
                pick({ kind: "train", id: train.id })();
              }}
              style={{ cursor: "pointer" }}
            >
              <title>{`${train.number} ${train.name}`}</title>
              <circle r="14" fill="transparent" />
              <g className={train.speedKmh > 0 ? "train-move" : undefined}>
                <rect x={-11} y={-6} width="22" height="12" rx="2" fill="#3d7eb8" stroke={active ? "#e6edf3" : "#1a232e"} />
                <rect x={dir > 0 ? 7 : -11} y={-4} width="6" height="8" fill="#2b5f8c" />
                <circle cx={-5} cy={6} r="1.6" fill="#dce3ea" />
                <circle cx={5} cy={6} r="1.6" fill="#dce3ea" />
              </g>
              <text x="0" y={train.direction === "UP" ? -12 : 20} textAnchor="middle" fill="#b9d4ea" fontSize="10" fontFamily="Consolas, monospace">
                {train.number}
                {train.direction === "UP" ? " →" : " ←"}
              </text>
            </g>
          );
        })}

        {conflicts.map((c) => {
          const train = trains.find((t) => t.id === c.trainId);
          const p = train ? trainPoint(train) : sectionGeom(c.sectionId);
          if (!p) return null;
          const x = "x" in p ? p.x : (p.x1 + p.x2) / 2;
          const y = "y" in p ? p.y - 28 : p.y - 28;
          const active = isSelected(selected, "conflict", c.id);
          return (
            <g key={c.id} onClick={(e) => { e.stopPropagation(); pick({ kind: "conflict", id: c.id })(); }} style={{ cursor: "pointer" }}>
              <polygon points={`${x},${y - 7} ${x + 7},${y + 5} ${x - 7},${y + 5}`} fill="#c81e1e" stroke={active ? "#e6edf3" : "none"} />
            </g>
          );
        })}
      </svg>
    </div>
  );
}
