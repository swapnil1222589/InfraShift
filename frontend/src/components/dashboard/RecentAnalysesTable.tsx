import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Analysis } from '../../types/analysis';
import { RiskBadge } from '../common/RiskBadge';
import { StatusBadge } from '../common/StatusBadge';
import { ConfidenceMeter } from '../common/ConfidenceMeter';
import { GitPullRequest, ExternalLink, Calendar, Layers } from 'lucide-react';

interface RecentAnalysesTableProps {
  analyses: Analysis[];
  isLoading?: boolean;
}

export const RecentAnalysesTable: React.FC<RecentAnalysesTableProps> = ({
  analyses,
  isLoading = false,
}) => {
  const navigate = useNavigate();

  const formatDate = (isoString: string) => {
    const d = new Date(isoString);
    return d.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div id="analyses-table" className="overflow-x-auto">
      <table className="w-full text-left text-xs text-slate-300">
        <thead className="bg-slate-950/80 text-[11px] font-mono uppercase text-slate-400 border-b border-slate-800">
          <tr>
            <th className="py-3 px-4 font-semibold">PR</th>
            <th className="py-3 px-4 font-semibold">Repository</th>
            <th className="py-3 px-4 font-semibold">Changed Component</th>
            <th className="py-3 px-4 font-semibold">Risk</th>
            <th className="py-3 px-4 font-semibold">Cost Impact</th>
            <th className="py-3 px-4 font-semibold">Performance Impact</th>
            <th className="py-3 px-4 font-semibold">Confidence</th>
            <th className="py-3 px-4 font-semibold">Status</th>
            <th className="py-3 px-4 font-semibold text-right">Date</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/60 font-sans">
          {analyses.map((item) => (
            <tr
              key={item.id}
              onClick={() => navigate(`/analyses/${item.id}`)}
              className="hover:bg-slate-800/40 transition cursor-pointer group"
            >
              {/* PR */}
              <td className="py-3.5 px-4 font-medium text-slate-100">
                <div className="flex items-center gap-2">
                  <div className="p-1 rounded bg-slate-800 text-amber-400 group-hover:bg-amber-500/20 transition">
                    <GitPullRequest className="w-3.5 h-3.5" />
                  </div>
                  <div>
                    <span className="font-mono font-bold text-amber-400 group-hover:text-amber-300">
                      #{item.prNumber}
                    </span>
                    <p className="text-[11px] text-slate-400 max-w-[200px] truncate group-hover:text-slate-200">
                      {item.prTitle}
                    </p>
                  </div>
                </div>
              </td>

              {/* Repository */}
              <td className="py-3.5 px-4 font-mono text-[11px] text-slate-400">
                <div className="truncate max-w-[140px]" title={item.repository}>
                  {item.repository.split('/')[1] || item.repository}
                </div>
              </td>

              {/* Changed Component */}
              <td className="py-3.5 px-4 font-mono text-[11px] text-slate-300">
                <div className="flex items-center gap-1.5">
                  <Layers className="w-3 h-3 text-slate-500 shrink-0" />
                  <span className="truncate max-w-[180px]" title={item.changedComponent}>
                    {item.changedComponent}
                  </span>
                </div>
              </td>

              {/* Risk */}
              <td className="py-3.5 px-4">
                <RiskBadge risk={item.risk} size="sm" />
              </td>

              {/* Cost Impact */}
              <td className="py-3.5 px-4 font-mono text-[11px]">
                <span
                  className={
                    item.costImpact.includes('+')
                      ? 'text-orange-400'
                      : item.costImpact.includes('-')
                      ? 'text-emerald-400'
                      : 'text-slate-300'
                  }
                >
                  {item.costImpact}
                </span>
              </td>

              {/* Performance Impact */}
              <td className="py-3.5 px-4 font-mono text-[11px] text-slate-300">
                <span
                  className={
                    item.performanceImpact.includes('-')
                      ? 'text-emerald-400'
                      : item.performanceImpact.includes('+')
                      ? 'text-amber-400'
                      : 'text-slate-300'
                  }
                >
                  {item.performanceImpact}
                </span>
              </td>

              {/* Confidence */}
              <td className="py-3.5 px-4">
                <ConfidenceMeter score={item.confidence} size="sm" showLabel={false} />
              </td>

              {/* Status */}
              <td className="py-3.5 px-4">
                <StatusBadge status={item.status} size="sm" />
              </td>

              {/* Date */}
              <td className="py-3.5 px-4 text-right font-mono text-[10px] text-slate-500 whitespace-nowrap">
                {formatDate(item.createdAt)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
