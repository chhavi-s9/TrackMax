import { Link, NavLink, Outlet, useLocation } from "react-router-dom";
import { CLOCK, DIVISION, OPERATING_DATE } from "../data/network";
import { useOps } from "../state/OpsContext";
import { Inspector } from "./Inspector";

const NAV = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/planning", label: "Block Planning" },
  { to: "/weather", label: "Weather & Replanning" },
  { to: "/network", label: "Network" },
  { to: "/assets", label: "Assets" },
  { to: "/analytics", label: "Analytics" },
  { to: "/reports", label: "Maintenance Reports" },
  { to: "/alerts", label: "Alerts" },
  { to: "/settings", label: "Settings" },
];

const CRUMBS: Record<string, string> = {
  "/": "Dashboard",
  "/planning": "Block Planning",
  "/weather": "Weather & Replanning",
  "/network": "Network",
  "/assets": "Assets",
  "/analytics": "Analytics",
  "/reports": "Maintenance Reports",
  "/alerts": "Alerts",
  "/settings": "Settings",
};

function Icon({ d }: { d: string }) {
  return (
    <svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.4">
      <path d={d} />
    </svg>
  );
}

const ICONS: Record<string, string> = {
  "/": "M2 8 L8 2 L14 8 M4 7 V14 H7 V10 H9 V14 H12 V7",
  "/planning": "M2 4 H14 M2 8 H14 M2 12 H10 M12 11 V13",
  "/weather": "M3 10 H12 A3 3 0 1 0 9 5 A4 4 0 0 0 3 10 Z",
  "/network": "M2 8 H14 M5 5 V11 M11 5 V11",
  "/assets": "M3 13 V6 L8 3 L13 6 V13 H3 M8 13 V8",
  "/analytics": "M3 12 H13 M5 12 V7 M8 12 V4 M11 12 V9",
  "/reports": "M4 2 H10 L13 5 V14 H4 Z M10 2 V5 H13",
  "/alerts": "M8 2 L14 13 H2 Z M8 6 V9 M8 11 V11.4",
  "/settings": "M3 5 H13 M3 8 H13 M3 11 H13 M6 5 V6 M10 8 V9 M7 11 V12",
};

export function AppShell() {
  const loc = useLocation();
  const { selected, live, metrics } = useOps();
  const hideInspector = loc.pathname.startsWith("/reports/") || loc.pathname === "/settings";
  const reportMatch = loc.pathname.match(/^\/reports\/(.+)$/);
  const pageTitle = reportMatch
    ? reportMatch[1]
    : (CRUMBS[loc.pathname] ?? "RailDoot");

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand__mark">RD</div>
          <div>
            <div className="brand__name">RailDoot</div>
            <div className="brand__sub">Block operations</div>
          </div>
        </div>
        <nav className="nav">
          {NAV.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.end} className={({ isActive }) => (isActive ? "active" : "")}>
              <Icon d={ICONS[item.to]} />
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar__foot">{live ? "API connected" : "Local snapshot"}</div>
      </aside>

      <div className="workspace">
        <header className="topbar">
          <nav className="crumbs" aria-label="Breadcrumb">
            <span>RailDoot</span>
            <span>/</span>
            {reportMatch ? (
              <>
                <Link to="/reports">Maintenance Reports</Link>
                <span>/</span>
                <strong>{reportMatch[1]}</strong>
              </>
            ) : (
              <strong>{pageTitle}</strong>
            )}
          </nav>
          <div className="top-meta">
            <span>
              Division <b>{DIVISION}</b>
            </span>
            <span>
              {OPERATING_DATE} <b>{CLOCK}</b>
            </span>
            <span className={`status-pill ${metrics.divisionStatus === "Normal" ? "ok" : "bad"}`}>
              <i />
              {metrics.divisionStatus}
            </span>
          </div>
        </header>
        <div className={hideInspector || !selected ? "page no-inspect" : "page"}>
          <div className="main">
            <Outlet />
          </div>
          {!hideInspector && selected ? <Inspector /> : null}
        </div>
      </div>
    </div>
  );
}
