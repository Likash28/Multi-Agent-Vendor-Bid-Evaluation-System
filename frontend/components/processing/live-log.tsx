"use client"

import { useEffect, useRef } from 'react';
import { ProcessingEvent } from '@/types/evaluation';
import { formatTime } from '@/lib/utils';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';

interface LiveLogProps {
  events: ProcessingEvent[];
}

export function LiveLog({ events }: LiveLogProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest entry
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [events]);

  return (
    <div className="border rounded-lg bg-slate-950">
      <div className="bg-slate-900 px-4 py-2 border-b border-slate-800 flex items-center justify-between">
        <h3 className="font-semibold text-sm text-slate-200">System Log</h3>
        <div className="flex gap-2">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <div className="w-3 h-3 rounded-full bg-yellow-500" />
          <div className="w-3 h-3 rounded-full bg-green-500" />
        </div>
      </div>
      <ScrollArea className="h-[400px]">
        <div className="p-4 font-mono text-xs space-y-1">
          {events.length === 0 ? (
            <p className="text-slate-500">Waiting for processing to start...</p>
          ) : (
            events.map((event, index) => (
              <LogEntry key={index} event={event} />
            ))
          )}
          <div ref={bottomRef} />
        </div>
      </ScrollArea>
    </div>
  );
}

interface LogEntryProps {
  event: ProcessingEvent;
}

function LogEntry({ event }: LogEntryProps) {
  const getLevelColor = () => {
    switch (event.level) {
      case 'success':
        return 'text-green-400';
      case 'error':
        return 'text-red-400';
      case 'warning':
        return 'text-yellow-400';
      default:
        return 'text-blue-400';
    }
  };

  const getLevelPrefix = () => {
    switch (event.level) {
      case 'success':
        return '[SUCCESS]';
      case 'error':
        return '[ERROR]';
      case 'warning':
        return '[WARN]';
      default:
        return '[INFO]';
    }
  };

  return (
    <div className="flex gap-2 text-slate-300">
      <span className="text-slate-500">{formatTime(event.timestamp)}</span>
      <span className={cn("font-semibold", getLevelColor())}>
        {getLevelPrefix()}
      </span>
      <span className="text-slate-400">{event.agent}:</span>
      <span>{event.message}</span>
    </div>
  );
}
