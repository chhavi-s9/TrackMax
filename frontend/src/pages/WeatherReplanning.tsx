import { useState } from "react";
import { requestReschedule } from "../api/client";
import { OPERATING_DATE } from "../data/network";
import { OpsTimeline } from "../components/OpsTimeline";
import { useOps } from "../state/OpsContext";
import type { WeatherKind } from "../types";

const OPTIONS: WeatherKind[] = ["NORMAL", "HEAVY_RAIN", "HEATWAVE", "FOG", "THUNDERSTORM"];

export function WeatherReplanning() {
  const { weather, setWeatherType, currentPlan, recommendedPlan, accepted, acceptRecommended, live } = useOps();
  const [section, setSection] = useState("JP-AII");
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState<string | null>(null);

  async function run() {
    setBusy(true);
    setNote(null);
    const result = await requestReschedule(section, weather.type, OPERATING_DATE);
    setBusy(false);
    if (result?.reason) {
      setNote(result.reason);
    } else if (!live) {
      setNote("Planner used the local snapshot. Recommended window is 16:30–20:30 after the rain cell.");
    } else {
      setNote("No reschedule payload returned. Recommended window below is still valid for this snapshot.");
    }
  }

  return (
    <>
      <div className="form-row">
        <div className="field">
          <label htmlFor="wx-section">Section</label>
          <select id="wx-section" value={section} onChange={(e) => setSection(e.target.value)}>
            <option>JP-AII</option>
            <option>JP-BKI</option>
            <option>AII-MJ</option>
            <option>JP-GAD</option>
          </select>
        </div>
        <div className="field">
          <label htmlFor="wx-type">Condition</label>
          <select id="wx-type" value={weather.type} onChange={(e) => setWeatherType(e.target.value as WeatherKind)}>
            {OPTIONS.map((o) => (
              <option key={o}>{o}</option>
            ))}
          </select>
        </div>
        <button className="btn" type="button" onClick={run} disabled={busy}>
          {busy ? "Running…" : "Re-rank and reschedule"}
        </button>
      </div>

      {weather.type === "HEAVY_RAIN" ? (
        <div className="warn">
          <div>
            <strong>Weather may affect planned maintenance</strong>
            <div className="muted">
              Heavy rainfall expected {weather.window} on {weather.section}. Rain {weather.rainfall} mm · vis {weather.visibility} km.
            </div>
          </div>
        </div>
      ) : null}

      <div className="plan-compare">
        <div className="plan">
          <h3>Current plan</h3>
          <div className="when">
            {currentPlan.start}–{currentPlan.end}
          </div>
          <div>Weather risk: {currentPlan.weatherRisk}</div>
          <div>{currentPlan.trainConflicts} train conflicts</div>
          <p className="muted">{currentPlan.note}</p>
        </div>
        <div className="plan rec">
          <h3>Recommended</h3>
          <div className="when">
            {recommendedPlan.start}–{recommendedPlan.end}
          </div>
          <div>Weather risk: {recommendedPlan.weatherRisk}</div>
          <div>{recommendedPlan.trainConflicts} train conflict · 2 fewer than current</div>
          <p className="muted">{recommendedPlan.note}</p>
          <button className="btn" type="button" disabled={accepted} onClick={acceptRecommended}>
            {accepted ? "Revised plan accepted" : "Accept revised plan"}
          </button>
        </div>
      </div>

      {note ? <p className="muted">{note}</p> : null}

      <div className="section">
        <div className="section-head">
          <h2>Window against train movement</h2>
        </div>
        <OpsTimeline />
      </div>
    </>
  );
}
