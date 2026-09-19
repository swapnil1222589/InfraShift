import React from 'react';
import { Filter, ChevronDown } from 'lucide-react';

interface RecommendationFiltersProps {
  priorityFilter: string;
  setPriorityFilter: (val: string) => void;
  statusFilter: string;
  setStatusFilter: (val: string) => void;
  resourceFilter: string;
  setResourceFilter: (val: string) => void;
  availableResources: string[];
}

export const RecommendationFilters: React.FC<RecommendationFiltersProps> = ({
  priorityFilter,
  setPriorityFilter,
  statusFilter,
  setStatusFilter,
  resourceFilter,
  setResourceFilter,
  availableResources
}) => {
  return (
    <div className="flex flex-wrap items-center gap-4 bg-slate-900/50 p-4 rounded-xl border border-slate-800">
      <div className="flex items-center gap-2 text-slate-400 mr-2">
        <Filter className="w-4 h-4" />
        <span className="text-sm font-semibold uppercase tracking-wider">Filters</span>
      </div>

      <div className="flex items-center gap-2">
        <label className="text-xs text-slate-500 font-medium">Priority:</label>
        <div className="relative">
          <select 
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="appearance-none bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded px-3 py-1.5 pr-8 focus:outline-none focus:border-indigo-500 hover:border-slate-600 transition-colors"
          >
            <option value="All">All</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
          <ChevronDown className="w-4 h-4 text-slate-500 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <label className="text-xs text-slate-500 font-medium">Status:</label>
        <div className="relative">
          <select 
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="appearance-none bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded px-3 py-1.5 pr-8 focus:outline-none focus:border-indigo-500 hover:border-slate-600 transition-colors"
          >
            <option value="All">All</option>
            <option value="Open">Open</option>
            <option value="Under Review">Under Review</option>
            <option value="Completed">Completed</option>
          </select>
          <ChevronDown className="w-4 h-4 text-slate-500 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <label className="text-xs text-slate-500 font-medium">Resource:</label>
        <div className="relative">
          <select 
            value={resourceFilter}
            onChange={(e) => setResourceFilter(e.target.value)}
            className="appearance-none bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded px-3 py-1.5 pr-8 focus:outline-none focus:border-indigo-500 hover:border-slate-600 transition-colors"
          >
            <option value="All">All Resources</option>
            {availableResources.map(res => (
              <option key={res} value={res}>{res}</option>
            ))}
          </select>
          <ChevronDown className="w-4 h-4 text-slate-500 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        </div>
      </div>
    </div>
  );
};
