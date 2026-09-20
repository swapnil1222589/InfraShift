import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Layers, ShieldCheck } from 'lucide-react';

export const Login: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    // Simulate network request
    setTimeout(() => {
      if (email === 'demo@infrashift.dev' && password === 'infrashift123') {
        login('email');
        navigate('/dashboard', { replace: true });
      } else {
        setError('Invalid demo credentials');
        setIsLoading(false);
      }
    }, 800);
  };

  const handleGithubLogin = () => {
    navigate('/github-authorize');
  };

  const fillDemoCredentials = () => {
    setEmail('demo@infrashift.dev');
    setPassword('infrashift123');
    setError('');
  };

  return (
    <div className="min-h-screen bg-slate-950 flex font-sans">
      {/* Left Branding Panel (Hidden on mobile) */}
      <div className="hidden lg:flex lg:w-1/2 bg-slate-900 border-r border-slate-800 flex-col justify-center items-center relative overflow-hidden">
        {/* Abstract Background Graphic */}
        <div className="absolute inset-0 z-0 opacity-20 pointer-events-none flex items-center justify-center">
          <div className="w-[800px] h-[800px] border border-amber-500/20 rounded-full flex items-center justify-center relative animate-[spin_60s_linear_infinite]">
            <div className="absolute top-0 w-3 h-3 bg-amber-500 rounded-full blur-[2px]" />
            <div className="w-[600px] h-[600px] border border-orange-500/20 rounded-full flex items-center justify-center relative animate-[spin_40s_linear_infinite_reverse]">
               <div className="absolute bottom-0 w-4 h-4 bg-orange-500 rounded-full blur-[2px]" />
               <div className="w-[400px] h-[400px] border border-sky-500/20 rounded-full relative animate-[spin_20s_linear_infinite]">
                 <div className="absolute right-0 top-1/2 w-2 h-2 bg-sky-500 rounded-full blur-[1px]" />
               </div>
            </div>
          </div>
        </div>

        <div className="z-10 max-w-lg px-12 text-center lg:text-left">
          <div className="flex items-center gap-3 mb-8 justify-center lg:justify-start">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-amber-500 via-orange-500 to-amber-600 flex items-center justify-center shadow-lg shadow-amber-500/20">
              <Layers className="w-7 h-7 text-slate-950" />
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-slate-100 tracking-tight text-3xl">InfraShift</span>
              <span className="text-sm font-mono text-amber-400 font-semibold tracking-wider uppercase mt-1">
                Pre-deploy intelligence
              </span>
            </div>
          </div>
          
          <h1 className="text-4xl lg:text-5xl font-bold text-slate-100 tracking-tight leading-tight mb-6">
            Know your infrastructure impact <span className="text-amber-500">before you deploy.</span>
          </h1>
          <p className="text-lg text-slate-400 leading-relaxed">
            Analyze code changes against AWS infrastructure, telemetry and historical deployments before they reach production.
          </p>
          
          <div className="mt-12 flex items-center gap-4 text-sm text-slate-500 font-mono bg-slate-950/50 p-4 rounded-lg border border-slate-800/80 w-max">
            <ShieldCheck className="w-5 h-5 text-emerald-500" />
            <span>Secure read-only AWS integration</span>
          </div>
        </div>
      </div>

      {/* Right Login Panel */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 relative">
        <div className="w-full max-w-md space-y-8">
          
          {/* Mobile Logo Header */}
          <div className="lg:hidden flex flex-col items-center justify-center mb-10 text-center">
            <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-amber-500 via-orange-500 to-amber-600 flex items-center justify-center shadow-lg shadow-amber-500/20 mb-4">
              <Layers className="w-7 h-7 text-slate-950" />
            </div>
            <span className="font-bold text-slate-100 tracking-tight text-3xl mb-1">InfraShift</span>
            <span className="text-sm font-mono text-amber-400 font-semibold tracking-wider uppercase">
              Pre-deploy intelligence
            </span>
          </div>

          <div className="text-center lg:text-left">
            <h2 className="text-2xl font-bold text-slate-100 tracking-tight">Welcome back</h2>
            <p className="text-sm text-slate-400 mt-2">Sign in to InfraShift</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-6">
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1.5 font-mono uppercase tracking-wider">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="engineer@infrashift.dev"
                  className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition text-sm"
                  required
                />
              </div>
              
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <label className="block text-xs font-semibold text-slate-300 font-mono uppercase tracking-wider">Password</label>
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500 transition text-sm font-mono"
                  required
                />
              </div>
            </div>

            {error && (
              <div className="p-3 rounded-md bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm flex items-center justify-center">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-2.5 px-4 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-slate-950 font-bold rounded-lg shadow-lg shadow-amber-500/20 transition-all active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {isLoading ? 'Signing in...' : 'Sign In'}
            </button>
            
            <button
              type="button"
              onClick={handleGithubLogin}
              disabled={isLoading}
              className="w-full py-2.5 px-4 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold rounded-lg border border-slate-700 transition flex items-center justify-center disabled:opacity-70 disabled:cursor-not-allowed"
            >
              Continue with GitHub
            </button>
          </form>

          <div className="pt-6 border-t border-slate-800 text-center">
            <button 
              onClick={fillDemoCredentials}
              className="text-xs font-mono text-slate-400 hover:text-amber-400 transition"
            >
              [ Use Demo Account ]
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
