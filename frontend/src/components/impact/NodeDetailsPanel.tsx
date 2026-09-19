import React from 'react';
import { Link, useParams } from 'react-router-dom';
import { ImpactNode } from '../../types/impact';
import { Card } from '../common/Card';
import { StatusBadge } from '../common/StatusBadge';
import { RiskBadge } from '../common/RiskBadge';
import {
  Layers,
  Server,
  Cpu,
  Database,
  Radio,
  ExternalLink,
  ShieldCheck,
  Activity,
  AlertTriangle,
  Info,
} from 'lucide-react';

interface NodeDetailsPanelProps {
  node: ImpactNode | null;
}

export const NodeDetailsPanel: React.FC<NodeDetailsPanelProps> = ({ node }) => {
  const { id } = useParams<{ id: string }>();

  if (!node) {
    return (
      <Card title="Node Inspection" subtitle="Select any graph element to inspect AWS telemetry">
        <div className="py-12 text-center text-slate-500 text-xs">
          <Layers className="w-8 h-8 text-slate-700 mx-auto mb-2" />
          <p>Click any node in the AWS dependency graph to inspect its telemetry and expected blast radius.</p>
        </div>
      </Card>
    );
  }

  const impactColorMap = {
    none: 'text-slate-400 bg-slate-800/40 border-slate-700',
    low: 'text-emerald-400 bg-emerald-950/40 border-emerald-800',
    moderate: 'text-amber-400 bg-amber-950/40 border-amber-800',
    high: 'text-orange-400 bg-orange-950/40 border-orange-800',
    critical: 'text-rose-400 bg-rose-950/40 border-rose-800',
  };

  return (
    <Card
      title="Node Telemetry & Evidence"
      subtitle="Correlated AWS CloudWatch metrics & configuration"
      badge={<Info className="w-4 h-4 text-amber-400" />}
      headerAction={<StatusBadge status={node.status} size="sm" />}
    >
      <div className="space-y-4 text-xs">
        {/* Resource Header */}
        <div className="p-3.5 rounded-lg bg-slate-950 border border-slate-800">
          <span className="text-[10px] font-mono text-slate-500 uppercase block">Selected Resource</span>
          <div className="text-sm font-bold font-mono text-amber-400 mt-1 break-all">
            {node.label}
          </div>
          <div className="flex flex-wrap items-center gap-2 mt-2 pt-2 border-t border-slate-800/80 font-mono text-[11px]">
            <span className="px-2 py-0.5 rounded bg-slate-900 text-slate-300 border border-slate-800">
              {node.awsService}
            </span>
            <span className="text-slate-500">
              {node.region || 'us-east-1'}
            </span>
            <span className={`px-2 py-0.5 rounded border uppercase text-[10px] font-semibold ${impactColorMap[node.impactLevel]}`}>
              {node.impactLevel} impact
            </span>
          </div>
        </div>

        {/* Current Utilization */}
        <div>
          <span className="text-[10px] font-mono uppercase text-slate-400 font-semibold block mb-1.5">
            CURRENT BASELINE UTILIZATION
          </span>
          <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 font-mono text-slate-200">
            {node.metrics?.currentUtilization || 'Nominal baseline telemetry'}
          </div>
        </div>

        {/* Expected Pre-Deployment Impact */}
        <div>
          <span className="text-[10px] font-mono uppercase text-slate-400 font-semibold block mb-1.5">
            EXPECTED PRE-DEPLOYMENT IMPACT
          </span>
          <div className="p-3 rounded-lg bg-amber-950/20 border border-amber-900/50 text-amber-300 font-medium leading-relaxed">
            {node.metrics?.expectedImpact}
          </div>
        </div>

        {/* Evidence Summary */}
        <div>
          <span className="text-[10px] font-mono uppercase text-slate-400 font-semibold block mb-1.5">
            CORRELATED HISTORICAL & AST EVIDENCE
          </span>
          <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 text-slate-300 leading-relaxed">
            {node.evidenceSummary}
          </div>
        </div>

        {/* Capacity / Concurrency if present */}
        {node.metrics?.throughputOrConcurrency && (
          <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between font-mono text-[11px]">
            <span className="text-slate-500 uppercase text-[10px]">Configured Limits:</span>
            <span className="text-slate-300 font-medium">
              {node.metrics.throughputOrConcurrency}
            </span>
          </div>
        )}

        <div className="pt-4 grid grid-cols-2 gap-3">
          <Link
            to={`/analyses/${id}/forecast`}
            className="inline-flex justify-center items-center gap-1.5 px-3 py-1.5 text-[11px] font-medium text-amber-400 bg-amber-500/10 border border-amber-500/20 rounded hover:bg-amber-500/20 transition-colors"
          >
            <Activity className="w-3 h-3" />
            View Forecast
          </Link>
          <Link
            to={`/analyses/${id}/evidence`}
            className="inline-flex justify-center items-center gap-1.5 px-3 py-1.5 text-[11px] font-medium text-indigo-400 bg-indigo-500/10 border border-indigo-500/20 rounded hover:bg-indigo-500/20 transition-colors"
          >
            <ShieldCheck className="w-3 h-3" />
            View Evidence
          </Link>
        </div>
      </div>
    </Card>
  );
};
