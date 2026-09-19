import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  headerAction?: React.ReactNode;
  badge?: React.ReactNode;
  noPadding?: boolean;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  title,
  subtitle,
  headerAction,
  badge,
  noPadding = false,
}) => {
  return (
    <div
      className={`bg-slate-900/90 border border-slate-800 rounded-lg shadow-sm backdrop-blur-sm transition-colors duration-150 ${className}`}
    >
      {(title || subtitle || headerAction || badge) && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between px-5 py-4 border-b border-slate-800/80 gap-2">
          <div className="flex items-center gap-3">
            {badge}
            <div>
              {title && <h3 className="text-sm font-semibold text-slate-100 tracking-tight">{title}</h3>}
              {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
            </div>
          </div>
          {headerAction && <div className="flex items-center gap-2">{headerAction}</div>}
        </div>
      )}
      <div className={noPadding ? '' : 'p-5'}>{children}</div>
    </div>
  );
};
