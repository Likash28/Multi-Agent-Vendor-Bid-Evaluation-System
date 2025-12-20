"use client"

import { FinancialAnalysis } from '@/types/evaluation';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { formatCurrency } from '@/lib/utils';
import { Trophy, TrendingUp, TrendingDown } from 'lucide-react';
import { BarChart } from '@/components/charts/bar-chart';

interface FinancialAnalysisProps {
  analyses: FinancialAnalysis[];
}

export function FinancialAnalysisComponent({ analyses }: FinancialAnalysisProps) {
  const l1Winner = analyses.find((a) => a.is_l1);

  // Prepare chart data
  const chartData = analyses.map((a) => ({
    name: a.vendor_name,
    quoted: a.quoted_price,
    adjusted: a.adjusted_price,
  }));

  return (
    <div className="space-y-6">
      {/* L1 Winner Highlight */}
      {l1Winner && (
        <div className="border-2 border-green-500 rounded-lg p-6 bg-green-50">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-green-500 rounded-full">
              <Trophy className="h-8 w-8 text-white" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold mb-2 text-green-900">
                L1 Winner - Lowest Bid
              </h2>
              <p className="text-xl mb-4">{l1Winner.vendor_name}</p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-green-700">Quoted Price</p>
                  <p className="text-2xl font-bold text-green-900">
                    {formatCurrency(l1Winner.quoted_price)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-green-700">Adjusted Price</p>
                  <p className="text-2xl font-bold text-green-900">
                    {formatCurrency(l1Winner.adjusted_price)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-green-700">Price Score</p>
                  <p className="text-2xl font-bold text-green-900">
                    {l1Winner.price_score.toFixed(1)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-green-700">Rank</p>
                  <p className="text-2xl font-bold text-green-900">#{l1Winner.rank}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Price Comparison Chart */}
      <div className="border rounded-lg p-6 bg-card">
        <h3 className="text-lg font-semibold mb-4">Price Comparison</h3>
        <BarChart
          data={chartData}
          dataKeys={[
            { key: 'quoted', color: '#3b82f6', name: 'Quoted Price' },
            { key: 'adjusted', color: '#10b981', name: 'Adjusted Price' },
          ]}
        />
      </div>

      {/* Detailed Table */}
      <div className="border rounded-lg overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Rank</TableHead>
              <TableHead>Vendor</TableHead>
              <TableHead className="text-right">Quoted Price</TableHead>
              <TableHead className="text-right">Adjustments</TableHead>
              <TableHead className="text-right">Adjusted Price</TableHead>
              <TableHead className="text-right">Price Score</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {analyses
              .sort((a, b) => a.rank - b.rank)
              .map((analysis) => (
                <TableRow
                  key={analysis.vendor_id}
                  className={analysis.is_l1 ? 'bg-green-50 font-semibold' : ''}
                >
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {analysis.is_l1 && <Trophy className="h-4 w-4 text-green-600" />}
                      #{analysis.rank}
                    </div>
                  </TableCell>
                  <TableCell>{analysis.vendor_name}</TableCell>
                  <TableCell className="text-right">
                    {formatCurrency(analysis.quoted_price)}
                  </TableCell>
                  <TableCell className="text-right">
                    {analysis.adjustments && analysis.adjustments.length > 0 ? (
                      <div className="flex items-center justify-end gap-1">
                        {analysis.adjusted_price > analysis.quoted_price ? (
                          <TrendingUp className="h-4 w-4 text-red-600" />
                        ) : (
                          <TrendingDown className="h-4 w-4 text-green-600" />
                        )}
                        {formatCurrency(
                          Math.abs(analysis.adjusted_price - analysis.quoted_price)
                        )}
                      </div>
                    ) : (
                      <span className="text-muted-foreground">None</span>
                    )}
                  </TableCell>
                  <TableCell className="text-right font-semibold">
                    {formatCurrency(analysis.adjusted_price)}
                  </TableCell>
                  <TableCell className="text-right">
                    <Badge>{analysis.price_score.toFixed(1)}</Badge>
                  </TableCell>
                  <TableCell>
                    {analysis.is_l1 && (
                      <Badge className="bg-green-600 text-white">L1</Badge>
                    )}
                  </TableCell>
                </TableRow>
              ))}
          </TableBody>
        </Table>
      </div>

      {/* Individual Vendor Details */}
      <div className="space-y-4">
        {analyses.map((analysis) => (
          <VendorFinancialDetail key={analysis.vendor_id} analysis={analysis} />
        ))}
      </div>
    </div>
  );
}

interface VendorFinancialDetailProps {
  analysis: FinancialAnalysis;
}

function VendorFinancialDetail({ analysis }: VendorFinancialDetailProps) {
  if (!analysis.adjustments || analysis.adjustments.length === 0) {
    return null;
  }

  return (
    <div className="border rounded-lg p-4 bg-card">
      <h4 className="font-semibold mb-3">{analysis.vendor_name} - Price Adjustments</h4>
      <div className="space-y-2">
        {analysis.adjustments.map((adj, index) => (
          <div key={index} className="flex items-start justify-between p-2 bg-muted rounded">
            <div>
              <p className="font-medium text-sm">{adj.type}</p>
              <p className="text-xs text-muted-foreground">{adj.reason}</p>
            </div>
            <Badge variant={adj.amount > 0 ? 'destructive' : 'secondary'}>
              {adj.amount > 0 ? '+' : ''}
              {formatCurrency(adj.amount)}
            </Badge>
          </div>
        ))}
      </div>
      {analysis.notes && (
        <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded">
          <p className="text-sm text-blue-800">{analysis.notes}</p>
        </div>
      )}
    </div>
  );
}
