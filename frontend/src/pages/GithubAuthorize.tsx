import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Layers, Check, ShieldAlert } from 'lucide-react';
import { GithubIcon } from '../components/common/Icons';
import { Button } from '../components/common/Button';

export const GithubAuthorize: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [isAuthorizing, setIsAuthorizing] = useState(false);

  const handleAuthorize = () => {
    setIsAuthorizing(true);
    
    // Simulate authorization latency
    setTimeout(() => {
      login('github');
      navigate('/dashboard', { replace: true });
    }, 1500);
  };

  const handleCancel = () => {
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 font-sans text-slate-200">
      
      {/* Disclaimer */}
      <div className="absolute top-6 flex items-center justify-center gap-2 px-4 py-2 bg-slate-900 border border-slate-800 rounded-full text-xs text-slate-400">
        <ShieldAlert className="w-4 h-4 text-amber-500" />
        <span>This is a demo authorization screen for the InfraShift hackathon.</span>
      </div>

      <div className="w-full max-w-[480px]">
        {/* Header Branding */}
        <div className="flex flex-col items-center mb-8">
          <div className="flex items-center justify-center gap-6 mb-6">
            {/* GitHub Logo */}
            <div className="w-14 h-14 rounded-full bg-slate-800 flex items-center justify-center border border-slate-700 shadow-xl">
              <GithubIcon className="w-8 h-8 text-slate-200" />
            </div>
            
            {/* Connection dots */}
            <div className="flex gap-1.5 opacity-40">
              <div className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-pulse" />
              <div className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-pulse delay-75" />
              <div className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-pulse delay-150" />
            </div>

            {/* InfraShift Logo */}
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-amber-500 via-orange-500 to-amber-600 flex items-center justify-center shadow-lg shadow-amber-500/20">
              <Layers className="w-7 h-7 text-slate-950" />
            </div>
          </div>
          
          <h1 className="text-2xl font-bold text-slate-100 tracking-tight">Authorize InfraShift</h1>
          <p className="text-sm text-slate-400 mt-2 text-center">
            InfraShift is requesting permission to access your GitHub account.
          </p>
        </div>

        {/* Authorization Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl shadow-2xl overflow-hidden">
          
          {/* Developer / Application Info */}
          <div className="p-6 border-b border-slate-800 bg-slate-900/50">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-sm font-semibold text-slate-200">InfraShift</h3>
                <p className="text-xs text-slate-500 font-mono mt-1">Developer: swapnil1222589</p>
              </div>
            </div>
          </div>

          {/* Requested Permissions */}
          <div className="p-6 border-b border-slate-800 bg-slate-900/50">
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4">
              Permissions requested
            </h4>
            <ul className="space-y-4">
              <li className="flex gap-3 text-sm text-slate-300">
                <Check className="w-5 h-5 text-emerald-500 shrink-0" />
                <span>Read your public profile</span>
              </li>
              <li className="flex gap-3 text-sm text-slate-300">
                <Check className="w-5 h-5 text-emerald-500 shrink-0" />
                <span>Read repository information</span>
              </li>
              <li className="flex gap-3 text-sm text-slate-300">
                <Check className="w-5 h-5 text-emerald-500 shrink-0" />
                <span>Read pull requests</span>
              </li>
            </ul>
          </div>

          {/* User Account Mock */}
          <div className="p-6 bg-slate-950/50 border-b border-slate-800">
             <div className="flex items-center gap-4">
               <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-amber-600 to-orange-400 text-slate-950 font-bold text-lg flex items-center justify-center ring-2 ring-slate-800">
                 GH
               </div>
               <div>
                 <div className="font-semibold text-slate-200 text-sm">GitHub Demo User</div>
                 <div className="text-xs text-slate-400 mt-0.5">@github-demo · demo@infrashift.dev</div>
               </div>
             </div>
          </div>

          {/* Action Buttons */}
          <div className="p-6 bg-slate-900 flex items-center justify-between gap-4">
            <Button
              variant="outline"
              className="flex-1 justify-center"
              onClick={handleCancel}
              disabled={isAuthorizing}
            >
              Cancel
            </Button>
            <Button
              variant="aws"
              className="flex-1 justify-center"
              onClick={handleAuthorize}
              loading={isAuthorizing}
            >
              {isAuthorizing ? 'Authorizing...' : 'Authorize InfraShift'}
            </Button>
          </div>
          
        </div>
      </div>
    </div>
  );
};
