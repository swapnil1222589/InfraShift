import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

export const Breadcrumbs: React.FC<{ extraItems?: { label: string; to?: string }[] }> = ({ extraItems }) => {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter((x) => x);

  const getLabel = (segment: string) => {
    if (segment === 'dashboard') return 'Dashboard';
    if (segment === 'analyses') return 'PR Analyses';
    if (segment === 'impact-graph') return 'Impact Graph';
    if (segment === 'forecasts') return 'Forecasts';
    if (segment === 'history') return 'History';
    if (segment === 'settings') return 'Settings';
    if (segment === 'analysis-pr-248' || segment === '248') return 'PR #248';
    if (segment.startsWith('analysis-pr-')) return `PR #${segment.replace('analysis-pr-', '')}`;
    if (segment === 'impact') return 'Impact Graph';
    if (segment === 'forecast') return 'Forecast';
    if (segment === 'evidence') return 'Evidence';
    if (segment === 'recommendations') return 'Recommendations';
    return segment;
  };

  return (
    <nav className="flex items-center space-x-1.5 text-xs text-slate-400 mb-3" aria-label="Breadcrumb">
      <Link to="/dashboard" className="flex items-center gap-1 hover:text-slate-200 transition-colors">
        <Home className="w-3.5 h-3.5 text-slate-500" />
        <span className="hidden sm:inline">InfraShift</span>
      </Link>

      {pathnames.map((segment, index) => {
        const to = `/${pathnames.slice(0, index + 1).join('/')}`;
        const isLast = index === pathnames.length - 1 && !extraItems?.length;
        const label = getLabel(segment);

        return (
          <React.Fragment key={to}>
            <ChevronRight className="w-3.5 h-3.5 text-slate-600 shrink-0" />
            {isLast ? (
              <span className="font-medium text-slate-200 font-mono">{label}</span>
            ) : (
              <Link to={to} className="hover:text-slate-200 transition-colors">
                {label}
              </Link>
            )}
          </React.Fragment>
        );
      })}

      {extraItems?.map((item, i) => (
        <React.Fragment key={i}>
          <ChevronRight className="w-3.5 h-3.5 text-slate-600 shrink-0" />
          {item.to ? (
            <Link to={item.to} className="hover:text-slate-200 transition-colors">
              {item.label}
            </Link>
          ) : (
            <span className="font-medium text-slate-200 font-mono">{item.label}</span>
          )}
        </React.Fragment>
      ))}
    </nav>
  );
};
