"use client"

import { AgentProgress, AgentType } from '@/types/evaluation';
import { AGENT_LABELS, AGENT_DESCRIPTIONS } from '@/lib/constants';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { CheckCircle2, Circle, Loader2, XCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AgentStatusProps {
  agents: AgentProgress[];
}

export function AgentStatus({ agents }: AgentStatusProps) {
  return (
    <div className="space-y-4">
      {agents.map((agent) => (
        <AgentStatusCard key={agent.agent} agent={agent} />
      ))}
    </div>
  );
}

interface AgentStatusCardProps {
  agent: AgentProgress;
}

function AgentStatusCard({ agent }: AgentStatusCardProps) {
  const getStatusIcon = () => {
    switch (agent.status) {
      case 'completed':
        return <CheckCircle2 className="h-5 w-5 text-green-600" />;
      case 'running':
        return <Loader2 className="h-5 w-5 text-blue-600 animate-spin" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-600" />;
      default:
        return <Circle className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusBadge = () => {
    const variants: Record<string, any> = {
      pending: { variant: 'outline', label: 'Pending' },
      running: { variant: 'default', label: 'Running' },
      completed: { variant: 'secondary', label: 'Completed' },
      error: { variant: 'destructive', label: 'Error' },
    };

    const config = variants[agent.status];
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  return (
    <div
      className={cn(
        "border rounded-lg p-4 transition-all",
        agent.status === 'running' && "border-blue-500 bg-blue-50/50",
        agent.status === 'completed' && "border-green-500 bg-green-50/50",
        agent.status === 'error' && "border-red-500 bg-red-50/50",
        agent.status === 'pending' && "border-gray-200"
      )}
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-3">
          {getStatusIcon()}
          <div>
            <h3 className="font-semibold text-sm">{AGENT_LABELS[agent.agent]}</h3>
            <p className="text-xs text-muted-foreground">
              {AGENT_DESCRIPTIONS[agent.agent]}
            </p>
          </div>
        </div>
        {getStatusBadge()}
      </div>

      {agent.status === 'running' && (
        <div className="mt-3 space-y-2">
          <Progress value={agent.progress} className="h-2" />
          <p className="text-xs text-muted-foreground">{agent.message}</p>
        </div>
      )}

      {agent.status === 'completed' && agent.message && (
        <p className="text-xs text-green-700 mt-2">{agent.message}</p>
      )}

      {agent.status === 'error' && agent.error && (
        <p className="text-xs text-red-700 mt-2">{agent.error}</p>
      )}
    </div>
  );
}
