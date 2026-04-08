import { ReactNode } from "react";
import { NavLink } from "react-router-dom";

const NAV = [
  { to: "/", label: "Home" },
  { to: "/attribution", label: "Attribution" },
  { to: "/channels", label: "Channel Performance" },
  { to: "/paths", label: "Conversion Paths" },
  { to: "/incrementality", label: "Incrementality" },
  { to: "/unified", label: "Unified Measurement" },
  { to: "/campaigns", label: "Campaign Explorer" },
  { to: "/planner", label: "Campaign Planner" },
  { to: "/ask", label: "Ask Cortex" },
];

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="flex h-screen overflow-hidden">
      <aside className="w-56 flex-shrink-0 bg-sf-dark text-white flex flex-col">
        <div className="p-5 border-b border-white/10">
          <h1 className="text-lg font-bold tracking-tight">MTA Dashboard</h1>
          <p className="text-xs text-sf-blue mt-1">Multi-Touch Attribution</p>
        </div>
        <nav className="flex-1 py-3 overflow-y-auto">
          {NAV.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.to === "/"}
              className={({ isActive }) =>
                `block px-5 py-2.5 text-sm transition-colors ${
                  isActive
                    ? "bg-sf-blue/20 text-sf-blue border-r-2 border-sf-blue font-medium"
                    : "text-gray-300 hover:bg-white/5 hover:text-white"
                }`
              }
            >
              {n.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-white/10 text-xs text-gray-500">
          Powered by Snowflake
        </div>
      </aside>
      <main className="flex-1 overflow-y-auto bg-gray-50 p-6">{children}</main>
    </div>
  );
}
