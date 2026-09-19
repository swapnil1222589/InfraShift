import React, { useState, useRef } from 'react';
import { ImpactGraphData, ImpactNode } from '../../types/impact';
import { Card } from '../common/Card';
import { StatusBadge } from '../common/StatusBadge';
import { NodeDetailsPanel } from './NodeDetailsPanel';
import {
  GitPullRequest,
  Code2,
  Layers,
  Cpu,
  Database,
  Radio,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Move,
  Info,
  ArrowDown,
} from 'lucide-react';

interface ImpactGraphViewProps {
  data: ImpactGraphData;
}

export const ImpactGraphView: React.FC<ImpactGraphViewProps> = ({ data }) => {
  const [selectedNode, setSelectedNode] = useState<ImpactNode>(data.nodes[4] || data.nodes[0]);
  const [zoom, setZoom] = useState<number>(1);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  const handleMouseDown = (e: React.MouseEvent) => {
    // Only start dragging if clicking canvas background
    if ((e.target as HTMLElement).closest('.graph-node')) return;
    setIsDragging(true);
    setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    setPan({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y,
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleReset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

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

  const impactBorder = {
    none: 'border-slate-800',
    low: 'border-emerald-800/80',
    moderate: 'border-amber-800/80',
    high: 'border-orange-600',
    critical: 'border-rose-600',
  };

  return (
    <div className="space-y-4">
      {/* Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 bg-slate-900 border border-slate-800 rounded-lg text-xs">
        <div className="flex items-center gap-2 text-slate-400 font-mono">
          <Info className="w-3.5 h-3.5 text-amber-500" />
          <span>Click any node to inspect AWS service metrics. Drag canvas to pan.</span>
        </div>

        <div className="flex items-center gap-1.5 bg-slate-950 border border-slate-800 rounded-md p-1 font-mono">
          <button
            onClick={() => setZoom((z) => Math.max(0.6, z - 0.1))}
            className="p-1.5 hover:bg-slate-800 rounded text-slate-300 transition"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <span className="text-[11px] px-2 text-slate-400 min-w-[45px] text-center">
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={() => setZoom((z) => Math.min(1.5, z + 0.1))}
            className="p-1.5 hover:bg-slate-800 rounded text-slate-300 transition"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <div className="w-px h-3.5 bg-slate-800 mx-0.5" />
          <button
            onClick={handleReset}
            className="p-1.5 hover:bg-slate-800 rounded text-slate-300 transition"
            title="Reset View"
          >
            <Maximize2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Grid: Visual Graph + Details Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Visual Graph Canvas */}
        <div
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          className={`lg:col-span-7 bg-slate-950/90 border border-slate-800 rounded-xl p-6 relative overflow-hidden min-h-[580px] flex flex-col justify-center items-center select-none shadow-inner ${
            isDragging ? 'cursor-grabbing' : 'cursor-grab'
          }`}
        >
          {/* Subtle Grid Dots */}
          <div
            className="absolute inset-0 opacity-15 pointer-events-none"
            style={{
              backgroundImage: 'radial-gradient(circle, #64748b 1px, transparent 1px)',
              backgroundSize: '24px 24px',
            }}
          />

          {/* Interactive Graph Node Chain */}
          <div
            className="w-full max-w-md flex flex-col items-center gap-2.5 transition-transform duration-75"
            style={{
              transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
              transformOrigin: 'center center',
            }}
          >
            {data.nodes.map((node, index) => {
              const isSelected = selectedNode?.id === node.id;
              return (
                <React.Fragment key={node.id}>
                  {/* Graph Node */}
                  <div
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedNode(node);
                    }}
                    className={`graph-node w-full p-3.5 rounded-lg border transition-all cursor-pointer flex items-center justify-between ${
                      isSelected
                        ? 'bg-slate-900 border-amber-500 ring-2 ring-amber-500/30 shadow-lg shadow-amber-950/40'
                        : `bg-slate-900/95 ${impactBorder[node.impactLevel]} hover:border-slate-600 hover:bg-slate-850`
                    }`}
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="p-2 rounded bg-slate-950 border border-slate-800 shrink-0">
                        {getNodeIcon(node.type)}
                      </div>
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs font-semibold text-slate-100 truncate">
                            {node.label}
                          </span>
                          <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 shrink-0">
                            {node.awsService}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400 mt-0.5 truncate">
                          {node.metrics?.expectedImpact}
                        </p>
                      </div>
                    </div>

                    <div className="shrink-0 pl-3">
                      <StatusBadge status={node.status} size="sm" />
                    </div>
                  </div>

                  {/* Connecting Edge Indicator */}
                  {index < data.nodes.length - 1 && (
                    <div className="flex flex-col items-center py-0.5">
                      <div className="w-0.5 h-3 bg-amber-500/60" />
                      <div className="w-1.5 h-1.5 rotate-45 border-r-2 border-b-2 border-amber-500" />
                    </div>
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>

        {/* Selected Node Details Side Panel */}
        <div className="lg:col-span-5">
          <NodeDetailsPanel node={selectedNode} />
        </div>
      </div>
    </div>
  );
};
