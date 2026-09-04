import { CorridorDiagram } from "../components/CorridorDiagram";
import { DataTable } from "../components/DataTable";
import { SECTIONS, STATIONS } from "../data/network";
import { useOps } from "../state/OpsContext";

export function Network() {
  const { trains, blocks, select } = useOps();

  return (
    <>
      <div className="section">
        <div className="section-head">
          <h2>Jaipur division schematic</h2>
        </div>
        <CorridorDiagram />
      </div>

      <div className="split-2">
        <div className="panel">
          <div className="panel-pad">
            <div className="section-head">
              <h2>Stations</h2>
            </div>
            <DataTable
              rows={STATIONS}
              rowKey={(r) => r.code}
              onRowClick={(r) => select({ kind: "station", id: r.code })}
              columns={[
                { key: "code", header: "Code", mono: true },
                { key: "name", header: "Station" },
                { key: "km", header: "Km", mono: true },
              ]}
            />
          </div>
        </div>
        <div className="panel">
          <div className="panel-pad">
            <div className="section-head">
              <h2>Track sections</h2>
            </div>
            <DataTable
              rows={SECTIONS}
              rowKey={(r) => r.id}
              onRowClick={(r) => select({ kind: "section", id: r.id })}
              columns={[
                { key: "id", header: "Track", mono: true },
                { key: "corridor", header: "Corridor" },
                { key: "label", header: "Move" },
                {
                  key: "occ",
                  header: "Occupancy",
                  render: (r) => {
                    const blk = blocks.find((b) => b.sectionId === r.id && b.status !== "COMPLETED");
                    const tr = trains.find((t) => t.sectionId === r.id);
                    if (blk?.status === "CONFLICT" || blk?.status === "ACTIVE") return <span className="tag red">{blk.status}</span>;
                    if (blk) return <span className="tag amber">{blk.status}</span>;
                    if (tr) return <span className="tag blue">{tr.number}</span>;
                    return <span className="tag green">Clear</span>;
                  },
                },
              ]}
            />
          </div>
        </div>
      </div>

      <div className="panel" style={{ marginTop: 12 }}>
        <div className="panel-pad">
          <div className="section-head">
            <h2>Train movement</h2>
          </div>
          <DataTable
            rows={trains}
            rowKey={(r) => r.id}
            onRowClick={(r) => select({ kind: "train", id: r.id })}
            columns={[
              { key: "number", header: "Train", mono: true },
              { key: "name", header: "Name" },
              { key: "route", header: "Route" },
              {
                key: "pos",
                header: "Current section",
                render: (r) => `${r.from} → ${r.to}`,
              },
              { key: "status", header: "Status" },
              {
                key: "delay",
                header: "Delay",
                render: (r) => (r.delayMin ? `+${r.delayMin} min` : "—"),
              },
              {
                key: "impact",
                header: "Impact",
              },
              {
                key: "action",
                header: "Action",
                render: () => <span className="linkish">Details</span>,
              },
            ]}
          />
        </div>
      </div>
    </>
  );
}
