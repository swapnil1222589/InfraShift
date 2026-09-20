import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  Layers,
  Search,
  Bell,
  ChevronDown,
  Globe,
  Server,
  Sparkles,
  LogOut,
} from 'lucide-react';
import { GithubIcon } from '../common/Icons';
import { mockProjects, mockEnvironments } from '../../mock/projects';

interface HeaderProps {
  currentProjectId: string;
  onProjectChange: (id: string) => void;
  currentEnvId: string;
  onEnvChange: (id: string) => void;
  onOpenAnalyzeModal: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentProjectId,
  onProjectChange,
  currentEnvId,
  onEnvChange,
  onOpenAnalyzeModal,
}) => {
  const [projectDropdownOpen, setProjectDropdownOpen] = useState(false);
  const [envDropdownOpen, setEnvDropdownOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const activeProject = mockProjects.find((p) => p.id === currentProjectId) || mockProjects[0];
  const activeEnv = mockEnvironments.find((e) => e.id === currentEnvId) || mockEnvironments[0];

  return (
    <header className="h-14 border-b border-slate-800 bg-slate-950/90 backdrop-blur-md sticky top-0 z-40 px-4 flex items-center justify-between gap-4">
      {/* Brand & Context Selectors */}
      <div className="flex items-center gap-4">
        {/* Brand Logo */}
        <div className="flex items-center gap-2.5 mr-2">
          <div className="w-8 h-8 rounded bg-gradient-to-br from-amber-500 via-orange-500 to-amber-600 flex items-center justify-center shadow-sm shadow-amber-500/20">
            <Layers className="w-5 h-5 text-slate-950" />
          </div>
          <div className="flex flex-col">
            <div className="flex items-center gap-1.5">
              <span className="font-bold text-slate-100 tracking-tight text-sm">InfraShift</span>
              <span className="text-[10px] font-mono px-1.5 py-0.2 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded font-semibold">
                AWS
              </span>
            </div>
            <span className="text-[10px] text-slate-400 font-mono hidden md:block">pre-deploy intelligence</span>
          </div>
        </div>

        <div className="h-5 w-px bg-slate-800 hidden lg:block" />

        {/* Project Selector */}
        <div className="relative hidden md:block">
          <button
            onClick={() => {
              setProjectDropdownOpen(!projectDropdownOpen);
              setEnvDropdownOpen(false);
            }}
            className="flex items-center gap-2 px-2.5 py-1.5 rounded-md bg-slate-900 border border-slate-800 text-xs font-medium text-slate-200 hover:border-slate-700 transition"
          >
            <Server className="w-3.5 h-3.5 text-amber-500" />
            <span className="max-w-[130px] truncate">{activeProject.name}</span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>

          {projectDropdownOpen && (
            <div className="absolute top-full left-0 mt-1 w-64 bg-slate-900 border border-slate-800 rounded-lg shadow-xl py-1 z-50">
              <div className="px-3 py-1.5 text-[11px] font-semibold text-slate-400 border-b border-slate-800/80">
                ACTIVE REPOSITORY
              </div>
              {mockProjects.map((p) => (
                <button
                  key={p.id}
                  onClick={() => {
                    onProjectChange(p.id);
                    setProjectDropdownOpen(false);
                  }}
                  className={`w-full text-left px-3 py-2 text-xs flex flex-col hover:bg-slate-800/60 transition ${
                    p.id === activeProject.id ? 'bg-amber-500/10 text-amber-300 font-medium' : 'text-slate-300'
                  }`}
                >
                  <span className="font-mono">{p.name}</span>
                  <span className="text-[10px] text-slate-500">{p.repository}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Environment Selector */}
        <div className="relative hidden lg:block">
          <button
            onClick={() => {
              setEnvDropdownOpen(!envDropdownOpen);
              setProjectDropdownOpen(false);
            }}
            className="flex items-center gap-2 px-2.5 py-1.5 rounded-md bg-slate-900 border border-slate-800 text-xs font-medium text-slate-200 hover:border-slate-700 transition"
          >
            <Globe className="w-3.5 h-3.5 text-sky-400" />
            <span className="max-w-[120px] truncate">{activeEnv.name.split(' ')[0]}</span>
            <span className="text-[10px] font-mono text-slate-400">({activeEnv.region})</span>
            <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
          </button>

          {envDropdownOpen && (
            <div className="absolute top-full left-0 mt-1 w-60 bg-slate-900 border border-slate-800 rounded-lg shadow-xl py-1 z-50">
              <div className="px-3 py-1.5 text-[11px] font-semibold text-slate-400 border-b border-slate-800/80">
                AWS ENVIRONMENT
              </div>
              {mockEnvironments.map((env) => (
                <button
                  key={env.id}
                  onClick={() => {
                    onEnvChange(env.id);
                    setEnvDropdownOpen(false);
                  }}
                  className={`w-full text-left px-3 py-2 text-xs flex flex-col hover:bg-slate-800/60 transition ${
                    env.id === activeEnv.id ? 'bg-sky-500/10 text-sky-300 font-medium' : 'text-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span>{env.name}</span>
                    <span className="text-[10px] font-mono text-slate-500">{env.stage}</span>
                  </div>
                  <span className="text-[10px] text-slate-500 font-mono">Account: {env.awsAccountId}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Center Search */}
      <div className="flex-1 max-w-md hidden md:block">
        <div className="relative">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search PR #, Lambda function, DynamoDB table, or AWS resource..."
            className="w-full bg-slate-900/90 border border-slate-800 rounded-md pl-9 pr-8 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition"
          />
          <kbd className="absolute right-2.5 top-1/2 -translate-y-1/2 px-1.5 py-0.5 text-[10px] font-mono text-slate-500 bg-slate-800 rounded border border-slate-700">
            /
          </kbd>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        {/* Quick CTA */}
        <button
          onClick={onOpenAnalyzeModal}
          className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-slate-950 font-semibold text-xs rounded-md shadow-sm transition active:translate-y-px"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Analyze PR</span>
        </button>

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setNotificationsOpen(!notificationsOpen)}
            className="p-1.5 rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-900 border border-transparent hover:border-slate-800 transition relative"
            title="Notifications"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-amber-500 ring-2 ring-slate-950" />
          </button>

          {notificationsOpen && (
            <div className="absolute right-0 top-full mt-1 w-80 bg-slate-900 border border-slate-800 rounded-lg shadow-2xl py-2 z-50 text-xs">
              <div className="px-3 py-1.5 border-b border-slate-800 font-semibold text-slate-200 flex items-center justify-between">
                <span>CloudWatch Telemetry Alerts</span>
                <span className="text-[10px] text-amber-400 font-mono">1 High Priority</span>
              </div>
              <div className="divide-y divide-slate-800/60 max-h-64 overflow-y-auto">
                <div className="p-3 hover:bg-slate-800/40 cursor-pointer">
                  <div className="text-orange-400 font-medium text-[11px] flex items-center gap-1">
                    <span>High Cost Forecast Alert</span>
                  </div>
                  <p className="text-slate-300 mt-1">PR #248 forecast indicates +28.4% DynamoDB RCU consumption spike.</p>
                  <span className="text-[10px] text-slate-500 font-mono mt-1 block">15m ago · Checkout Service</span>
                </div>
                <div className="p-3 hover:bg-slate-800/40 cursor-pointer">
                  <div className="text-emerald-400 font-medium text-[11px]">Outcome Validated</div>
                  <p className="text-slate-300 mt-1">PR #245 staging verification finished with error delta &lt; 2%.</p>
                  <span className="text-[10px] text-slate-500 font-mono mt-1 block">2h ago · Presigned URLs</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* GitHub Link */}
        <a
          href="https://github.com/swapnil1222589/InfraShift"
          target="_blank"
          rel="noreferrer"
          className="p-1.5 text-slate-400 hover:text-slate-200 rounded-md hover:bg-slate-900 transition hidden sm:block"
          title="GitHub Integration"
        >
          <GithubIcon className="w-4 h-4" />
        </a>

        {/* User Profile Pill */}
        <div className="relative">
          <button
            onClick={() => setProfileDropdownOpen(!profileDropdownOpen)}
            className="flex items-center gap-2 pl-2 border-l border-slate-800 focus:outline-none hover:opacity-80 transition"
          >
            <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-amber-600 to-orange-400 text-slate-950 font-bold text-xs flex items-center justify-center ring-1 ring-slate-700 shrink-0">
              {user?.initials || 'DE'}
            </div>
            <div className="hidden xl:flex flex-col text-left">
              <span className="text-xs font-medium text-slate-200 leading-tight">{user?.name || 'Demo Engineer'}</span>
              <span className="text-[10px] text-slate-500 font-mono leading-tight">{user?.role || 'Platform Engineer'}</span>
            </div>
          </button>
          
          {profileDropdownOpen && (
            <div className="absolute right-0 top-full mt-2 w-48 bg-slate-900 border border-slate-800 rounded-lg shadow-xl py-1 z-50">
              <button
                onClick={handleLogout}
                className="w-full text-left px-4 py-2 text-xs flex items-center gap-2 text-rose-400 hover:bg-slate-800/60 transition"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span>Log Out</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
