import React from 'react';
import { ToastMessage } from '../../contexts/ToastContext';
import { X, CheckCircle2, AlertCircle, Info } from 'lucide-react';

interface ToastProps {
  toast: ToastMessage;
  onClose: () => void;
}

export const Toast: React.FC<ToastProps> = ({ toast, onClose }) => {
  const getIcon = () => {
    switch (toast.type) {
      case 'success':
        return <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-rose-400" />;
      case 'info':
      default:
        return <Info className="w-4 h-4 text-indigo-400" />;
    }
  };

  const getBorder = () => {
    switch (toast.type) {
      case 'success': return 'border-emerald-500/30';
      case 'error': return 'border-rose-500/30';
      case 'info':
      default: return 'border-indigo-500/30';
    }
  };

  return (
    <div className={`flex items-center gap-3 bg-slate-900 border ${getBorder()} p-3 rounded-lg shadow-xl shadow-slate-950/50 min-w-[300px] animate-in slide-in-from-right-8 fade-in duration-300`}>
      {getIcon()}
      <p className="flex-1 text-sm font-medium text-slate-200">{toast.message}</p>
      <button onClick={onClose} className="p-1 hover:bg-slate-800 rounded text-slate-500 hover:text-slate-300 transition-colors">
        <X className="w-4 h-4" />
      </button>
    </div>
  );
};
