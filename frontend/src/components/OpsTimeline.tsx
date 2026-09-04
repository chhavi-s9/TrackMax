import { CLOCK } from "../data/network";
import { useOps } from "../state/OpsContext";

const START = 12 * 60;
const END = 22 * 60;
const LEFT = 118;
const TOP = 28;
const ROW_H = 28;
const WIDTH = 920;

function toMin(hhmm: string): number {
  const [h, m] = hhmm.split(":").map(Number);
  return h * 60 + m;
}

function xAt(hhmm: string): number {
  const t = Math.min(END, Math.max(START, toMin(hhmm)));
  return LEFT + ((t - START) / (END - START)) * WIDTH;
}

function wBetween(a: string, b: string): number {
  return Math.max(8, xAt(b) - xAt(a));
}

export function OpsTimeline() {
  const { trains, blocks, conflicts, selected, select } = useOps();
  const rows = [
    ...blocks.filter((b) => b.date === "2026-09-05").map((b) => ({ kind: "block" as const, id: b.id, label: b.sectionId, sub: b.code })),
    ...trains.map((t) => ({ kind: "train" as const, id: t.id, label: t.number, sub: `${t.from}→${t.to}` })),
  ];
  const height = TOP + rows.length * ROW_H + 16;
  const hours = [];
  for (let h = 12; h <= 22; h += 1) hours.push(h);
  const nowX = xAt(CLOCK);

  return (
    <div className="timeline">
      <svg viewBox={`0 0 1060 ${height}`} role="img" aria-label="Block and train timeline">
        {hours.map((h) => {
          const x = xAt(`${String(h).padStart(2, "0")}:00`);
          return (
            <g key={h}>
              <line x1={x} y1={18} x2={x} y2={height - 8} stroke="#2a3340" />
              <text x={x} y="14" fill="#8d99a6" fontSize="10" textAnchor="middle" fontFamily="Consolas, monospace">
                {String(h).padStart(2, "0")}:00
              </text>
            </g>
          );
        })}
        <line x1={nowX} y1={18} x2={nowX} y2={height - 8} stroke="#c81e1e" strokeDasharray="2 3" />
        <text x={nowX + 4} y="14" fill="#c81e1e" fontSize="10">
          {CLOCK}
        </text>

        {rows.map((row, i) => {
          const y = TOP + i * ROW_H;
          const active = selected?.id === row.id;
          return (
            <g key={`${row.kind}-${row.id}`}>
              <rect x="0" y={y} width="1060" height={ROW_H} fill={i % 2 ? "#121a24" : "#141c26"} />
              <text x="10" y={y + 18} fill="#8d99a6" fontSize="11" fontFamily="Consolas, monospace">
                {row.label}
              </text>
              <line x1={LEFT} y1={y + ROW_H / 2} x2={LEFT + WIDTH} y2={y + ROW_H / 2} stroke="#2a3340" />
              {row.kind === "block"
                ? (() => {
                    const b = blocks.find((x) => x.id === row.id);
                    if (!b) return null;
                    const fill = b.status === "CONFLICT" || b.status === "ACTIVE" ? "#c81e1e" : b.status === "COMPLETED" ? "#2f8f63" : "#c9a227";
                    return (
                      <g
                        onClick={() => select({ kind: "block", id: b.id })}
                        style={{ cursor: "pointer" }}
                      >
                        <rect
                          x={xAt(b.start)}
                          y={y + 7}
                          width={wBetween(b.start, b.end)}
                          height="14"
                          fill={fill}
                          stroke={active ? "#e6edf3" : "transparent"}
                        />
                        <text x={xAt(b.start) + 6} y={y + 18} fill="#0a1018" fontSize="10" fontWeight="700">
                          {b.maintenanceType.split(" ")[0]}
                        </text>
                      </g>
                    );
                  })()
                : (() => {
                    const t = trains.find((x) => x.id === row.id);
                    if (!t) return null;
                    const x = xAt(CLOCK) + (t.direction === "UP" ? 18 : -18);
                    const conflicted = conflicts.some((c) => c.trainId === t.id);
                    return (
                      <g onClick={() => select({ kind: "train", id: t.id })} style={{ cursor: "pointer" }}>
                        <rect
                          x={x - 16}
                          y={y + 8}
                          width="32"
                          height="12"
                          rx="2"
                          fill="#3d7eb8"
                          stroke={selected?.id === t.id ? "#e6edf3" : conflicted ? "#c81e1e" : "transparent"}
                        />
                        <text x={x} y={y + 17} textAnchor="middle" fill="#e6edf3" fontSize="8" fontFamily="Consolas, monospace">
                          {t.number}
                        </text>
                      </g>
                    );
                  })()}
            </g>
          );
        })}
      </svg>
    </div>
  );
}
