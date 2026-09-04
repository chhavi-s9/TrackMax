import { useNavigate } from "react-router-dom";
import { DataTable } from "../components/DataTable";
import { useOps } from "../state/OpsContext";

export function Reports() {
  const { reports, select } = useOps();
  const nav = useNavigate();

  return (
    <div className="panel">
      <div className="panel-pad">
        <div className="section-head">
          <h2>Maintenance reports</h2>
        </div>
        <DataTable
          rows={reports}
          rowKey={(r) => r.id}
          onRowClick={(r) => {
            select({ kind: "report", id: r.id });
            nav(`/reports/${r.id}`);
          }}
          columns={[
            { key: "reportId", header: "Report ID", mono: true },
            { key: "blockId", header: "Block ID", mono: true },
            { key: "section", header: "Section" },
            { key: "maintenanceType", header: "Type" },
            { key: "planned", header: "Planned" },
            { key: "actual", header: "Actual" },
            { key: "weather", header: "Weather" },
            { key: "assetsAffected", header: "Assets" },
            { key: "trainsAffected", header: "Trains" },
            { key: "delay", header: "Delay" },
            {
              key: "completion",
              header: "Status",
              render: (r) => (
                <span className={`tag ${r.completion === "COMPLETED" ? "green" : r.completion === "IN PROGRESS" ? "amber" : "red"}`}>
                  {r.completion}
                </span>
              ),
            },
          ]}
        />
      </div>
    </div>
  );
}
