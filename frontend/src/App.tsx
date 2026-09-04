import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "./components/AppShell";
import { Alerts } from "./pages/Alerts";
import { Analytics } from "./pages/Analytics";
import { Assets } from "./pages/Assets";
import { BlockPlanning } from "./pages/BlockPlanning";
import { Dashboard } from "./pages/Dashboard";
import { Network } from "./pages/Network";
import { ReportDetail } from "./pages/ReportDetail";
import { Reports } from "./pages/Reports";
import { Settings } from "./pages/Settings";
import { WeatherReplanning } from "./pages/WeatherReplanning";
import { OpsProvider } from "./state/OpsContext";

export default function App() {
  return (
    <OpsProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<AppShell />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/planning" element={<BlockPlanning />} />
            <Route path="/weather" element={<WeatherReplanning />} />
            <Route path="/network" element={<Network />} />
            <Route path="/assets" element={<Assets />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/reports/:reportId" element={<ReportDetail />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </OpsProvider>
  );
}
