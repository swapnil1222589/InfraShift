import React from 'react';
import { Loader2, AlertCircle, Inbox, RefreshCw, CheckCircle2, ShieldAlert } from 'lucide-react';
import { Button } from './Button';

export const LoadingState: React.FC<{ message?: string; subtext?: string }> = ({
  message = 'Analyzing infrastructure impact telemetry...',
  subtext = 'Connecting to AWS CloudWatch & parsing PR AST',
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
      <div className="relative mb-4">
        <div className="w-12 h-12 rounded-full border-2 border-slate-800 border-t-amber-500 animate-spin flex items-center justify-center" />
        <Loader2 className="w-5 h-5 text-amber-500 absolute inset-0 m-auto animate-pulse" />
      </div>
      <h4 className="text-sm font-medium text-slate-200">{message}</h4>
      <p className="text-xs text-slate-500 mt-1 max-w-sm">{subtext}</p>
    </div>
  );
};

export const EmptyState: React.FC<{
  title?: string;
  description?: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: React.ReactNode;
}> = ({
  title = 'No analyses found',
  description = 'No PR analyses have been triggered for this project yet.',
  actionLabel,
  onAction,
  icon = <Inbox className="w-8 h-8 text-slate-600" />,
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-14 px-4 text-center border border-dashed border-slate-800 rounded-lg bg-slate-900/30">
      <div className="p-3 bg-slate-800/60 rounded-full mb-3">{icon}</div>
      <h4 className="text-sm font-semibold text-slate-200">{title}</h4>
      <p className="text-xs text-slate-400 mt-1 max-w-md">{description}</p>
      {actionLabel && onAction && (
        <div className="mt-4">
          <Button variant="outline" size="sm" onClick={onAction}>
            {actionLabel}
          </Button>
        </div>
      )}
    </div>
  );
};

export const ErrorState: React.FC<{
  error?: string;
  onRetry?: () => void;
}> = ({
  error = 'Failed to load telemetry data from CloudWatch or API Gateway',
  onRetry,
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center border border-rose-900/40 rounded-lg bg-rose-950/20">
      <AlertCircle className="w-8 h-8 text-rose-400 mb-3" />
      <h4 className="text-sm font-semibold text-rose-200">Unable to load data</h4>
      <p className="text-xs text-rose-300/80 mt-1 max-w-md font-mono">{error}</p>
      {onRetry && (
        <div className="mt-4">
          <Button variant="danger" size="sm" icon={<RefreshCw className="w-3.5 h-3.5" />} onClick={onRetry}>
            Retry Request
          </Button>
        </div>
      )}
    </div>
  );
};

export const SuccessState: React.FC<{
  title?: string;
  message?: string;
}> = ({
  title = 'Analysis completed successfully',
  message = 'Infrastructure impact forecast and recommendations are ready.',
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center border border-emerald-900/40 rounded-lg bg-emerald-950/20">
      <CheckCircle2 className="w-8 h-8 text-emerald-400 mb-3" />
      <h4 className="text-sm font-semibold text-emerald-200">{title}</h4>
      <p className="text-xs text-emerald-300/80 mt-1 max-w-md font-mono">{message}</p>
    </div>
  );
};

export const InsufficientEvidenceState: React.FC<{
  title?: string;
  message?: string;
}> = ({
  title = 'Insufficient Evidence',
  message = 'Insufficient evidence to generate a reliable forecast. We recommend deploying to a staging environment first.',
}) => {
  return (
    <div className="flex flex-col items-center justify-center py-12 px-4 text-center border border-amber-900/40 rounded-lg bg-amber-950/20">
      <ShieldAlert className="w-8 h-8 text-amber-500 mb-3" />
      <h4 className="text-sm font-semibold text-amber-200">{title}</h4>
      <p className="text-xs text-amber-300/80 mt-1 max-w-md font-mono">{message}</p>
    </div>
  );
};
