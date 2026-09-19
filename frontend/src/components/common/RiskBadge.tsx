import React from 'react';
import { RiskLevel } from '../../types/analysis';
import { ShieldAlert, ShieldCheck, AlertTriangle, AlertOctagon } from 'lucide-react';

interface RiskBadgeProps {
  risk: RiskLevel;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({
  risk,
  size = 'md',
  showIcon = true,
}) => {
  const styles: Record<RiskLevel, { bg: string; text: string; border: string; label: string; icon: React.ReactNode }> = {
    low: {
      bg: 'bg-emerald-950/50',
      text: 'text-emerald-400',
      border: 'border-emerald-800/60',
      label: 'Low Risk',
      icon: <ShieldCheck className="w-3.5 h-3.5" />,
    },
    medium: {
      bg: 'bg-amber-950/50',
      text: 'text-amber-400',
      border: 'border-amber-800/60',
      label: 'Medium Risk',
      icon: <AlertTriangle className="w-3.5 h-3.5" />,
    },
    high: {
      bg: 'bg-orange-950/50',
      text: 'text-orange-400',
      border: 'border-orange-800/60',
      label: 'High Risk',
      icon: <ShieldAlert className="w-3.5 h-3.5" />,
    },
    critical: {
      bg: 'bg-rose-950/50',
      text: 'text-rose-400',
      border: 'border-rose-800/60',
      label: 'Critical Risk',
      icon: <AlertOctagon className="w-3.5 h-3.5" />,
    },
  };

  const current = styles[risk] || styles.low;

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5 font-medium',
    lg: 'text-sm px-3 py-1.5 gap-2 font-semibold',
  };

  return (
    <span
      className={`inline-flex items-center rounded-md border tracking-wide uppercase font-mono ${current.bg} ${current.text} ${current.border} ${sizeClasses[size]}`}
    >
      {showIcon && current.icon}
      <span>{current.label}</span>
    </span>
  );
};
