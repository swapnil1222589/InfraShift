import React from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline' | 'danger' | 'ghost' | 'aws';
  size?: 'sm' | 'md' | 'lg';
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  loading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'secondary',
  size = 'md',
  icon,
  iconPosition = 'left',
  loading = false,
  className = '',
  disabled,
  ...props
}) => {
  const base =
    'inline-flex items-center justify-center font-medium transition-all duration-150 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-950 disabled:opacity-50 disabled:cursor-not-allowed select-none cursor-pointer';

  const variants = {
    primary:
      'bg-amber-500 hover:bg-amber-400 text-slate-950 font-semibold focus:ring-amber-500 shadow-sm active:translate-y-px',
    aws:
      'bg-orange-500 hover:bg-orange-400 text-slate-950 font-semibold focus:ring-orange-500 shadow-sm active:translate-y-px',
    secondary:
      'bg-slate-800 hover:bg-slate-700 text-slate-100 border border-slate-700/80 focus:ring-slate-600',
    outline:
      'bg-transparent hover:bg-slate-800 text-slate-200 border border-slate-700 focus:ring-slate-600',
    danger:
      'bg-rose-900/40 hover:bg-rose-900/60 text-rose-200 border border-rose-800 focus:ring-rose-500',
    ghost:
      'bg-transparent hover:bg-slate-800 text-slate-300 hover:text-white focus:ring-slate-700',
  };

  const sizes = {
    sm: 'text-xs px-2.5 py-1.5 gap-1.5',
    md: 'text-sm px-3.5 py-2 gap-2',
    lg: 'text-base px-5 py-2.5 gap-2.5',
  };

  return (
    <button
      className={`${base} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-1.5" />
      ) : (
        icon && iconPosition === 'left' && <span className="shrink-0">{icon}</span>
      )}
      <span>{children}</span>
      {!loading && icon && iconPosition === 'right' && <span className="shrink-0">{icon}</span>}
    </button>
  );
};
