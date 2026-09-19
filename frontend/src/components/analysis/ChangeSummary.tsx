import React from 'react';
import { ChangeSummary as ChangeSummaryType } from '../../types/analysis';
import { Card } from '../common/Card';
import { FileCode, FunctionSquare, Layers, Radio, ShieldAlert, Check, ChevronRight } from 'lucide-react';

interface ChangeSummaryProps {
  summary: ChangeSummaryType;
}

export const ChangeSummary: React.FC<ChangeSummaryProps> = ({ summary }) => {
  return (
    <Card
      title="SECTION 1 — Change Summary"
      subtitle="Static AST & infrastructure-as-code diff breakdown"
      badge={<FileCode className="w-4 h-4 text-amber-400" />}
      headerAction={
        <div className="flex items-center gap-2 font-mono text-xs">
          <span className="text-emerald-400 font-semibold">+{summary.totalAdditions}</span>
          <span className="text-slate-600">/</span>
          <span className="text-rose-400 font-semibold">-{summary.totalDeletions}</span>
        </div>
      }
    >
      <div className="space-y-6">
        {/* Core Profile Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
            <span className="text-[10px] font-mono text-slate-500 uppercase block">Change Type</span>
            <span className="text-xs font-semibold text-amber-400 mt-1 block">
              {summary.changeType}
            </span>
            <span className="text-[10px] text-slate-400 mt-0.5 block">Access pattern update</span>
          </div>

          <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
            <span className="text-[10px] font-mono text-slate-500 uppercase block">Estimated Blast Radius</span>
            <span className="text-xs font-mono font-semibold text-orange-400 uppercase mt-1 block">
              {summary.blastRadius}
            </span>
            <span className="text-[10px] text-slate-400 mt-0.5 block">Isolated to checkout domain</span>
          </div>

          <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
            <span className="text-[10px] font-mono text-slate-500 uppercase block">Affected AWS Services</span>
            <span className="text-xs font-semibold text-sky-400 mt-1 block truncate">
              {summary.primaryAffectedService}
            </span>
            <span className="text-[10px] text-slate-400 mt-0.5 block">Amazon DynamoDB & Lambda</span>
          </div>

          <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800">
            <span className="text-[10px] font-mono text-slate-500 uppercase block">Changed Functions</span>
            <span className="text-xs font-mono font-semibold text-slate-200 mt-1 block">
              {summary.changedFunctionsCount} functions modified
            </span>
            <span className="text-[10px] text-slate-400 mt-0.5 block">AST method correlation</span>
          </div>
        </div>

        {/* Changed Files Detail Table */}
        <div>
          <span className="text-[11px] font-mono uppercase text-slate-400 font-semibold block mb-2">
            CHANGED SOURCE FILES & AST MAPPINGS:
          </span>

          <div className="border border-slate-800 rounded-lg overflow-hidden bg-slate-950/50">
            <div className="divide-y divide-slate-800/80">
              {summary.changedFiles.map((file, idx) => (
                <div key={idx} className="p-3.5 hover:bg-slate-900/40 transition">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <FileCode className="w-4 h-4 text-slate-400 shrink-0" />
                      <span className="font-mono text-xs text-slate-200 font-medium">
                        {file.path}
                      </span>
                      <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 border border-slate-700 uppercase">
                        {file.status}
                      </span>
                    </div>

                    <div className="flex items-center gap-3 font-mono text-xs">
                      <span className="text-emerald-400 font-medium">+{file.additions}</span>
                      <span className="text-rose-400 font-medium">-{file.deletions}</span>
                    </div>
                  </div>

                  {/* Functions altered */}
                  {file.functions.length > 0 && (
                    <div className="mt-2 pl-6 flex flex-wrap items-center gap-1.5">
                      <span className="text-[10px] text-slate-500 font-mono">Affected methods:</span>
                      {file.functions.map((fn, fIdx) => (
                        <span
                          key={fIdx}
                          className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 font-mono text-[10px] border border-amber-500/20"
                        >
                          {fn}()
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};
