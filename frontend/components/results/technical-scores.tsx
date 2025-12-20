"use client"

import { useState } from 'react';
import { TechnicalScore } from '@/types/evaluation';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { RadarChart } from '@/components/charts/radar-chart';
import { getScoreColor } from '@/lib/utils';

interface TechnicalScoresProps {
  scores: TechnicalScore[];
}

export function TechnicalScores({ scores }: TechnicalScoresProps) {
  const [selectedVendorId, setSelectedVendorId] = useState(scores[0]?.vendor_id);

  const selectedScore = scores.find((s) => s.vendor_id === selectedVendorId);

  // Prepare radar chart data
  const radarData = selectedScore?.criteria.map((c) => ({
    criterion: c.name,
    score: c.score,
    weight: c.weight,
  })) || [];

  return (
    <div className="space-y-6">
      {/* Vendor Selector */}
      <div className="flex items-center gap-4">
        <label className="font-semibold">Select Vendor:</label>
        <Select value={selectedVendorId} onValueChange={setSelectedVendorId}>
          <SelectTrigger className="w-[300px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {scores.map((score) => (
              <SelectItem key={score.vendor_id} value={score.vendor_id}>
                {score.vendor_name} - {score.total_score.toFixed(1)}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {selectedScore && (
        <>
          {/* Overall Score */}
          <div className="border rounded-lg p-6 bg-card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">
                Technical Score: {selectedScore.vendor_name}
              </h3>
              <div className="text-right">
                <p className="text-sm text-muted-foreground">Total Score</p>
                <p className={`text-3xl font-bold ${getScoreColor(selectedScore.total_score)}`}>
                  {selectedScore.total_score.toFixed(1)}
                </p>
              </div>
            </div>
          </div>

          {/* Radar Chart */}
          <div className="border rounded-lg p-6 bg-card">
            <h4 className="font-semibold mb-4">Score Breakdown</h4>
            <RadarChart
              data={radarData}
              dataKeys={[
                { key: 'score', color: '#3b82f6', name: 'Score' },
              ]}
            />
          </div>

          {/* Criteria Details */}
          <div className="border rounded-lg p-6 bg-card">
            <h4 className="font-semibold mb-4">Detailed Analysis by Criteria</h4>
            <div className="space-y-4">
              {selectedScore.criteria.map((criterion, index) => (
                <CriterionCard key={index} criterion={criterion} />
              ))}
            </div>
          </div>

          {/* Overall Notes */}
          {selectedScore.overall_notes && (
            <div className="border rounded-lg p-6 bg-blue-50 border-blue-200">
              <h4 className="font-semibold mb-2 text-blue-900">
                Overall AI Assessment
              </h4>
              <p className="text-sm text-blue-800">{selectedScore.overall_notes}</p>
            </div>
          )}
        </>
      )}
    </div>
  );
}

interface CriterionCardProps {
  criterion: {
    name: string;
    weight: number;
    score: number;
    weighted_score: number;
    justification: string;
  };
}

function CriterionCard({ criterion }: CriterionCardProps) {
  return (
    <div className="border rounded-lg p-4">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h5 className="font-semibold">{criterion.name}</h5>
          <p className="text-xs text-muted-foreground">
            Weight: {criterion.weight}% | Weighted Score: {criterion.weighted_score.toFixed(1)}
          </p>
        </div>
        <Badge className={getScoreColor(criterion.score)}>
          {criterion.score.toFixed(1)}
        </Badge>
      </div>
      <Progress value={criterion.score} className="h-2 mb-3" />
      <div className="bg-muted p-3 rounded text-sm">
        <p className="font-medium text-xs text-muted-foreground mb-1">
          AI Justification:
        </p>
        <p>{criterion.justification}</p>
      </div>
    </div>
  );
}
