import React from 'react';
import { NavLink, useParams } from 'react-router-dom';
import {
  FileCode,
  Network,
  TrendingUp,
  FileQuestion,
  ShieldCheck,
  CheckCircle2,
} from 'lucide-react';

interface TabNavProps {
  activeTab?: string;
  onTabChange?: (tab: string) => void;
  recommendationsCount?: number;
}

export const TabNav: React.FC<TabNavProps> = ({
  activeTab,
  onTabChange,
  recommendationsCount = 3,
}) => {
  const { id = 'analysis-pr-248' } = useParams<{ id: string }>();

  const tabs = [
    {
      id: 'overview',
      label: 'Change Summary',
      icon: FileCode,
      to: `/analyses/${id}`,
      end: true,
    },
    {
      id: 'impact',
      label: 'AWS Impact Graph',
      icon: Network,
      to: `/analyses/${id}/impact`,
    },
    {
      id: 'forecast',
      label: 'Cost & Perf Forecast',
      icon: TrendingUp,
      to: `/analyses/${id}/forecast`,
    },
    {
      id: 'evidence',
      label: 'Why This Forecast?',
      icon: FileQuestion,
      to: `/analyses/${id}/evidence`,
    },
    {
      id: 'recommendations',
      label: 'Recommendations & Decision',
      icon: ShieldCheck,
      to: `/analyses/${id}/recommendations`,
      badge: recommendationsCount.toString(),
    },
  ];

  return (
    <div className="border-b border-slate-800 bg-slate-950/70 -mx-4 md:-mx-6 px-4 md:px-6 pt-2 overflow-x-auto scrollbar-none w-[calc(100%+2rem)] md:w-[calc(100%+3rem)] max-w-none">
      <div className="flex space-x-2 min-w-max pb-px">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <NavLink
              key={tab.id}
              to={tab.to}
              end={tab.end}
              className={({ isActive }) =>
                `flex items-center gap-2 px-4 py-3 text-[13px] font-medium border-b-2 transition-all select-none ${
                  isActive
                    ? 'border-amber-500 text-amber-400 bg-amber-500/10'
                    : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700 hover:bg-slate-900/50'
                }`
              }
            >
              <Icon className="w-3.5 h-3.5 shrink-0" />
              <span>{tab.label}</span>
              {tab.badge && (
                <span className="ml-1 px-1.5 py-0.2 text-[10px] font-mono rounded bg-amber-500/20 text-amber-300 font-semibold border border-amber-500/30">
                  {tab.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </div>
    </div>
  );
};
