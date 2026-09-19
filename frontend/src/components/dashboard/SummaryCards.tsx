import React from 'react';
import { GitPullRequest, Gauge, DollarSign, AlertTriangle, ArrowUpRight, TrendingUp } from 'lucide-react';
import { Card } from '../common/Card';

interface SummaryCardsProps {
  analysesCount?: number;
  avgConfidence?: number;
  costImpactRange?: string;
  highRiskCount?: number;
}

export const SummaryCards: React.FC<SummaryCardsProps> = ({
  analysesCount = 34,
  avgConfidence = 89,
  costImpactRange = '+$180 – $320/mo',
  highRiskCount = 3,
}) => {
  const cards = [
    {
      title: 'Analyses This Week',
      value: analysesCount.toString(),
      subtext: '+8 PRs vs previous 7 days',
      icon: GitPullRequest,
      iconColor: 'text-amber-400',
      iconBg: 'bg-amber-500/10 border-amber-500/20',
      metricDelta: '+30.7%',
      positive: true,
    },
    {
      title: 'Average Confidence',
      value: `${avgConfidence}%`,
      subtext: 'High statistical correlation',
      icon: Gauge,
      iconColor: 'text-emerald-400',
      iconBg: 'bg-emerald-500/10 border-emerald-500/20',
      metricDelta: '≥ 80% threshold',
      positive: true,
    },
    {
      title: 'Potential Cost Impact',
      value: costImpactRange,
      subtext: 'Projected net AWS billing delta',
      icon: DollarSign,
      iconColor: 'text-sky-400',
      iconBg: 'bg-sky-500/10 border-sky-500/20',
      metricDelta: '5 PRs monitored',
      positive: false,
    },
    {
      title: 'High Risk Changes',
      value: highRiskCount.toString(),
      subtext: 'Requires load test or pre-warming',
      icon: AlertTriangle,
      iconColor: 'text-orange-400',
      iconBg: 'bg-orange-500/10 border-orange-500/20',
      metricDelta: 'Action required',
      positive: false,
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((c, i) => {
        const Icon = c.icon;
        return (
          <Card key={i} className="hover:border-slate-700/80 transition-all">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-medium text-slate-400 tracking-wide uppercase font-mono">
                  {c.title}
                </p>
                <div className="mt-2 text-2xl font-bold text-slate-100 font-sans tracking-tight">
                  {c.value}
                </div>
              </div>
              <div className={`p-2.5 rounded-lg border ${c.iconBg}`}>
                <Icon className={`w-5 h-5 ${c.iconColor}`} />
              </div>
            </div>

            <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
              <span className="text-slate-500">{c.subtext}</span>
              <span
                className={`font-mono text-[11px] font-medium ${
                  c.positive ? 'text-emerald-400' : 'text-amber-400'
                }`}
              >
                {c.metricDelta}
              </span>
            </div>
          </Card>
        );
      })}
    </div>
  );
};
