"use client"

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useWebSocket } from '@/hooks/use-websocket';
import { AgentProgress, ProcessingEvent, AgentType } from '@/types/evaluation';
import { AgentStatus } from './agent-status';
import { ProgressTimeline } from './progress-timeline';
import { LiveLog } from './live-log';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { formatDuration } from '@/lib/utils';
import { AlertCircle, CheckCircle2, XCircle } from 'lucide-react';

interface ProcessingViewProps {
  evaluationId: string;
}

export function ProcessingView({ evaluationId }: ProcessingViewProps) {
  const router = useRouter();
  const [overallProgress, setOverallProgress] = useState(0);
  const [agents, setAgents] = useState<AgentProgress[]>(initializeAgents());
  const [events, setEvents] = useState<ProcessingEvent[]>([]);
  const [startTime] = useState(Date.now());
  const [isCompleted, setIsCompleted] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string>('');

  const handleAgentUpdate = useCallback((agentUpdate: AgentProgress) => {
    setAgents(prev => {
      const index = prev.findIndex(a => a.agent === agentUpdate.agent);
      if (index === -1) return prev;

      const updated = [...prev];
      updated[index] = agentUpdate;
      return updated;
    });
  }, []);

  const handleProgress = useCallback((progress: number) => {
    setOverallProgress(progress);
  }, []);

  const handleLog = useCallback((event: ProcessingEvent) => {
    setEvents(prev => [...prev, event]);
  }, []);

  const handleCompletion = useCallback(() => {
    setIsCompleted(true);
    setTimeout(() => {
      router.push(`/evaluations/${evaluationId}/results`);
    }, 2000);
  }, [evaluationId, router]);

  const handleError = useCallback((error: string) => {
    setHasError(true);
    setErrorMessage(error);
  }, []);

  const { isConnected } = useWebSocket({
    evaluationId,
    onAgentUpdate: handleAgentUpdate,
    onProgress: handleProgress,
    onLog: handleLog,
    onCompletion: handleCompletion,
    onError: handleError,
  });

  const handleCancel = async () => {
    try {
      await fetch(`/api/evaluations/${evaluationId}/cancel`, {
        method: 'POST',
      });
      router.push(`/evaluations/${evaluationId}`);
    } catch (error) {
      console.error('Failed to cancel evaluation:', error);
    }
  };

  const elapsedTime = Date.now() - startTime;
  const estimatedTotal = overallProgress > 0 ? (elapsedTime / overallProgress) * 100 : 0;
  const remainingTime = estimatedTotal - elapsedTime;

  if (hasError) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="border border-red-200 rounded-lg p-6 bg-red-50">
          <div className="flex items-center gap-3 mb-4">
            <XCircle className="h-8 w-8 text-red-600" />
            <div>
              <h2 className="text-xl font-semibold text-red-900">Processing Failed</h2>
              <p className="text-sm text-red-700">{errorMessage}</p>
            </div>
          </div>
          <Button onClick={() => router.push(`/evaluations/${evaluationId}`)}>
            Return to Evaluation
          </Button>
        </div>
      </div>
    );
  }

  if (isCompleted) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="border border-green-200 rounded-lg p-6 bg-green-50">
          <div className="flex items-center gap-3 mb-4">
            <CheckCircle2 className="h-8 w-8 text-green-600" />
            <div>
              <h2 className="text-xl font-semibold text-green-900">Processing Complete!</h2>
              <p className="text-sm text-green-700">
                Redirecting to results...
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Processing Evaluation</h1>
          <p className="text-sm text-muted-foreground">
            Multi-agent AI system is evaluating vendor bids
          </p>
        </div>
        <div className="flex items-center gap-4">
          {!isConnected && (
            <div className="flex items-center gap-2 text-yellow-600">
              <AlertCircle className="h-4 w-4" />
              <span className="text-sm">Reconnecting...</span>
            </div>
          )}
          <Button variant="outline" onClick={handleCancel}>
            Cancel Evaluation
          </Button>
        </div>
      </div>

      {/* Overall Progress */}
      <div className="border rounded-lg p-6 bg-card">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold">Overall Progress</h2>
            <p className="text-sm text-muted-foreground">
              {overallProgress.toFixed(0)}% complete
            </p>
          </div>
          <div className="text-right">
            <p className="text-sm text-muted-foreground">Elapsed Time</p>
            <p className="text-lg font-semibold">{formatDuration(elapsedTime)}</p>
            {remainingTime > 0 && (
              <p className="text-xs text-muted-foreground">
                ~{formatDuration(remainingTime)} remaining
              </p>
            )}
          </div>
        </div>
        <Progress value={overallProgress} className="h-3" />
      </div>

      {/* Agent Status */}
      <div className="border rounded-lg p-6 bg-card">
        <h2 className="text-lg font-semibold mb-4">Agent Status</h2>
        <AgentStatus agents={agents} />
      </div>

      {/* Timeline and Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ProgressTimeline events={events} />
        <LiveLog events={events} />
      </div>
    </div>
  );
}

function initializeAgents(): AgentProgress[] {
  const agentTypes: AgentType[] = [
    'document_parser',
    'compliance_checker',
    'technical_evaluator',
    'financial_evaluator',
    'comparison_agent',
    'report_generator',
  ];

  return agentTypes.map(agent => ({
    agent,
    status: 'pending',
    progress: 0,
    message: 'Waiting to start...',
  }));
}
