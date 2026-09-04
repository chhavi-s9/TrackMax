import { Link } from "react-router-dom";
import { SECTIONS, STATIONS, sectionById, stationByCode } from "../data/network";
import { useOps } from "../state/OpsContext";
import type { BlockStatus } from "../types";

function statusTag(status: string): string {
  if (status === "ACTIVE" || status === "CONFLICT" || status === "critical") return "tag red";
  if (status === "PLANNED" || status === "APPROVED" || status === "Delayed" || status === "Held" || status === "warning") return "tag amber";
  if (status === "COMPLETED" || status === "On Time" || status === "OPERATIONAL" || status === "info") return "tag green";
  return "tag";
}

function blockTone(status: BlockStatus): string {
  if (status === "CONFLICT" || status === "ACTIVE") return "red";
  if (status === "PLANNED" || status === "APPROVED") return "amber";
  return "green";
}

export function Inspector() {
  const { selected, trains, blocks, conflicts, assets, reports, alerts, select, recommendedPlan, accepted, acceptRecommended } = useOps();
  if (!selected) return null;

  if (selected.kind === "train") {
    const t = trains.find((x) => x.id === selected.id);
    if (!t) return <Empty />;
    const sec = sectionById(t.sectionId);
    return (
      <aside className="inspector">
        <h2>Train</h2>
        <h3>{t.number}</h3>
        <p className="muted" style={{ marginTop: 0 }}>
          {t.name} · {t.type}
        </p>
        <dl className="kv">
          <dt>Status</dt>
          <dd>
            <span className={statusTag(t.status)}>{t.status}</span>
            {t.delayMin ? `  +${t.delayMin} min` : ""}
          </dd>
          <dt>Current section</dt>
          <dd>
            {t.from} → {t.to}
          </dd>
          <dt>Track</dt>
          <dd>{sec?.id} {sec?.track}</dd>
          <dt>Next station</dt>
          <dd>{t.nextStation}</dd>
          <dt>Speed</dt>
          <dd>{t.speedKmh} km/h</dd>
          <dt>Expected arrival</dt>
          <dd>{t.eta}</dd>
          <dt>Route</dt>
          <dd>{t.route}</dd>
          <dt>Impact</dt>
          <dd>{t.impact}</dd>
        </dl>
        <div className="actions">
          <Link className="btn ghost" to="/network" onClick={() => select({ kind: "section", id: t.sectionId })}>
            Open section
          </Link>
        </div>
      </aside>
    );
  }

  if (selected.kind === "station") {
    const s = stationByCode(selected.id) ?? STATIONS.find((x) => x.code === selected.id);
    if (!s) return <Empty />;
    const here = trains.filter((t) => t.from === s.code || t.to === s.code || t.nextStation === s.code);
    return (
      <aside className="inspector">
        <h2>Station</h2>
        <h3>{s.code}</h3>
        <p className="muted" style={{ marginTop: 0 }}>
          {s.name} · km {s.km}
        </p>
        <dl className="kv">
          <dt>Division</dt>
          <dd>Jaipur</dd>
          <dt>Corridor</dt>
          <dd>BKI–JP–AII–MJ</dd>
          <dt>Trains nearby</dt>
          <dd>{here.map((t) => t.number).join(", ") || "None"}</dd>
        </dl>
        <div className="actions">
          <Link className="btn ghost" to="/network">
            Network
          </Link>
        </div>
      </aside>
    );
  }

  if (selected.kind === "section") {
    const sec = sectionById(selected.id) ?? SECTIONS.find((x) => x.id === selected.id);
    if (!sec) return <Empty />;
    const occ = trains.filter((t) => t.sectionId === sec.id);
    const blk = blocks.filter((b) => b.sectionId === sec.id);
    const clear = blk.every((b) => b.status === "COMPLETED") && occ.length === 0;
    return (
      <aside className="inspector">
        <h2>Track section</h2>
        <h3>{sec.id}</h3>
        <p className="muted" style={{ marginTop: 0 }}>
          {sec.from} → {sec.to} · {sec.track} · {sec.corridor}
        </p>
        <dl className="kv">
          <dt>Status</dt>
          <dd>
            <span className={clear ? "tag green" : blk.some((b) => b.status === "CONFLICT" || b.status === "ACTIVE") ? "tag red" : "tag amber"}>
              {clear ? "Available" : blk[0]?.status.replace("_", " ") ?? "Occupied"}
            </span>
          </dd>
          <dt>Km</dt>
          <dd>
            {sec.kmFrom}–{sec.kmTo}
          </dd>
          <dt>Trains</dt>
          <dd>{occ.map((t) => t.number).join(", ") || "None"}</dd>
          <dt>Blocks</dt>
          <dd>{blk.map((b) => b.code).join(", ") || "None"}</dd>
        </dl>
      </aside>
    );
  }

  if (selected.kind === "block") {
    const b = blocks.find((x) => x.id === selected.id);
    if (!b) return <Empty />;
    const affected = trains.filter((t) => b.affectedTrainIds.includes(t.id));
    const rec = b.id === "BLK-T02" && !accepted;
    return (
      <aside className="inspector">
        <h2>Maintenance block</h2>
        <h3>{b.code}</h3>
        <dl className="kv">
          <dt>Status</dt>
          <dd>
            <span className={`tag ${blockTone(b.status)}`}>{b.status}</span>
          </dd>
          <dt>Section</dt>
          <dd>
            {sectionById(b.sectionId)?.from} → {sectionById(b.sectionId)?.to} ({b.sectionId})
          </dd>
          <dt>Department</dt>
          <dd>{b.department}</dd>
          <dt>Maintenance</dt>
          <dd>{b.maintenanceType}</dd>
          <dt>Start</dt>
          <dd>{b.start}</dd>
          <dt>End</dt>
          <dd>{b.end}</dd>
          <dt>Weather risk</dt>
          <dd>{b.weatherRisk ?? "—"}</dd>
          <dt>Affected trains</dt>
          <dd>{affected.map((t) => t.number).join(", ") || "None"}</dd>
        </dl>
        {rec && b.recommendation ? (
          <>
            <p className="muted" style={{ marginTop: 12 }}>
              <span className="tag cyan">Suggested by RailDoot</span>
            </p>
            <p>{b.recommendation}</p>
            <p className="mono">
              {recommendedPlan.start}–{recommendedPlan.end} · {recommendedPlan.trainConflicts} conflict
            </p>
            <div className="actions">
              <button className="btn" type="button" onClick={acceptRecommended}>
                Accept revised plan
              </button>
              <Link className="btn ghost" to="/weather">
                Weather & Replanning
              </Link>
            </div>
          </>
        ) : (
          <div className="actions">
            <Link className="btn ghost" to="/planning">
              Open in planning
            </Link>
          </div>
        )}
      </aside>
    );
  }

  if (selected.kind === "conflict") {
    const c = conflicts.find((x) => x.id === selected.id);
    if (!c) return <Empty />;
    const train = trains.find((t) => t.id === c.trainId);
    const block = blocks.find((b) => b.id === c.blockId);
    return (
      <aside className="inspector">
        <h2>Conflict</h2>
        <h3>{c.type.replaceAll("_", " ")}</h3>
        <p>{c.summary}</p>
        <dl className="kv">
          <dt>Time</dt>
          <dd>{c.time}</dd>
          <dt>Train</dt>
          <dd>{train?.number ?? c.trainId}</dd>
          <dt>Block</dt>
          <dd>{block?.code ?? c.blockId}</dd>
          <dt>Section</dt>
          <dd>{c.sectionId}</dd>
        </dl>
        <div className="actions">
          <button className="btn ghost" type="button" onClick={() => select({ kind: "block", id: c.blockId })}>
            Block details
          </button>
          <button className="btn ghost" type="button" onClick={() => select({ kind: "train", id: c.trainId })}>
            Train details
          </button>
        </div>
      </aside>
    );
  }

  if (selected.kind === "asset") {
    const a = assets.find((x) => x.id === selected.id || x.assetId === selected.id);
    if (!a) return <Empty />;
    return (
      <aside className="inspector">
        <h2>Asset</h2>
        <h3>{a.assetId}</h3>
        <dl className="kv">
          <dt>Type</dt>
          <dd>{a.type}</dd>
          <dt>Location</dt>
          <dd>{a.location}</dd>
          <dt>Section</dt>
          <dd>{a.section}</dd>
          <dt>Status</dt>
          <dd>
            <span className={statusTag(a.status)}>{a.status.replaceAll("_", " ")}</span>
          </dd>
          <dt>Assignment</dt>
          <dd>{a.assignment}</dd>
          <dt>Availability</dt>
          <dd>{a.availability}</dd>
          <dt>Condition</dt>
          <dd>{a.condition}</dd>
        </dl>
      </aside>
    );
  }

  if (selected.kind === "report") {
    const r = reports.find((x) => x.id === selected.id);
    if (!r) return <Empty />;
    return (
      <aside className="inspector">
        <h2>Report</h2>
        <h3>{r.reportId}</h3>
        <dl className="kv">
          <dt>Block</dt>
          <dd>{r.blockId}</dd>
          <dt>Section</dt>
          <dd>{r.section}</dd>
          <dt>Status</dt>
          <dd>{r.completion}</dd>
        </dl>
        <div className="actions">
          <Link className="btn" to={`/reports/${r.id}`}>
            Open record
          </Link>
        </div>
      </aside>
    );
  }

  if (selected.kind === "alert") {
    const a = alerts.find((x) => x.id === selected.id);
    if (!a) return <Empty />;
    return (
      <aside className="inspector">
        <h2>Alert</h2>
        <h3 className={a.severity === "critical" ? "red" : a.severity === "warning" ? "amber" : ""}>{a.message}</h3>
        <dl className="kv">
          <dt>Time</dt>
          <dd>{a.time}</dd>
          <dt>Location</dt>
          <dd>{a.location}</dd>
          <dt>Severity</dt>
          <dd>
            <span className={`tag ${a.severity === "critical" ? "red" : a.severity === "warning" ? "amber" : "blue"}`}>{a.severity}</span>
          </dd>
        </dl>
        <div className="actions">
          <Link className="btn" to={a.actionTo}>
            {a.actionLabel}
          </Link>
        </div>
      </aside>
    );
  }

  return <Empty />;
}

function Empty() {
  return (
    <aside className="inspector">
      <h2>Details</h2>
      <p className="muted">Selection not found.</p>
    </aside>
  );
}
