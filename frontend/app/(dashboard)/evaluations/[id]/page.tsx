"use client"

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Evaluation } from '@/types/evaluation';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { getStatusColor, formatDateTime } from '@/lib/utils';
import {
  AlertCircle,
  Play,
  Edit,
  FileText,
  Clock,
  CheckCircle,
  XCircle,
} from 'lucide-react';

interface EvaluationDetailPageProps {
  params: {
    id: string;
  };
}

export default function EvaluationDetailPage({ params }: EvaluationDetailPageProps) {
  const router = useRouter();
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEvaluation = async () => {
      try {
        const response = await fetch(`/api/evaluations/${params.id}`);
        if (!response.ok) {
          throw new Error('Failed to fetch evaluation');
        }
        const data = await response.json();
        setEvaluation(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setIsLoading(false);
      }
    };

    fetchEvaluation();
  }, [params.id]);

  if (isLoading) {
    return <LoadingSkeleton />;
  }

  if (error || !evaluation) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="border border-red-200 rounded-lg p-6 bg-red-50">
          <div className="flex items-center gap-3">
            <AlertCircle className="h-8 w-8 text-red-600" />
            <div>
              <h2 className="text-xl font-semibold text-red-900">Error</h2>
              <p className="text-sm text-red-700">{error || 'Evaluation not found'}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const handleStartProcessing = async () => {
    try {
      const response = await fetch(`/api/evaluations/${params.id}/start`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error('Failed to start evaluation');
      }
      router.push(`/evaluations/${params.id}/processing`);
    } catch (err) {
      console.error('Error starting evaluation:', err);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">{evaluation.title}</h1>
          {evaluation.description && (
            <p className="text-muted-foreground">{evaluation.description}</p>
          )}
        </div>
        <Badge className={getStatusColor(evaluation.status)}>{evaluation.status}</Badge>
      </div>

      {/* Details Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <DetailCard
          icon={<FileText className="h-5 w-5" />}
          label="Evaluation Method"
          value={evaluation.method}
        />
        <DetailCard
          icon={<Clock className="h-5 w-5" />}
          label="Created At"
          value={formatDateTime(evaluation.created_at)}
        />
        {evaluation.technical_weight && (
          <DetailCard
            icon={<CheckCircle className="h-5 w-5" />}
            label="Technical Weight"
            value={`${evaluation.technical_weight}%`}
          />
        )}
        {evaluation.financial_weight && (
          <DetailCard
            icon={<CheckCircle className="h-5 w-5" />}
            label="Financial Weight"
            value={`${evaluation.financial_weight}%`}
          />
        )}
        {evaluation.vendor_count && (
          <DetailCard
            icon={<FileText className="h-5 w-5" />}
            label="Number of Bids"
            value={evaluation.vendor_count.toString()}
          />
        )}
        {evaluation.completed_at && (
          <DetailCard
            icon={<CheckCircle className="h-5 w-5" />}
            label="Completed At"
            value={formatDateTime(evaluation.completed_at)}
          />
        )}
      </div>

      {/* Status-based Content */}
      {evaluation.status === 'DRAFT' && (
        <div className="border rounded-lg p-6 bg-card">
          <h2 className="text-lg font-semibold mb-4">Ready to Start</h2>
          <p className="text-sm text-muted-foreground mb-4">
            This evaluation is in draft mode. You can edit the configuration or start
            the AI-powered evaluation process.
          </p>
          <div className="flex gap-3">
            <Button onClick={() => router.push(`/evaluations/${params.id}/edit`)}>
              <Edit className="h-4 w-4 mr-2" />
              Edit Configuration
            </Button>
            <Button onClick={handleStartProcessing}>
              <Play className="h-4 w-4 mr-2" />
              Start Evaluation
            </Button>
          </div>
        </div>
      )}

      {evaluation.status === 'PROCESSING' && (
        <div className="border border-blue-200 rounded-lg p-6 bg-blue-50">
          <div className="flex items-center gap-3 mb-4">
            <div className="h-2 w-2 bg-blue-600 rounded-full animate-pulse" />
            <h2 className="text-lg font-semibold text-blue-900">Processing in Progress</h2>
          </div>
          <p className="text-sm text-blue-700 mb-4">
            The multi-agent AI system is currently evaluating vendor bids.
          </p>
          <Button onClick={() => router.push(`/evaluations/${params.id}/processing`)}>
            View Processing Status
          </Button>
        </div>
      )}

      {evaluation.status === 'COMPLETED' && (
        <div className="border border-green-200 rounded-lg p-6 bg-green-50">
          <div className="flex items-center gap-3 mb-4">
            <CheckCircle className="h-6 w-6 text-green-600" />
            <h2 className="text-lg font-semibold text-green-900">
              Evaluation Complete
            </h2>
          </div>
          <p className="text-sm text-green-700 mb-4">
            The evaluation has been completed successfully. View the detailed results and
            AI-generated report.
          </p>
          <Button onClick={() => router.push(`/evaluations/${params.id}/results`)}>
            View Results
          </Button>
        </div>
      )}

      {evaluation.status === 'FAILED' && (
        <div className="border border-red-200 rounded-lg p-6 bg-red-50">
          <div className="flex items-center gap-3 mb-4">
            <XCircle className="h-6 w-6 text-red-600" />
            <h2 className="text-lg font-semibold text-red-900">Evaluation Failed</h2>
          </div>
          <p className="text-sm text-red-700 mb-4">
            The evaluation process encountered an error. Please review the configuration
            and try again.
          </p>
          <Button variant="destructive" onClick={() => router.push(`/evaluations`)}>
            Return to Evaluations
          </Button>
        </div>
      )}
    </div>
  );
}

interface DetailCardProps {
  icon: React.ReactNode;
  label: string;
  value: string;
}

function DetailCard({ icon, label, value }: DetailCardProps) {
  return (
    <div className="border rounded-lg p-4 bg-card">
      <div className="flex items-center gap-2 mb-2 text-muted-foreground">
        {icon}
        <span className="text-sm">{label}</span>
      </div>
      <p className="text-lg font-semibold">{value}</p>
    </div>
  );
}

function LoadingSkeleton() {
  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div>
        <Skeleton className="h-10 w-96 mb-2" />
        <Skeleton className="h-4 w-64" />
      </div>
      <div className="grid grid-cols-2 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <Skeleton key={i} className="h-24" />
        ))}
      </div>
      <Skeleton className="h-48 w-full" />
    </div>
  );
}
