import React, { useState, useEffect } from 'react';
import { getHistory } from '../api/history';
import { AnalysisHistoryItem, HistorySummaryData } from '../types';
import { HistorySummary } from '../components/history/HistorySummary';
import { HistoryFilters } from '../components/history/HistoryFilters';
import { HistoryTable } from '../components/history/HistoryTable';
import { HistoryDetailsDrawer } from '../components/history/HistoryDetailsDrawer';
import { EmptyState, LoadingSkeleton, ErrorState } from '../components/common';

export const History: React.FC = () => {
  const [items, setItems] = useState<AnalysisHistoryItem[]>([]);
  const [summary, setSummary] = useState<HistorySummaryData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [riskFilter, setRiskFilter] = useState('All');
  const [outcomeFilter, setOutcomeFilter] = useState('All');
  
  const [selectedItem, setSelectedItem] = useState<AnalysisHistoryItem | null>(null);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getHistory();
      setItems(data.items);
      setSummary(data.summary);
    } catch (err) {
      setError('Unable to load analysis history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const filteredItems = items.filter(item => {
    const matchesSearch = 
      item.prTitle.toLowerCase().includes(searchTerm.toLowerCase()) || 
      item.repository.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.changedComponent.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.prNumber.toString().includes(searchTerm);
      
    const matchesStatus = statusFilter === 'All' || item.workflowStatus === statusFilter;
    const matchesRisk = riskFilter === 'All' || item.risk === riskFilter;
    const matchesOutcome = outcomeFilter === 'All' || item.outcomeStatus === outcomeFilter;
    
    return matchesSearch && matchesStatus && matchesRisk && matchesOutcome;
  });

  const clearFilters = () => {
    setSearchTerm('');
    setStatusFilter('All');
    setRiskFilter('All');
    setOutcomeFilter('All');
  };

  if (error) {
    return (
      <div className="py-20">
        <ErrorState error={error} onRetry={fetchHistory} />
      </div>
    );
  }

  return (
    <div className="space-y-6 h-[calc(100vh-6rem)] flex flex-col relative overflow-hidden">
      <div>
        <h1 className="text-xl font-bold text-slate-100 font-sans tracking-tight">
          Analysis History
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Review previous infrastructure impact analyses and their outcomes.
        </p>
      </div>

      {loading && !summary ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <LoadingSkeleton type="card" count={4} />
        </div>
      ) : summary && (
        <HistorySummary summary={summary} />
      )}

      <HistoryFilters 
        searchTerm={searchTerm} setSearchTerm={setSearchTerm}
        statusFilter={statusFilter} setStatusFilter={setStatusFilter}
        riskFilter={riskFilter} setRiskFilter={setRiskFilter}
        outcomeFilter={outcomeFilter} setOutcomeFilter={setOutcomeFilter}
      />

      <div className="flex-1 min-h-0 flex gap-6 relative">
        <div className="flex-1 overflow-y-auto">
          {loading && items.length === 0 ? (
            <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
              <LoadingSkeleton type="tableRow" count={5} />
            </div>
          ) : filteredItems.length === 0 ? (
            <EmptyState 
              title="No analyses found" 
              description="Try changing your filters or search terms." 
              actionLabel="Clear Filters"
              onAction={clearFilters}
            />
          ) : (
            <HistoryTable 
              items={filteredItems} 
              onRowClick={setSelectedItem} 
              selectedItemId={selectedItem?.id || null} 
            />
          )}
        </div>

        {selectedItem && (
          <HistoryDetailsDrawer 
            item={selectedItem} 
            onClose={() => setSelectedItem(null)} 
          />
        )}
      </div>
    </div>
  );
};
