import { Link, useParams } from "react-router-dom";
import { useOps } from "../state/OpsContext";

export function ReportDetail() {
  const { reportId } = useParams();
  const { reports } = useOps();
  const r = reports.find((x) => x.id === reportId);

  if (!r) {
    return (
      <p>
        Record not found. <Link to="/reports">Back to list</Link>
      </p>
    );
  }

  return (
    <article className="record">
      <header>
        <div>
          <h1>Maintenance record {r.reportId}</h1>
          <div className="muted">
            {r.section} · {r.blockId} · {r.department}
          </div>
        </div>
        <Link className="btn ghost" to="/reports">
          Back to list
        </Link>
      </header>
      <div className="record-grid">
        <div>
          <span>Report ID</span>
          <b className="mono">{r.reportId}</b>
        </div>
        <div>
          <span>Block ID</span>
          <b className="mono">{r.blockId}</b>
        </div>
        <div>
          <span>Section</span>
          <b>{r.section}</b>
        </div>
        <div>
          <span>Completion</span>
          <b>{r.completion}</b>
        </div>
        <div>
          <span>Maintenance type</span>
          {r.maintenanceType}
        </div>
        <div>
          <span>Department</span>
          {r.department}
        </div>
        <div>
          <span>Planned time</span>
          <span className="mono">{r.planned}</span>
        </div>
        <div>
          <span>Actual time</span>
          <span className="mono">{r.actual}</span>
        </div>
        <div>
          <span>Weather</span>
          {r.weather}
        </div>
        <div>
          <span>Delay</span>
          {r.delay}
        </div>
        <div>
          <span>Assets affected</span>
          <span className="mono">{r.assetsAffected}</span>
        </div>
        <div>
          <span>Trains affected</span>
          {r.trainsAffected}
        </div>
        <div>
          <span>Supervisor</span>
          {r.supervisor}
        </div>
        <div>
          <span>Remarks</span>
          {r.remarks}
        </div>
      </div>
      <div className="panel-pad">
        <div className="panel-title">Analysis</div>
        <p>{r.analysis}</p>
      </div>
    </article>
  );
}
