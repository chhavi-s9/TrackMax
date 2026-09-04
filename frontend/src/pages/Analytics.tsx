import { Link } from "react-router-dom";
import { DataTable } from "../components/DataTable";
import { useOps } from "../state/OpsContext";

const SCENARIOS = [
  { id: "manual", label: "Manual", hours: 18.4, blocks: 9, conflicts: 6, availability: "82%", disruption: "18%", tasks: 11 },
  { id: "coordinated", label: "Coordinated", hours: 14.1, blocks: 7, conflicts: 2, availability: "88%", disruption: "10%", tasks: 13 },
  { id: "ai", label: "Recommended plan", hours: 11.6, blocks: 5, conflicts: 1, availability: "93%", disruption: "4%", tasks: 14 },
];

export function Analytics() {
  const { metrics, trains, blocks } = useOps();
  const delayed = trains.filter((t) => t.delayMin > 0);

  return (
    <>
      <p className="muted" style={{ marginTop: 0 }}>
        Simulation figures for this operating day. Not measured railway performance.
      </p>

      <div className="panel">
        <div className="panel-pad">
          <div className="section-head">
            <h2>Plan comparison · JP-AII week</h2>
          </div>
          <DataTable
            rows={SCENARIOS}
            rowKey={(r) => r.id}
            columns={[
              { key: "label", header: "Plan" },
              { key: "hours", header: "Block hours", mono: true, render: (r) => String(r.hours) },
              { key: "blocks", header: "Blocks", mono: true, render: (r) => String(r.blocks) },
              { key: "conflicts", header: "Conflicts", mono: true, render: (r) => String(r.conflicts) },
              { key: "availability", header: "Asset availability" },
              { key: "disruption", header: "Train disruption" },
              { key: "tasks", header: "Tasks covered", mono: true, render: (r) => String(r.tasks) },
            ]}
          />
        </div>
      </div>

      <div className="split-2" style={{ marginTop: 12 }}>
        <div className="panel">
          <div className="panel-pad">
            <div className="section-head">
              <h2>Today</h2>
            </div>
            <dl className="kv">
              <dt>Division status</dt>
              <dd>{metrics.divisionStatus}</dd>
              <dt>Active blocks</dt>
              <dd>{metrics.activeBlocks}</dd>
              <dt>Conflicts</dt>
              <dd>{metrics.conflicts}</dd>
              <dt>Trains delayed / held</dt>
              <dd>{delayed.length}</dd>
              <dt>Completed overnight</dt>
              <dd>{blocks.filter((b) => b.status === "COMPLETED").length}</dd>
            </dl>
            <div className="actions">
              <Link className="btn ghost" to="/planning">
                Open planning
              </Link>
              <Link className="btn ghost" to="/reports">
                Open reports
              </Link>
            </div>
          </div>
        </div>
        <div className="panel">
          <div className="panel-pad">
            <div className="section-head">
              <h2>Delay board</h2>
            </div>
            <DataTable
              rows={delayed}
              rowKey={(r) => r.id}
              columns={[
                { key: "number", header: "Train", mono: true },
                { key: "status", header: "Status" },
                { key: "delayMin", header: "Delay", render: (r) => `+${r.delayMin} min` },
                { key: "impact", header: "Cause" },
              ]}
            />
          </div>
        </div>
      </div>
    </>
  );
}
