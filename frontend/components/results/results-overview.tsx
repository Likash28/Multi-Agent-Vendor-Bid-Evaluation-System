"use client"

import { EvaluationResults } from '@/types/evaluation';
import { Badge } from '@/components/ui/badge';
import { formatDuration, formatDateTime } from '@/lib/utils';
import { Trophy, Users, CheckCircle, XCircle, Clock, BarChart3 } from 'lucide-react';
import { ComparisonChart } from '@/components/charts/comparison-chart';

interface ResultsOverviewProps {
  results: EvaluationResults;
}

export function ResultsOverview({ results }: ResultsOverviewProps) {
  const winner = results.rankings.find(r => r.is_winner);
  const qualified = results.rankings.filter(r => r.compliance_status === 'PASS').length;
  const disqualified = results.rankings.filter(r => r.compliance_status === 'FAIL').length;

  const chartData = results.rankings.map(r => ({
    vendor: r.vendor_name,
    compliance: r.compliance_score,
    technical: r.technical_score,
    financial: r.financial_score,
    total: r.total_score,
    isWinner: r.is_winner,
  }));

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          icon={<Users className="h-5 w-5" />}
          label="Total Bids"
          value={results.rankings.length.toString()}
          color="blue"
        />
        <StatCard
          icon={<CheckCircle className="h-5 w-5" />}
          label="Qualified"
          value={qualified.toString()}
          color="green"
        />
        <StatCard
          icon={<XCircle className="h-5 w-5" />}
          label="Disqualified"
          value={disqualified.toString()}
          color="red"
        />
        <StatCard
          icon={<BarChart3 className="h-5 w-5" />}
          label="Method"
          value={results.method}
          color="purple"
        />
      </div>

      {/* Winner Card */}
      {winner && (
        <div className="border-2 border-yellow-400 rounded-lg p-6 bg-gradient-to-r from-yellow-50 to-amber-50">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-yellow-400 rounded-full">
              <Trophy className="h-8 w-8 text-white" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold mb-2">Preferred Bidder</h2>
              <p className="text-xl mb-4">{winner.vendor_name}</p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div>
                  <p className="text-sm text-muted-foreground">Rank</p>
                  <p className="text-2xl font-bold">#{winner.rank}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Total Score</p>
                  <p className="text-2xl font-bold">{winner.total_score.toFixed(1)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Technical</p>
                  <p className="text-2xl font-bold">{winner.technical_score.toFixed(1)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Financial</p>
                  <p className="text-2xl font-bold">{winner.financial_score.toFixed(1)}</p>
                </div>
              </div>
              <Badge className="bg-green-600 text-white">
                {winner.compliance_status}
              </Badge>
            </div>
          </div>
        </div>
      )}

      {/* Score Distribution Chart */}
      <div className="border rounded-lg p-6 bg-card">
        <h3 className="text-lg font-semibold mb-4">Vendor Score Distribution</h3>
        <ComparisonChart data={chartData} />
      </div>

      {/* Processing Info */}
      {results.processing_time && results.completed_at && (
        <div className="border rounded-lg p-4 bg-card flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Clock className="h-5 w-5 text-muted-foreground" />
            <div>
              <p className="text-sm font-medium">Processing Time</p>
              <p className="text-xs text-muted-foreground">
                {formatDuration(results.processing_time)}
              </p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm font-medium">Completed At</p>
            <p className="text-xs text-muted-foreground">
              {formatDateTime(results.completed_at)}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  color: 'blue' | 'green' | 'red' | 'purple';
}

function StatCard({ icon, label, value, color }: StatCardProps) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    red: 'bg-red-100 text-red-600',
    purple: 'bg-purple-100 text-purple-600',
  };

  return (
    <div className="border rounded-lg p-4 bg-card">
      <div className="flex items-center gap-3 mb-2">
        <div className={`p-2 rounded-lg ${colorClasses[color]}`}>
          {icon}
        </div>
        <p className="text-sm text-muted-foreground">{label}</p>
      </div>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  );
}
