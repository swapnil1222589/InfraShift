import React, { useState } from 'react';
import { Analysis } from '../../types/analysis';
import { RiskBadge } from '../common/RiskBadge';
import { StatusBadge } from '../common/StatusBadge';
import { ConfidenceMeter } from '../common/ConfidenceMeter';
import { Button } from '../common/Button';
import { GitHubPRModal } from './GitHubPRModal';
import {
  GitPullRequest,
  GitBranch,
  GitCommit,
  ExternalLink,
  Share2,
  RefreshCw,
  Clock,
  ShieldCheck,
} from 'lucide-react';
import { GithubIcon } from '../common/Icons';

interface AnalysisHeaderProps {
  analysis: Analysis;
  onRefresh?: () => void;
  isRefreshing?: boolean;
}

export const AnalysisHeader: React.FC<AnalysisHeaderProps> = ({
  analysis,
  onRefresh,
  isRefreshing = false,
}) => {
  const [isGitHubModalOpen, setIsGitHubModalOpen] = useState(false);

  return (
    <>
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 md:p-6 shadow-sm">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            {/* Top meta tags */}
            <div className="flex flex-wrap items-center gap-2.5 mb-2.5">
              <span className="font-mono font-bold text-amber-400 text-sm md:text-base flex items-center gap-1.5">
                <GitPullRequest className="w-4 h-4 text-amber-400" />
                PR #{analysis.prNumber}
              </span>
              <RiskBadge risk={analysis.risk} size="md" />
              <StatusBadge status={analysis.status} size="md" />
              <ConfidenceMeter score={analysis.confidence} />
            </div>

            {/* Title */}
            <h1 className="text-2xl md:text-3xl font-extrabold text-slate-100 font-sans tracking-tight mt-1">
              {analysis.prTitle}
            </h1>

            {/* Git Repository Meta Information */}
            <div className="mt-4 flex flex-wrap items-center gap-4 text-xs font-mono text-slate-400">
              <div className="flex items-center gap-1.5 text-slate-300">
                <GithubIcon className="w-3.5 h-3.5 text-slate-400" />
                <span className="font-semibold text-amber-300/90">{analysis.repository}</span>
              </div>
              <span className="text-slate-600">·</span>
              <div className="flex items-center gap-1.5">
                <GitBranch className="w-3.5 h-3.5 text-slate-500" />
                <span className="text-slate-300">{analysis.branch}</span>
                <span className="text-slate-600">→</span>
                <span className="text-slate-400">{analysis.targetBranch}</span>
              </div>
              <span className="text-slate-600">·</span>
              <div className="flex items-center gap-1.5">
                <GitCommit className="w-3.5 h-3.5 text-slate-500" />
                <span className="text-amber-400 font-mono">{analysis.commitSha}</span>
              </div>
              <span className="text-slate-600">·</span>
              <div className="text-slate-400">
                Author: <span className="text-slate-200">{analysis.author.name}</span>
              </div>
            </div>
          </div>

          {/* Action Controls */}
          <div className="flex flex-wrap items-center gap-2.5 self-start lg:self-center shrink-0">
            {onRefresh && (
              <Button
                variant="outline"
                size="sm"
                icon={<RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />}
                onClick={onRefresh}
                title="Resync CloudWatch metrics"
              >
                Re-evaluate
              </Button>
            )}

            <button
              onClick={() => setIsGitHubModalOpen(true)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs font-medium rounded-md transition shrink-0"
            >
              <span>View GitHub PR</span>
              <ExternalLink className="w-3 h-3 text-slate-400 shrink-0" />
            </button>
          </div>
        </div>
      </div>

      <GitHubPRModal
        isOpen={isGitHubModalOpen}
        onClose={() => setIsGitHubModalOpen(false)}
      />
    </>
  );
};
