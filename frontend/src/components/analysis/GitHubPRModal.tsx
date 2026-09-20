import React, { useState, useEffect } from 'react';
import { X, ExternalLink, CheckCircle2 } from 'lucide-react';
import { Button } from '../common/Button';
import { GithubIcon } from '../common/Icons';
import { buildGitHubPullRequestUrl } from '../../utils/github';

interface GitHubPRModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const GitHubPRModal: React.FC<GitHubPRModalProps> = ({
  isOpen,
  onClose,
}) => {
  const [repositoryUrl, setRepositoryUrl] = useState('https://github.com/swapnil1222589/InfraShift');
  const [prNumber, setPrNumber] = useState('1');
  
  const [repoError, setRepoError] = useState('');
  const [prError, setPrError] = useState('');
  
  const [isRepoValid, setIsRepoValid] = useState(false);
  const [isPrValid, setIsPrValid] = useState(false);

  // Validate Repository
  const checkRepoValidity = (url: string) => {
    if (!url.trim()) return { valid: false, error: 'Repository URL is required.' };
    try {
      // Use the utility to test if it parses correctly
      buildGitHubPullRequestUrl(url, 1);
      return { valid: true, error: '' };
    } catch {
      return { valid: false, error: 'Enter a valid GitHub repository URL.' };
    }
  };

  // Validate PR Number
  const checkPrValidity = (pr: string) => {
    const trimmed = pr.trim();
    if (!trimmed) return { valid: false, error: 'Pull request number is required.' };
    if (!/^\d+$/.test(trimmed)) return { valid: false, error: 'Enter a valid pull request number.' };
    const num = parseInt(trimmed, 10);
    if (isNaN(num) || num <= 0) return { valid: false, error: 'Enter a valid pull request number.' };
    return { valid: true, error: '' };
  };

  // Reset state on open
  useEffect(() => {
    if (isOpen) {
      setRepositoryUrl('https://github.com/swapnil1222589/InfraShift');
      setPrNumber('1');
      setRepoError('');
      setPrError('');
      setIsRepoValid(true);
      setIsPrValid(true);
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleRepoBlur = () => {
    const { valid, error } = checkRepoValidity(repositoryUrl);
    setIsRepoValid(valid);
    setRepoError(error);
  };

  const handlePrBlur = () => {
    const { valid, error } = checkPrValidity(prNumber);
    setIsPrValid(valid);
    setPrError(error);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const repoCheck = checkRepoValidity(repositoryUrl);
    const prCheck = checkPrValidity(prNumber);
    
    setIsRepoValid(repoCheck.valid);
    setRepoError(repoCheck.error);
    setIsPrValid(prCheck.valid);
    setPrError(prCheck.error);

    if (!repoCheck.valid || !prCheck.valid) {
      return;
    }
    
    try {
      // Construct final URL using the safe builder
      const githubPrUrl = buildGitHubPullRequestUrl(repositoryUrl, parseInt(prNumber, 10));
      
      console.log("Opening GitHub PR:", githubPrUrl);
      
      // Open in new tab
      const newWindow = window.open(githubPrUrl, '_blank', 'noopener,noreferrer');
      
      if (!newWindow) {
        setRepoError('Your browser blocked the GitHub tab. Please allow pop-ups and try again.');
        return;
      }
      
      onClose();
    } catch (err) {
      setRepoError('Enter a valid GitHub repository URL.');
    }
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-150"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div 
        className="bg-slate-900 border border-slate-800 rounded-xl shadow-2xl max-w-[460px] w-full overflow-hidden flex flex-col"
        role="dialog"
        aria-modal="true"
        aria-labelledby="github-modal-title"
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-slate-800 text-slate-300 border border-slate-700 shadow-sm">
              <GithubIcon className="w-4 h-4" />
            </div>
            <div>
              <h3 id="github-modal-title" className="text-[15px] font-semibold text-slate-100 tracking-tight">View GitHub Pull Request</h3>
              <p className="text-xs text-slate-400 mt-0.5">Enter the repository and pull request you want to inspect.</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-500 hover:text-slate-200 p-1.5 rounded-md hover:bg-slate-800 transition-colors"
            aria-label="Close modal"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {/* Repository Input */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Repository URL
            </label>
            <div className="relative">
              <input
                type="text"
                value={repositoryUrl}
                onChange={(e) => {
                  setRepositoryUrl(e.target.value);
                  setIsRepoValid(false);
                  setRepoError('');
                }}
                onBlur={handleRepoBlur}
                placeholder="https://github.com/owner/repository"
                className={`w-full bg-slate-950/50 border rounded-lg px-3 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 transition-all ${
                  repoError 
                    ? 'border-rose-500/50 focus:border-rose-500 focus:ring-rose-500/20' 
                    : isRepoValid 
                      ? 'border-emerald-500/50 focus:border-emerald-500 focus:ring-emerald-500/20' 
                      : 'border-slate-800 focus:border-amber-500 focus:ring-amber-500/20'
                }`}
              />
              {isRepoValid && !repoError && (
                <CheckCircle2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-emerald-500" />
              )}
            </div>
            {repoError && (
              <p className="text-xs text-rose-400 font-medium mt-1.5 ml-1">{repoError}</p>
            )}
          </div>

          {/* PR Input */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
              Pull Request Number
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-sm font-mono text-slate-500 font-bold select-none">
                #
              </span>
              <input
                type="text"
                value={prNumber}
                onChange={(e) => {
                  setPrNumber(e.target.value);
                  setIsPrValid(false);
                  setPrError('');
                }}
                onBlur={handlePrBlur}
                placeholder="1"
                className={`w-full bg-slate-950/50 border rounded-lg pl-7 pr-3 py-2.5 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-2 transition-all ${
                  prError 
                    ? 'border-rose-500/50 focus:border-rose-500 focus:ring-rose-500/20' 
                    : isPrValid 
                      ? 'border-emerald-500/50 focus:border-emerald-500 focus:ring-emerald-500/20' 
                      : 'border-slate-800 focus:border-amber-500 focus:ring-amber-500/20'
                }`}
              />
              {isPrValid && !prError && (
                <CheckCircle2 className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-emerald-500" />
              )}
            </div>
            {prError && (
              <p className="text-xs text-rose-400 font-medium mt-1.5 ml-1">{prError}</p>
            )}
          </div>

          <div className="pt-2 flex flex-col sm:flex-row items-center justify-end gap-3 mt-6">
            <Button variant="ghost" className="w-full sm:w-auto justify-center" type="button" onClick={onClose}>
              Cancel
            </Button>
            <Button
              variant="aws"
              className="w-full sm:w-auto justify-center"
              type="submit"
              icon={<ExternalLink className="w-4 h-4" />}
              iconPosition="right"
            >
              Open GitHub PR
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
