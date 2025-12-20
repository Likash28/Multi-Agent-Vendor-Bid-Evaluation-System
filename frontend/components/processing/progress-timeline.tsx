"use client"

import { useEffect, useRef } from 'react';
import { ProcessingEvent } from '@/types/evaluation';
import { AGENT_LABELS } from '@/lib/constants';
import { formatTime } from '@/lib/utils';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';

interface ProgressTimelineProps {
  events: ProcessingEvent[];
}

export function ProgressTimeline({ events }: ProgressTimelineProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest entry
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [events]);

  return (
    <div className="border rounded-lg">
      <div className="bg-muted px-4 py-2 border-b">
        <h3 className="font-semibold text-sm">Processing Timeline</h3>
      </div>
      <ScrollArea className="h-[400px]">
        <div className="p-4 space-y-3">
          {events.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              No events yet. Processing will start soon...
            </p>
          ) : (
            events.map((event, index) => (
              <TimelineEvent key={index} event={event} />
            ))
          )}
          <div ref={bottomRef} />
        </div>
      </ScrollArea>
    </div>
  );
}

interface TimelineEventProps {
  event: ProcessingEvent;
}

function TimelineEvent({ event }: TimelineEventProps) {
  const getLevelColor = () => {
    switch (event.level) {
      case 'success':
        return 'text-green-600';
      case 'error':
        return 'text-red-600';
      case 'warning':
        return 'text-yellow-600';
      default:
        return 'text-blue-600';
    }
  };

  const getLevelDot = () => {
    switch (event.level) {
      case 'success':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      case 'warning':
        return 'bg-yellow-500';
      default:
        return 'bg-blue-500';
    }
  };

  return (
    <div className="flex gap-3">
      <div className="flex flex-col items-center">
        <div className={cn("w-2 h-2 rounded-full mt-1.5", getLevelDot())} />
        <div className="w-px h-full bg-border mt-1" />
      </div>
      <div className="flex-1 pb-4">
        <div className="flex items-baseline gap-2 mb-1">
          <span className="text-xs font-mono text-muted-foreground">
            {formatTime(event.timestamp)}
          </span>
          <span className={cn("text-xs font-medium", getLevelColor())}>
            {AGENT_LABELS[event.agent]}
          </span>
        </div>
        <p className="text-sm">{event.message}</p>
        {event.action && (
          <p className="text-xs text-muted-foreground mt-0.5">
            Action: {event.action}
          </p>
        )}
      </div>
    </div>
  );
}
