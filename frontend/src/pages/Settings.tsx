import { CLOCK, DIVISION, OPERATING_DATE } from "../data/network";
import { useOps } from "../state/OpsContext";

export function Settings() {
  const { live } = useOps();

  return (
    <div className="panel">
      <div className="panel-pad">
        <div className="section-head">
          <h2>Workspace</h2>
        </div>
        <dl className="settings-grid">
          <dt>Application</dt>
          <dd>RailDoot block operations</dd>
          <dt>Division</dt>
          <dd>{DIVISION}</dd>
          <dt>Operating date</dt>
          <dd className="mono">
            {OPERATING_DATE} {CLOCK}
          </dd>
          <dt>Data source</dt>
          <dd>{live ? "Backend API on :8000, with corridor snapshot overlay" : "Local corridor snapshot (API not connected)"}</dd>
          <dt>Units</dt>
          <dd>km, km/h, 24-hour clock</dd>
          <dt>Display</dt>
          <dd>Dark operations theme — status colour only</dd>
          <dt>Note</dt>
          <dd className="muted">Synthetic / demonstration data. Not live Indian Railways traffic.</dd>
        </dl>
      </div>
    </div>
  );
}
