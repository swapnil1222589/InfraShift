import React from 'react';
import { Search, Filter, ChevronDown } from 'lucide-react';

interface HistoryFiltersProps {
  searchTerm: string;
  setSearchTerm: (term: string) => void;
  statusFilter: string;
  setStatusFilter: (status: string) => void;
  riskFilter: string;
  setRiskFilter: (risk: string) => void;
  outcomeFilter: string;
  setOutcomeFilter: (outcome: string) => void;
}

export const HistoryFilters: React.FC<HistoryFiltersProps> = ({
  searchTerm,
  setSearchTerm,
  statusFilter,
  setStatusFilter,
  riskFilter,
  setRiskFilter,
  outcomeFilter,
  setOutcomeFilter,
}) => {
  return (
    <div className="flex flex-wrap items-center gap-4 bg-slate-900/50 p-4 rounded-xl border border-slate-800">
      <div className="flex items-center gap-2 text-slate-400 mr-2 shrink-0">
        <Filter className="w-4 h-4" />
        <span className="text-sm font-semibold uppercase tracking-wider">Filters</span>
      </div>

      <div className="flex items-center gap-2 flex-1 min-w-[200px]">
        <div className="relative w-full">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            placeholder="Search PR, repository or resource..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-1.5 pl-9 text-sm text-slate-200 focus:outline-none focus:border-amber-500 hover:border-slate-600 transition-colors"
          />
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        <label className="text-xs text-slate-500 font-medium">Status:</label>
        <div className="relative">
          <select 
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="appearance-none bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded px-3 py-1.5 pr-8 focus:outline-none focus:border-indigo-500 hover:border-slate-600 transition-colors"
          >
            <option value="All">All</option>
            <option value="Completed">Completed</option>
            <option value="Running">Running</option>
            <option value="Failed">Failed</option>
            <option value="Pending">Pending</option>
          </select>
          <ChevronDown className="w-4 h-4 text-slate-500 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        <label className="text-xs text-slate-500 font-medium">Risk:</label>
        <div className="relative">
          <select 
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="appearance-none bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded px-3 py-1.5 pr-8 focus:outline-none focus:border-indigo-500 hover:border-slate-600 transition-colors"
          >
            <option value="All">All</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
            <option value="CRITICAL">Critical</option>
          </select>
          <ChevronDown className="w-4 h-4 text-slate-500 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        </div>
      </div>
      
      <div className="flex items-center gap-2 shrink-0">
        <label className="text-xs text-slate-500 font-medium">Outcome:</label>
        <div className="relative">
          <select 
            value={outcomeFilter}
            onChange={(e) => setOutcomeFilter(e.target.value)}
            className="appearance-none bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded px-3 py-1.5 pr-8 focus:outline-none focus:border-indigo-500 hover:border-slate-600 transition-colors"
          >
            <option value="All">All</option>
            <option value="Validated">Validated</option>
            <option value="Not Validated">Not Validated</option>
            <option value="Awaiting Deployment">Awaiting Deployment</option>
          </select>
          <ChevronDown className="w-4 h-4 text-slate-500 absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        </div>
      </div>
    </div>
  );
};
