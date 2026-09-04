import { Link } from "react-router-dom";
import { CorridorDiagram } from "../components/CorridorDiagram";
import { DataTable } from "../components/DataTable";
import { OpsTimeline } from "../components/OpsTimeline";
import { useOps } from "../state/OpsContext";

export function BlockPlanning() {
  const { blocks, trains, weather, currentPlan, recommendedPlan, accepted, acceptRecommended, select } = useOps();
  const today = blocks.filter((b) => b.date === "2026-09-05");

  return (
    <>
      {weather.type === "HEAVY_RAIN" && !accepted ? (
        <div className="warn">
          <div>
            <strong>Weather may affect planned maintenance</strong>
            <div className="muted">
              Heavy rainfall expected {weather.window}. Tamping block T-02 currently {currentPlan.start}–{currentPlan.end}.
            </div>
          </div>
          <Link className="btn ghost" to="/weather">
            Weather & Replanning
          </Link>
        </div>
      ) : null}

      <div className="plan-compare">
        <div className="plan">
          <h3>Current plan</h3>
          <div className="when">
            {currentPlan.start}–{currentPlan.end}
          </div>
          <div className="muted">Weather risk: {currentPlan.weatherRisk}</div>
          <div className="muted">{currentPlan.trainConflicts} train conflicts</div>
          <p>{currentPlan.note}</p>
        </div>
        <div className="plan rec">
          <h3>Recommended</h3>
          <div className="when">
            {recommendedPlan.start}–{recommendedPlan.end}
          </div>
          <div className="muted">Weather risk: {recommendedPlan.weatherRisk}</div>
          <div className="muted">{recommendedPlan.trainConflicts} train conflict · 2 fewer than current</div>
          <p>{recommendedPlan.note}</p>
          <button className="btn" type="button" disabled={accepted} onClick={acceptRecommended}>
            {accepted ? "Revised plan accepted" : "Accept revised plan"}
          </button>
        </div>
      </div>

      <div className="section">
        <div className="section-head">
          <h2>Track occupancy</h2>
        </div>
        <CorridorDiagram />
      </div>

      <div className="section">
        <div className="section-head">
          <h2>Operating timeline · 05 Sep · 12:00–22:00</h2>
        </div>
        <OpsTimeline />
      </div>

      <div className="panel">
        <div className="panel-pad">
          <div className="section-head">
            <h2>Today’s blocks</h2>
          </div>
          <DataTable
            rows={today}
            rowKey={(r) => r.id}
            onRowClick={(r) => select({ kind: "block", id: r.id })}
            columns={[
              { key: "code", header: "Block ID", mono: true },
              { key: "sectionId", header: "Track", mono: true },
              { key: "corridor", header: "Section" },
              { key: "department", header: "Department" },
              { key: "maintenanceType", header: "Type" },
              {
                key: "window",
                header: "Window",
                render: (r) => (
                  <span className="mono">
                    {r.start}–{r.end}
                  </span>
                ),
              },
              {
                key: "status",
                header: "Status",
                render: (r) => (
                  <span className={`tag ${r.status === "CONFLICT" || r.status === "ACTIVE" ? "red" : r.status === "COMPLETED" ? "green" : "amber"}`}>
                    {r.status}
                  </span>
                ),
              },
              {
                key: "affected",
                header: "Affected trains",
                render: (r) =>
                  r.affectedTrainIds
                    .map((id) => trains.find((t) => t.id === id)?.number ?? id)
                    .join(", ") || "—",
              },
            ]}
          />
        </div>
      </div>
    </>
  );
}
