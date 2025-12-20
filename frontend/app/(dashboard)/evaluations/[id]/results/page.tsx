"use client"

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { EvaluationResults } from '@/types/evaluation';
import { ReportContent } from '@/types/report';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ResultsOverview } from '@/components/results/results-overview';
import { RankingsTable } from '@/components/results/rankings-table';
import { ComplianceResults } from '@/components/results/compliance-results';
import { TechnicalScores } from '@/components/results/technical-scores';
import { FinancialAnalysisComponent } from '@/components/results/financial-analysis';
import { ReportViewer } from '@/components/results/report-viewer';
import { Skeleton } from '@/components/ui/skeleton';
import { AlertCircle } from 'lucide-react';

interface ResultsPageProps {
  params: {
    id: string;
  };
}

export default function ResultsPage({ params }: ResultsPageProps) {
  const router = useRouter();
  const [results, setResults] = useState<EvaluationResults | null>(null);
  const [report, setReport] = useState<ReportContent | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const response = await fetch(`/api/evaluations/${params.id}/results`);
        if (!response.ok) {
          throw new Error('Failed to fetch results');
        }
        const data = await response.json();
        setResults(data);

        // Fetch report
        const reportResponse = await fetch(`/api/evaluations/${params.id}/report`);
        if (reportResponse.ok) {
          const reportData = await reportResponse.json();
          setReport(reportData);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setIsLoading(false);
      }
    };

    fetchResults();
  }, [params.id]);

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  if (error || !results) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="border border-red-200 rounded-lg p-6 bg-red-50">
          <div className="flex items-center gap-3">
            <AlertCircle className="h-8 w-8 text-red-600" />
            <div>
              <h2 className="text-xl font-semibold text-red-900">Error Loading Results</h2>
              <p className="text-sm text-red-700">{error || 'Unknown error'}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold mb-2">Evaluation Results</h1>
        <p className="text-muted-foreground">
          Comprehensive AI-powered vendor bid evaluation results
        </p>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="rankings">Rankings</TabsTrigger>
          <TabsTrigger value="compliance">Compliance</TabsTrigger>
          <TabsTrigger value="technical">Technical</TabsTrigger>
          <TabsTrigger value="financial">Financial</TabsTrigger>
          {report && <TabsTrigger value="report">Report</TabsTrigger>}
        </TabsList>

        <TabsContent value="overview">
          <ResultsOverview results={results} />
        </TabsContent>

        <TabsContent value="rankings">
          <div className="border rounded-lg p-6 bg-card">
            <h2 className="text-lg font-semibold mb-4">Vendor Rankings</h2>
            <RankingsTable rankings={results.rankings} />
          </div>
        </TabsContent>

        <TabsContent value="compliance">
          <div className="space-y-4">
            <div className="border rounded-lg p-4 bg-card">
              <h2 className="text-lg font-semibold">Compliance Analysis</h2>
              <p className="text-sm text-muted-foreground">
                Document verification and requirement compliance status
              </p>
            </div>
            <ComplianceResults results={results.compliance} />
          </div>
        </TabsContent>

        <TabsContent value="technical">
          <div className="space-y-4">
            <div className="border rounded-lg p-4 bg-card">
              <h2 className="text-lg font-semibold">Technical Evaluation</h2>
              <p className="text-sm text-muted-foreground">
                AI-powered scoring of technical proposals and capabilities
              </p>
            </div>
            <TechnicalScores scores={results.technical} />
          </div>
        </TabsContent>

        <TabsContent value="financial">
          <div className="space-y-4">
            <div className="border rounded-lg p-4 bg-card">
              <h2 className="text-lg font-semibold">Financial Analysis</h2>
              <p className="text-sm text-muted-foreground">
                Price evaluation and L1 determination
              </p>
            </div>
            <FinancialAnalysisComponent analyses={results.financial} />
          </div>
        </TabsContent>

        {report && (
          <TabsContent value="report">
            <div className="border rounded-lg p-6 bg-card">
              <ReportViewer report={report} evaluationId={params.id} />
            </div>
          </TabsContent>
        )}
      </Tabs>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      <div>
        <Skeleton className="h-8 w-64 mb-2" />
        <Skeleton className="h-4 w-96" />
      </div>
      <Skeleton className="h-10 w-full" />
      <div className="grid grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} className="h-32" />
        ))}
      </div>
      <Skeleton className="h-96 w-full" />
    </div>
  );
}
