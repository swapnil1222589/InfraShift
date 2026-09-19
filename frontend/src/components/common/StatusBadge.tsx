import React from 'react';
import { AnalysisStatus } from '../../types/analysis';
import { CheckCircle2, Clock, AlertCircle, RefreshCw, XCircle, AlertTriangle, FileCode } from 'lucide-react';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const map: Record<string, { bg: string; text: string; dot: string; label: string; icon: React.ReactNode }> = {
    completed: {
      bg: 'bg-emerald-500/10',
      text: 'text-emerald-400',
      dot: 'bg-emerald-500',
      label: 'Completed',
      icon: <CheckCircle2 className="w-3.5 h-3.5" />,
    },
    analyzing: {
      bg: 'bg-cyan-500/10',
      text: 'text-cyan-400',
      dot: 'bg-cyan-400 animate-pulse',
      label: 'Analyzing',
      icon: <RefreshCw className="w-3.5 h-3.5 animate-spin" />,
    },
    flagged: {
      bg: 'bg-rose-500/10',
      text: 'text-rose-400',
      dot: 'bg-rose-500',
      label: 'Flagged',
      icon: <AlertCircle className="w-3.5 h-3.5" />,
    },
    queued: {
      bg: 'bg-slate-500/10',
      text: 'text-slate-400',
      dot: 'bg-slate-400',
      label: 'Queued',
      icon: <Clock className="w-3.5 h-3.5" />,
    },
    failed: {
      bg: 'bg-red-500/10',
      text: 'text-red-400',
      dot: 'bg-red-500',
      label: 'Failed',
      icon: <XCircle className="w-3.5 h-3.5" />,
    },
    healthy: {
      bg: 'bg-emerald-500/10',
      text: 'text-emerald-400',
      dot: 'bg-emerald-500',
      label: 'Healthy',
      icon: <CheckCircle2 className="w-3.5 h-3.5" />,
    },
    stabilized: {
      bg: 'bg-emerald-500/10',
      text: 'text-emerald-400',
      dot: 'bg-emerald-500',
      label: 'Stabilized',
      icon: <CheckCircle2 className="w-3.5 h-3.5" />,
    },
    at_risk: {
      bg: 'bg-orange-500/10',
      text: 'text-orange-400',
      dot: 'bg-orange-500',
      label: 'At Risk',
      icon: <AlertTriangle className="w-3.5 h-3.5" />,
    },
    modified: {
      bg: 'bg-amber-500/10',
      text: 'text-amber-400',
      dot: 'bg-amber-400',
      label: 'Modified',
      icon: <FileCode className="w-3.5 h-3.5" />,
    },
    degraded: {
      bg: 'bg-rose-500/10',
      text: 'text-rose-400',
      dot: 'bg-rose-500',
      label: 'Degraded',
      icon: <AlertCircle className="w-3.5 h-3.5" />,
    },
    verified: {
      bg: 'bg-sky-500/10',
      text: 'text-sky-400',
      dot: 'bg-sky-500',
      label: 'Verified',
      icon: <CheckCircle2 className="w-3.5 h-3.5" />,
    },
    monitoring: {
      bg: 'bg-amber-500/10',
      text: 'text-amber-400',
      dot: 'bg-amber-400 animate-pulse',
      label: 'Monitoring',
      icon: <Clock className="w-3.5 h-3.5" />,
    },
    investigating: {
      bg: 'bg-amber-500/10',
      text: 'text-amber-400',
      dot: 'bg-amber-400',
      label: 'Investigating',
      icon: <AlertTriangle className="w-3.5 h-3.5" />,
    },
    discrepancy_flagged: {
      bg: 'bg-rose-500/10',
      text: 'text-rose-400',
      dot: 'bg-rose-500',
      label: 'Discrepancy Flagged',
      icon: <AlertCircle className="w-3.5 h-3.5" />,
    },
    active: {
      bg: 'bg-emerald-500/10',
      text: 'text-emerald-400',
      dot: 'bg-emerald-400',
      label: 'Active',
      icon: <CheckCircle2 className="w-3.5 h-3.5" />,
    },
  };

  const item = map[status] || {
    bg: 'bg-slate-800/50',
    text: 'text-slate-300',
    dot: 'bg-slate-400',
    label: status.replace('_', ' '),
    icon: <CheckCircle2 className="w-3.5 h-3.5" />,
  };
  const padding = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full border border-slate-800 font-medium ${item.bg} ${item.text} ${padding}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${item.dot}`} />
      <span>{item.label}</span>
    </span>
  );
};
