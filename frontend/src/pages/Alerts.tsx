import { useNavigate } from "react-router-dom";
import { DataTable } from "../components/DataTable";
import { useOps } from "../state/OpsContext";

export function Alerts() {
  const { alerts, select } = useOps();
  const nav = useNavigate();

  return (
    <div className="panel">
      <div className="panel-pad">
        <div className="section-head">
          <h2>Operating alerts</h2>
        </div>
        <DataTable
          rows={alerts}
          rowKey={(r) => r.id}
          onRowClick={(r) => {
            select({ kind: "alert", id: r.id });
            nav(r.actionTo);
          }}
          columns={[
            { key: "time", header: "Time", mono: true },
            {
              key: "severity",
              header: "Sev.",
              render: (r) => (
                <span className={`tag ${r.severity === "critical" ? "red" : r.severity === "warning" ? "amber" : "blue"}`}>
                  {r.severity}
                </span>
              ),
            },
            { key: "location", header: "Location", mono: true },
            { key: "message", header: "Message" },
            { key: "actionLabel", header: "Action" },
          ]}
        />
      </div>
    </div>
  );
}
