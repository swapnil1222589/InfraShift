import React, { useState } from 'react';
import { mockImpactPR248 } from '../mock/impact';
import { ImpactNode } from '../types/impact';
import { Card } from '../components/common/Card';
import { RiskBadge } from '../components/common/RiskBadge';
import { StatusBadge } from '../components/common/StatusBadge';
import {
  Layers,
  GitPullRequest,
  Code2,
  Cpu,
  Database,
  Radio,
  ArrowRight,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Info,
} from 'lucide-react';

export const ImpactGraph: React.FC = () => {
  const data = mockImpactPR248;
  const [selectedNode, setSelectedNode] = useState<ImpactNode>(data.nodes[4]); // default to DynamoDB node
  const [zoom, setZoom] = useState(1);

  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'pr':
        return <GitPullRequest className="w-4 h-4 text-amber-400" />;
      case 'code':
        return <Code2 className="w-4 h-4 text-sky-400" />;
      case 'service':
        return <Layers className="w-4 h-4 text-purple-400" />;
      case 'lambda':
        return <Cpu className="w-4 h-4 text-orange-400" />;
      case 'dynamodb':
        return <Database className="w-4 h-4 text-rose-400" />;
      case 'sqs':
        return <Radio className="w-4 h-4 text-emerald-400" />;
      default:
        return <Layers className="w-4 h-4 text-slate-400" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-100 font-sans tracking-tight">
            AWS Impact Graph
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Visual dependency graph correlating code modifications to AWS Cloud architecture.
          </p>
        </div>

        {/* Zoom Controls */}
        <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-800 rounded-md p-1">
          <button
            onClick={() => setZoom((z) => Math.max(0.7, z - 0.1))}
            className="p-1.5 hover:bg-slate-800 rounded text-slate-300 transition"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <span className="text-[11px] font-mono px-2 text-slate-400">{Math.round(zoom * 100)}%</span>
          <button
            onClick={() => setZoom((z) => Math.min(1.4, z + 0.1))}
            className="p-1.5 hover:bg-slate-800 rounded text-slate-300 transition"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => setZoom(1)}
            className="p-1.5 hover:bg-slate-800 rounded text-slate-300 transition"
            title="Reset Zoom"
          >
            <Maximize2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Graph Canvas Container */}
        <div className="lg:col-span-8 bg-slate-950/90 border border-slate-800 rounded-xl p-8 relative overflow-hidden min-h-[500px] flex flex-col justify-center items-center shadow-inner">
          {/* Subtle grid pattern */}
          <div
            className="absolute inset-0 opacity-15 pointer-events-none"
            style={{
              backgroundImage: 'radial-gradient(circle, #475569 1px, transparent 1px)',
              backgroundSize: '20px 20px',
            }}
          />

          <div
            className="w-full max-w-md flex flex-col items-center gap-3 transition-transform duration-200"
            style={{ transform: `scale(${zoom})` }}
          >
            {data.nodes.map((node, index) => {
              const isSelected = selectedNode?.id === node.id;
              return (
                <React.Fragment key={node.id}>
                  {/* Node Card */}
                  <div
                    onClick={() => setSelectedNode(node)}
                    className={`w-full p-3.5 rounded-lg border transition-all cursor-pointer select-none flex items-center justify-between ${
                      isSelected
                        ? 'bg-slate-900 border-amber-500 ring-2 ring-amber-500/30 shadow-lg shadow-amber-950/40'
                        : 'bg-slate-900/90 border-slate-800 hover:border-slate-700 hover:bg-slate-850'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded bg-slate-950 border border-slate-800 shrink-0">
                        {getNodeIcon(node.type)}
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs font-semibold text-slate-100">
                            {node.label}
                          </span>
                          <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">
                            {node.awsService}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400 mt-0.5">{node.metrics?.expectedImpact}</p>
                      </div>
                    </div>

                    <div className="shrink-0 pl-2">
                      <StatusBadge status={node.status} size="sm" />
                    </div>
                  </div>

                  {/* Connecting Edge Indicator */}
                  {index < data.nodes.length - 1 && (
                    <div className="flex flex-col items-center my-0.5">
                      <div className="w-0.5 h-3 bg-amber-500/60" />
                      <div className="w-1.5 h-1.5 rotate-45 border-r-2 border-b-2 border-amber-500" />
                    </div>
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>

        {/* Selected Node Details Panel */}
        <div className="lg:col-span-4">
          <Card
            title="Resource Impact Details"
            subtitle="Deep inspection of selected AWS dependency"
            badge={<Info className="w-4 h-4 text-amber-400" />}
          >
            {selectedNode ? (
              <div className="space-y-4 text-xs">
                <div className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                  <span className="text-[10px] font-mono text-slate-500 uppercase block">Selected Node</span>
                  <h4 className="text-sm font-bold font-mono text-amber-400 mt-0.5">
                    {selectedNode.label}
                  </h4>
                  <div className="flex items-center gap-2 mt-2">
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[10px]">
                      {selectedNode.awsService}
                    </span>
                    <span className="text-slate-500 font-mono text-[10px]">
                      {selectedNode.region || 'us-east-1'}
                    </span>
                  </div>
                </div>

                <div>
                  <span className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
                    Current Baseline Utilization
                  </span>
                  <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800 font-mono text-slate-300">
                    {selectedNode.metrics?.currentUtilization || 'Telemetry baseline nominal'}
                  </div>
                </div>

                <div>
                  <span className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
                    Expected Pre-Deployment Impact
                  </span>
                  <div className="p-2.5 rounded bg-amber-950/20 border border-amber-900/40 text-amber-300">
                    {selectedNode.metrics?.expectedImpact}
                  </div>
                </div>

                <div>
                  <span className="text-[10px] font-mono uppercase text-slate-400 block mb-1">
                    Telemetry & AST Evidence
                  </span>
                  <div className="p-2.5 rounded bg-slate-950/60 border border-slate-800 text-slate-300 leading-relaxed">
                    {selectedNode.evidenceSummary}
                  </div>
                </div>

                {selectedNode.metrics?.throughputOrConcurrency && (
                  <div className="pt-2 border-t border-slate-800 text-slate-400 flex justify-between font-mono text-[11px]">
                    <span>Capacity / Limit:</span>
                    <span className="text-slate-200">
                      {selectedNode.metrics.throughputOrConcurrency}
                    </span>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-xs text-slate-500">Select any node in the graph to view details.</p>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
};
