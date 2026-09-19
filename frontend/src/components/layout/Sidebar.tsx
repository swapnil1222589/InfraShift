import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  GitPullRequest,
  Network,
  TrendingUp,
  History,
  Settings,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  Activity,
  Layers,
  Sparkles,
} from 'lucide-react';

interface SidebarProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggleCollapse }) => {
  const navItems = [
    {
      to: '/dashboard',
      label: 'Dashboard',
      icon: LayoutDashboard,
    },
    {
      to: '/analyses',
      label: 'PR Analyses',
      icon: GitPullRequest,
      badge: '6',
    },
    {
      to: '/analyses/analysis-pr-248/impact',
      label: 'Impact Graph',
      icon: Network,
    },
    {
      to: '/analyses/analysis-pr-248/forecast',
      label: 'Forecasts',
      icon: TrendingUp,
    },
    {
      to: '/history',
      label: 'History',
      icon: History,
    },
    {
      to: '/settings',
      label: 'Settings',
      icon: Settings,
    },
  ];

  return (
    <aside
      className={`border-r border-slate-800 bg-slate-950 flex flex-col justify-between shrink-0 select-none transition-all duration-200 z-30 ${
        collapsed ? 'w-16' : 'w-60'
      }`}
    >
      <div className="py-4">
        {/* Navigation Category Header */}
        {!collapsed && (
          <div className="px-4 mb-3 flex items-center justify-between">
            <span className="text-[10px] font-mono uppercase tracking-wider text-slate-500 font-semibold">
              Platform Navigation
            </span>
          </div>
        )}

        <nav className="space-y-1 px-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center ${
                    collapsed ? 'justify-center py-2.5 px-2' : 'justify-between px-3 py-2'
                  } rounded-md text-xs font-medium transition-all group ${
                    isActive
                      ? 'bg-amber-500/15 text-amber-400 border border-amber-500/30 font-semibold'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/80 border border-transparent'
                  }`
                }
                title={collapsed ? item.label : undefined}
              >
                <div className="flex items-center gap-2.5 min-w-0">
                  <Icon className="w-4 h-4 shrink-0 transition-colors" />
                  {!collapsed && <span className="truncate">{item.label}</span>}
                </div>
                {!collapsed && item.badge && (
                  <span className="px-1.5 py-0.2 text-[10px] font-mono bg-slate-800 text-slate-300 rounded border border-slate-700">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Demo PR Quick Jump */}
        {!collapsed && (
          <div className="mt-8 px-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-mono uppercase tracking-wider text-slate-500 font-semibold">
                Hackathon Demo PR
              </span>
              <span className="w-1.5 h-1.5 rounded-full bg-orange-400 animate-pulse" />
            </div>
            <div className="p-3 rounded-lg bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-amber-400 font-mono">PR #248</span>
                <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-orange-950 text-orange-400 border border-orange-800">
                  High Risk
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mt-1 line-clamp-2 leading-snug">
                Optimize order processing database queries
              </p>
              <NavLink
                to="/analyses/analysis-pr-248"
                className="mt-2.5 inline-flex items-center gap-1 text-[11px] text-amber-400 hover:text-amber-300 font-medium font-mono"
              >
                <span>Open Analysis</span>
                <span>→</span>
              </NavLink>
            </div>
          </div>
        )}
      </div>

      {/* Footer: Telemetry status + collapse toggle */}
      <div className="p-2 border-t border-slate-800/80">
        {!collapsed && (
          <div className="p-2.5 mb-2 rounded-lg bg-slate-900/50 border border-slate-800/80 text-[11px]">
            <div className="flex items-center justify-between text-slate-400 mb-1">
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="font-mono text-[10px] text-slate-300 font-medium">CloudWatch Sync</span>
              </div>
              <span className="text-[10px] font-mono text-emerald-400 font-semibold">LIVE</span>
            </div>
            <div className="text-[10px] text-slate-500 font-mono flex items-center justify-between">
              <span>Region:</span>
              <span className="text-slate-300">us-east-1</span>
            </div>
          </div>
        )}

        {/* Toggle Collapse Button */}
        <button
          onClick={onToggleCollapse}
          className={`w-full flex items-center ${
            collapsed ? 'justify-center' : 'justify-between px-3'
          } py-2 rounded-md hover:bg-slate-900 text-slate-400 hover:text-slate-200 transition text-xs font-mono`}
          title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
        >
          {!collapsed && <span>Collapse Navigation</span>}
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>
    </aside>
  );
};
