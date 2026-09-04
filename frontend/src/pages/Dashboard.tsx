import { Link } from "react-router-dom";
import { CorridorDiagram } from "../components/CorridorDiagram";
import { DataTable } from "../components/DataTable";
import { useOps } from "../state/OpsContext";

function tagForBlock(status: string) {
  if (status === "CONFLICT" || status === "ACTIVE") return "tag red";
  if (status === "PLANNED" || status === "APPROVED") return "tag amber";
  return "tag green";
}

function tagForTrain(status: string) {
  if (status === "Delayed" || status === "Held") return "tag amber";
  if (status === "Cancelled") return "tag red";
  return "tag green";
}

export function Dashboard() {
  const { metrics, blocks, trains, alerts, weather, accepted, select } = useOps();
  const active = blocks.filter((b) => b.status !== "COMPLETED");
  const affected = trains.filter((t) => active.some((b) => b.affectedTrainIds.includes(t.id)));
  const recent = blocks.filter((b) => b.status === "COMPLETED");

  return (
    <>
      {weather.type === "HEAVY_RAIN" && !accepted ? (
        <div className="warn">
          <div>
            <strong>Weather may affect planned maintenance</strong>
            <div className="muted">
              Heavy rainfall expected {weather.window} on {weather.section}. {weather.description}.
            </div>
          </div>
          <Link className="btn" to="/weather">
            Review revised plan
          </Link>
        </div>
      ) : null}

      <div className="metrics">
        <div className="metric">
          <span>Active blocks</span>
          <Link to="/planning">
            <b>{metrics.activeBlocks}</b>
          </Link>
        </div>
        <div className="metric">
          <span>Planned blocks</span>
          <Link to="/planning">
            <b>{metrics.plannedBlocks}</b>
          </Link>
        </div>
        <div className="metric">
          <span>Trains on corridor</span>
          <Link to="/network">
            <b>{metrics.trainsOnCorridor}</b>
          </Link>
        </div>
        <div className="metric">
          <span>Affected trains</span>
          <b>{metrics.trainsAffected}</b>
        </div>
        <div className="metric">
          <span>Conflicts</span>
          <Link to="/alerts">
            <b>{metrics.conflicts}</b>
          </Link>
        </div>
        <div className="metric">
          <span>Assets blocked</span>
          <Link to="/assets">
            <b>{metrics.assetsBlocked}</b>
          </Link>
        </div>
        <div className="metric">
          <span>Overdue assets</span>
          <Link to="/assets">
            <b>{metrics.overdueAssets}</b>
          </Link>
        </div>
      </div>

      <div className="section">
        <div className="section-head">
          <h2>Corridor schematic · JP–AII</h2>
          <Link to="/network">Full network</Link>
        </div>
        <CorridorDiagram />
      </div>

      <div className="split">
        <div className="panel">
          <div className="panel-pad">
            <div className="section-head">
              <h2>Active / planned blocks</h2>
              <Link to="/planning">Planning</Link>
            </div>
            <DataTable
              rows={active}
              rowKey={(r) => r.id}
              selectedKey={null}
              onRowClick={(r) => select({ kind: "block", id: r.id })}
              columns={[
                { key: "code", header: "Block", mono: true },
                { key: "sectionId", header: "Track", mono: true },
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
                  render: (r) => <span className={tagForBlock(r.status)}>{r.status}</span>,
                },
              ]}
            />
          </div>
        </div>
        <div className="panel">
          <div className="panel-pad">
            <div className="section-head">
              <h2>Affected trains</h2>
              <Link to="/network">Network</Link>
            </div>
            <DataTable
              rows={affected}
              rowKey={(r) => r.id}
              onRowClick={(r) => select({ kind: "train", id: r.id })}
              columns={[
                { key: "number", header: "Train", mono: true },
                { key: "route", header: "Route" },
                {
                  key: "status",
                  header: "Status",
                  render: (r) => <span className={tagForTrain(r.status)}>{r.status}</span>,
                },
                {
                  key: "delay",
                  header: "Delay",
                  render: (r) => (r.delayMin ? `+${r.delayMin}` : "—"),
                },
              ]}
            />
          </div>
        </div>
        <div className="panel">
          <div className="panel-pad">
            <div className="section-head">
              <h2>Alerts</h2>
              <Link to="/alerts">All alerts</Link>
            </div>
            <DataTable
              rows={alerts.slice(0, 5)}
              rowKey={(r) => r.id}
              onRowClick={(r) => select({ kind: "alert", id: r.id })}
              columns={[
                { key: "time", header: "Time", mono: true },
                { key: "message", header: "Message" },
              ]}
            />
            <div className="section-head" style={{ marginTop: 12 }}>
              <h2>Recent maintenance</h2>
              <Link to="/reports">Reports</Link>
            </div>
            <DataTable
              rows={recent}
              rowKey={(r) => r.id}
              onRowClick={(r) => select({ kind: "block", id: r.id })}
              columns={[
                { key: "code", header: "Block", mono: true },
                {
                  key: "window",
                  header: "Window",
                  render: (r) => `${r.start}–${r.end}`,
                },
              ]}
            />
          </div>
        </div>
      </div>
    </>
  );
}
