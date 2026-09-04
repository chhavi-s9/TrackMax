import { DataTable } from "../components/DataTable";
import { useOps } from "../state/OpsContext";

function statusClass(status: string): string {
  if (status === "FAILED" || status === "UNDER_MAINTENANCE") return "tag red";
  if (status === "DEGRADED") return "tag amber";
  return "tag green";
}

export function Assets() {
  const { assets, select } = useOps();

  return (
    <div className="panel">
      <div className="panel-pad">
        <div className="section-head">
          <h2>Asset availability</h2>
        </div>
        <DataTable
          rows={assets}
          rowKey={(r) => r.id}
          onRowClick={(r) => select({ kind: "asset", id: r.id })}
          columns={[
            { key: "assetId", header: "Asset ID", mono: true },
            { key: "type", header: "Type" },
            { key: "location", header: "Location" },
            { key: "section", header: "Section", mono: true },
            {
              key: "status",
              header: "Status",
              render: (r) => <span className={statusClass(r.status)}>{r.status.replaceAll("_", " ")}</span>,
            },
            { key: "assignment", header: "Assignment", mono: true },
            { key: "availability", header: "Availability" },
            { key: "department", header: "Dept" },
            {
              key: "condition",
              header: "Cond.",
              mono: true,
              render: (r) => String(r.condition),
            },
          ]}
        />
      </div>
    </div>
  );
}
