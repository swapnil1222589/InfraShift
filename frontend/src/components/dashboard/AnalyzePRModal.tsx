import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { X, GitPullRequest, Sparkles, CheckCircle2, ArrowRight } from 'lucide-react';
import { Button } from '../common/Button';
import { triggerPRAnalysis } from '../../api/analyses';

interface AnalyzePRModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectId: string;
}

export const AnalyzePRModal: React.FC<AnalyzePRModalProps> = ({
  isOpen,
  onClose,
  projectId,
}) => {
  const navigate = useNavigate();
  const [prNumber, setPrNumber] = useState<number>(248);
  const [repository, setRepository] = useState('aws-samples/serverless-checkout-api');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const result = await triggerPRAnalysis(projectId, prNumber, repository);
      onClose();
      navigate(`/analyses/${result.id}`);
    } catch (err) {
      console.error(err);
      navigate('/analyses/analysis-pr-248');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-2xl max-w-lg w-full overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-100">Analyze Pull Request</h3>
              <p className="text-xs text-slate-400">Map code diffs to AWS resources & forecast impact</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 p-1 rounded-md hover:bg-slate-800 transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-xs font-mono text-slate-400 uppercase mb-1">
              GitHub Repository
            </label>
            <input
              type="text"
              value={repository}
              onChange={(e) => setRepository(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-md px-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-mono text-slate-400 uppercase mb-1">
              Pull Request Number
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-xs font-mono text-amber-500 font-bold">
                #
              </span>
              <input
                type="number"
                value={prNumber}
                onChange={(e) => setPrNumber(parseInt(e.target.value) || 0)}
                className="w-full bg-slate-950 border border-slate-800 rounded-md pl-7 pr-3 py-2 text-xs font-mono text-slate-200 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
                required
              />
            </div>
          </div>

          {/* Quick preset selection */}
          <div>
            <span className="text-[11px] font-mono text-slate-500 block mb-2">
              RECOMMENDED DEMO PRESETS:
            </span>
            <div className="grid grid-cols-1 gap-2">
              <button
                type="button"
                onClick={() => {
                  setPrNumber(248);
                  setRepository('aws-samples/serverless-checkout-api');
                }}
                className={`text-left p-2.5 rounded-lg border text-xs transition ${
                  prNumber === 248
                    ? 'border-amber-500/50 bg-amber-500/10 text-amber-200'
                    : 'border-slate-800 bg-slate-950/60 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between font-mono">
                  <span className="font-semibold text-slate-200">PR #248 (Primary Hackathon Demo)</span>
                  <span className="text-orange-400">High Risk</span>
                </div>
                <div className="text-[11px] text-slate-400 mt-1">
                  DynamoDB Secondary Index query mutation & Lambda latency delta
                </div>
              </button>

              <button
                type="button"
                onClick={() => {
                  setPrNumber(247);
                  setRepository('aws-samples/serverless-checkout-api');
                }}
                className={`text-left p-2.5 rounded-lg border text-xs transition ${
                  prNumber === 247
                    ? 'border-amber-500/50 bg-amber-500/10 text-amber-200'
                    : 'border-slate-800 bg-slate-950/60 text-slate-400 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between font-mono">
                  <span className="font-semibold text-slate-200">PR #247 (SQS Tuning)</span>
                  <span className="text-amber-400">Medium Risk</span>
                </div>
                <div className="text-[11px] text-slate-400 mt-1">
                  SQS batch processing size & concurrency optimization
                </div>
              </button>
            </div>
          </div>

          <div className="pt-2 flex items-center justify-end gap-3 border-t border-slate-800/80">
            <Button variant="ghost" size="sm" type="button" onClick={onClose}>
              Cancel
            </Button>
            <Button
              variant="aws"
              size="md"
              type="submit"
              loading={isSubmitting}
              icon={<ArrowRight className="w-4 h-4" />}
              iconPosition="right"
            >
              Start Pre-Deployment Analysis
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
