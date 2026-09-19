import React from 'react';
import { Link, useParams } from 'react-router-dom';
import { CostForecast } from '../../types/forecast';
import { Card } from '../common/Card';
import { ConfidenceMeter } from '../common/ConfidenceMeter';
import { DollarSign, TrendingUp, HelpCircle, Layers, Server } from 'lucide-react';

interface CostForecastCardProps {
  cost: CostForecast;
}

export const CostForecastCard: React.FC<CostForecastCardProps> = ({ cost }) => {
  const { id } = useParams<{ id: string }>();

  return (
    <Card
      title="Cost Forecast Range"
      subtitle="Monthly AWS billing delta projection"
      badge={<DollarSign className="w-4 h-4 text-orange-400" />}
      headerAction={<ConfidenceMeter score={cost.confidence} />}
    >
      <div className="space-y-4">
        {/* Main Forecast Range Display */}
        <div className="p-4 rounded-lg bg-slate-950/80 border border-slate-800">
          <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-2">
            <div>
              <span className="text-[10px] font-mono uppercase text-slate-500 block">
                PROJECTED MONTHLY COST DELTA
              </span>
              <div className="text-2xl sm:text-3xl font-bold font-mono text-orange-400 mt-1">
                ${cost.projectedMonthlyMinUsd - cost.currentMonthlyBaselineUsd} – ${cost.projectedMonthlyMaxUsd - cost.currentMonthlyBaselineUsd}
                <span className="text-xs sm:text-sm text-slate-400 font-sans ml-2">/ month</span>
              </div>
            </div>

            <div className="text-right font-mono">
              <span className="text-xs px-2 py-0.5 rounded bg-orange-950/80 text-orange-300 border border-orange-800 font-semibold">
                +{cost.percentageChangeMin}% to +{cost.percentageChangeMax}%
              </span>
              <span className="text-[10px] text-slate-500 block mt-1">Relative to baseline</span>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800/80 grid grid-cols-2 gap-4 text-xs font-mono">
            <div>
              <span className="text-slate-500 text-[10px] block uppercase">Current Baseline</span>
              <span className="text-slate-200 font-medium">${cost.currentMonthlyBaselineUsd}.00 / mo</span>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] block uppercase">Projected Total</span>
              <span className="text-amber-400 font-medium">${cost.projectedMonthlyMinUsd} – ${cost.projectedMonthlyMaxUsd} / mo</span>
            </div>
          </div>
        </div>

        {/* Cost Drivers Breakdown */}
        <div>
          <span className="text-[11px] font-mono uppercase text-slate-400 font-semibold block mb-2">
            COST DRIVER ATTRIBUTION:
          </span>
          <div className="space-y-2">
            {cost.driverBreakdown.map((item, idx) => (
              <div
                key={idx}
                className="p-3 rounded-lg bg-slate-950/50 border border-slate-800 hover:border-slate-700 transition text-xs"
              >
                <div className="flex items-center justify-between font-mono">
                  <span className="font-semibold text-slate-200 truncate pr-2">{item.awsService}</span>
                  <span className="text-orange-400 font-bold shrink-0">
                    +${item.estimatedDeltaUsd.toFixed(2)}/mo
                  </span>
                </div>
                <div className="text-[11px] font-mono text-slate-400 mt-0.5 truncate">
                  {item.resource}
                </div>
                <p className="text-[11px] text-slate-400 mt-1 leading-snug">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>

        <div className="pt-2">
          <Link
            to={`/analyses/${id}/evidence`}
            className="w-full inline-flex justify-center items-center gap-2 px-4 py-2 text-xs font-medium text-slate-300 bg-slate-800 hover:bg-slate-700 hover:text-white border border-slate-700 rounded-md transition"
          >
            <HelpCircle className="w-3.5 h-3.5" />
            Why This Forecast?
          </Link>
        </div>
      </div>
    </Card>
  );
};
