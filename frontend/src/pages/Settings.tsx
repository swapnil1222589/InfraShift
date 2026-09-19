import React from 'react';
import { Card } from '../components/common/Card';
import { Cloud, Sliders, ShieldCheck, CheckCircle2, Lock } from 'lucide-react';
import { GithubIcon } from '../components/common/Icons';

export const Settings: React.FC = () => {
  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-xl font-bold text-slate-100 font-sans tracking-tight">
          Platform Settings & AWS Integrations
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Configure GitHub repository hooks, CloudWatch telemetry sampling, and AWS IAM role trusts.
        </p>
      </div>

      {/* Repository Section */}
      <Card
        title="GitHub Repository Integration"
        subtitle="Webhook triggers and AST analysis pipeline"
        badge={<GithubIcon className="w-4 h-4 text-slate-300" />}
        headerAction={
          <span className="flex items-center gap-1.5 text-xs text-emerald-400 font-mono">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Connected</span>
          </span>
        }
      >
        <div className="space-y-3 text-xs">
          <div className="flex justify-between py-2 border-b border-slate-800/80">
            <span className="text-slate-400">Repository:</span>
            <span className="font-mono text-slate-200">aws-samples/serverless-checkout-api</span>
          </div>
          <div className="flex justify-between py-2 border-b border-slate-800/80">
            <span className="text-slate-400">Webhook Status:</span>
            <span className="text-emerald-400 font-medium">Listening on PR open, synchronize, reopen</span>
          </div>
          <div className="flex justify-between py-2">
            <span className="text-slate-400">Default Target Branch:</span>
            <span className="font-mono text-slate-300">main</span>
          </div>
        </div>
      </Card>

      {/* AWS Environment Section */}
      <Card
        title="AWS Environment & Infrastructure"
        subtitle="Connected cloud accounts and monitoring scopes"
        badge={<Cloud className="w-4 h-4 text-orange-400" />}
      >
        <div className="space-y-3 text-xs">
          <div className="flex justify-between py-2 border-b border-slate-800/80">
            <span className="text-slate-400">Environment:</span>
            <span className="text-slate-200 font-semibold">Production (us-east-1)</span>
          </div>
          <div className="flex justify-between py-2 border-b border-slate-800/80">
            <span className="text-slate-400">AWS Region:</span>
            <span className="font-mono text-slate-300">us-east-1 (US East N. Virginia)</span>
          </div>
          <div className="flex justify-between py-2">
            <span className="text-slate-400">AWS Account Reference:</span>
            <span className="font-mono text-slate-300">arn:aws:iam::124982148192:role/InfraShiftCorrelatorRole</span>
          </div>
        </div>
      </Card>

      {/* Metrics Section */}
      <Card
        title="CloudWatch Metrics & Baselines"
        subtitle="Observation windows for statistical inferencing"
        badge={<Sliders className="w-4 h-4 text-sky-400" />}
      >
        <div className="space-y-3 text-xs">
          <div className="flex justify-between py-2 border-b border-slate-800/80">
            <span className="text-slate-400">Monitored Namespaces:</span>
            <span className="font-mono text-slate-300">AWS/Lambda, AWS/DynamoDB, AWS/ApiGateway, AWS/SQS</span>
          </div>
          <div className="flex justify-between py-2 border-b border-slate-800/80">
            <span className="text-slate-400">Baseline Window:</span>
            <span className="font-mono text-slate-300">14 days rolling (1-minute granularity)</span>
          </div>
          <div className="flex justify-between py-2">
            <span className="text-slate-400">Comparison Window:</span>
            <span className="font-mono text-slate-300">24-hour peak alignment</span>
          </div>
        </div>
      </Card>

      {/* Access & Security */}
      <Card
        title="Security & Permissions"
        subtitle="Least-privilege read-only AWS IAM role status"
        badge={<ShieldCheck className="w-4 h-4 text-emerald-400" />}
      >
        <div className="space-y-3 text-xs">
          <div className="p-3 bg-emerald-950/20 border border-emerald-800/40 rounded text-emerald-300 flex items-center gap-2">
            <Lock className="w-4 h-4 shrink-0 text-emerald-400" />
            <span>
              Zero credential storage. InfraShift operates via short-lived AWS STS AssumeRole credentials with read-only CloudWatch and Describe API policies.
            </span>
          </div>
          <div className="flex justify-between py-2">
            <span className="text-slate-400">Permission Scope:</span>
            <span className="font-mono text-slate-300">ReadOnlyAccess (Telemetry & Config only)</span>
          </div>
        </div>
      </Card>
    </div>
  );
};
