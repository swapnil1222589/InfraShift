import React from 'react';

interface LoadingSkeletonProps {
  type: 'card' | 'tableRow' | 'chart';
  count?: number;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({ type, count = 1 }) => {
  const renderSkeleton = () => {
    switch (type) {
      case 'card':
        return (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 w-full h-full animate-pulse flex flex-col gap-3">
            <div className="h-4 bg-slate-800 rounded w-1/3"></div>
            <div className="h-8 bg-slate-800 rounded w-1/2 mt-2"></div>
            <div className="h-3 bg-slate-800 rounded w-full mt-auto"></div>
          </div>
        );
      case 'tableRow':
        return (
          <div className="flex items-center justify-between p-4 border-b border-slate-800 animate-pulse">
            <div className="h-4 bg-slate-800 rounded w-1/6"></div>
            <div className="h-4 bg-slate-800 rounded w-1/4"></div>
            <div className="h-4 bg-slate-800 rounded w-1/6"></div>
            <div className="h-4 bg-slate-800 rounded w-1/12"></div>
            <div className="h-4 bg-slate-800 rounded w-1/12"></div>
            <div className="h-4 bg-slate-800 rounded w-1/6"></div>
          </div>
        );
      case 'chart':
        return (
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 w-full animate-pulse h-80 flex flex-col">
            <div className="h-5 bg-slate-800 rounded w-1/4 mb-4"></div>
            <div className="flex-1 bg-slate-800/50 rounded-lg w-full"></div>
          </div>
        );
    }
  };

  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <React.Fragment key={i}>{renderSkeleton()}</React.Fragment>
      ))}
    </>
  );
};
