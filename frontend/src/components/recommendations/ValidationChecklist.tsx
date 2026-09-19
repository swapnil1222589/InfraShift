import React, { useState } from 'react';
import { Card } from '../common/Card';
import { ListChecks } from 'lucide-react';

export const ValidationChecklist: React.FC = () => {
  const [tasks, setTasks] = useState([
    { id: 1, text: 'Run load test against staging DynamoDB', completed: false },
    { id: 2, text: 'Review DynamoDB read capacity auto-scaling policies', completed: false },
    { id: 3, text: 'Verify Lambda timeout and memory settings', completed: false },
    { id: 4, text: 'Monitor downstream API Gateway latency', completed: false },
    { id: 5, text: 'Confirm CloudWatch alarms for throttle events are active', completed: false },
  ]);

  const toggleTask = (id: number) => {
    setTasks(tasks.map(t => t.id === id ? { ...t, completed: !t.completed } : t));
  };

  const completedCount = tasks.filter(t => t.completed).length;

  return (
    <Card className="flex flex-col gap-4">
      <div className="flex justify-between items-center border-b border-slate-700/50 pb-3">
        <div className="flex items-center gap-2">
          <ListChecks className="w-5 h-5 text-indigo-400" />
          <h3 className="text-lg font-semibold text-slate-100">Pre-deployment Validation Checklist</h3>
        </div>
        <span className="text-sm font-medium px-3 py-1 bg-indigo-500/10 text-indigo-400 rounded-full border border-indigo-500/20">
          {completedCount} of {tasks.length} completed
        </span>
      </div>

      <div className="space-y-1">
        {tasks.map(task => (
          <label 
            key={task.id} 
            className={`flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-colors ${
              task.completed ? 'bg-slate-800/30 text-slate-500 line-through' : 'bg-slate-800/50 text-slate-200 hover:bg-slate-700/50'
            }`}
          >
            <input 
              type="checkbox" 
              checked={task.completed}
              onChange={() => toggleTask(task.id)}
              className="mt-0.5 w-4 h-4 rounded border-slate-600 text-indigo-600 focus:ring-indigo-500 focus:ring-offset-slate-900 bg-slate-800"
            />
            <span className="text-sm select-none">{task.text}</span>
          </label>
        ))}
      </div>
      
      <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden mt-2">
        <div 
          className="h-full bg-indigo-500 transition-all duration-300" 
          style={{ width: `${(completedCount / tasks.length) * 100}%` }} 
        />
      </div>
    </Card>
  );
};
