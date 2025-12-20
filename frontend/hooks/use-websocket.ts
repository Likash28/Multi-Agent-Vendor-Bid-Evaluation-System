"use client"

import { useEffect, useRef, useState, useCallback } from 'react';
import { WS_BASE_URL } from '@/lib/constants';
import { WebSocketMessage, AgentProgress, ProcessingEvent } from '@/types/evaluation';

interface UseWebSocketOptions {
  evaluationId: string;
  onAgentUpdate?: (agent: AgentProgress) => void;
  onProgress?: (progress: number) => void;
  onLog?: (event: ProcessingEvent) => void;
  onCompletion?: () => void;
  onError?: (error: string) => void;
}

export function useWebSocket({
  evaluationId,
  onAgentUpdate,
  onProgress,
  onLog,
  onCompletion,
  onError,
}: UseWebSocketOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(`${WS_BASE_URL}/ws/evaluation/${evaluationId}`);

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setReconnectAttempts(0);
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);

          switch (message.type) {
            case 'agent_update':
              onAgentUpdate?.(message.data as AgentProgress);
              break;
            case 'progress':
              onProgress?.(message.data as number);
              break;
            case 'log':
              onLog?.(message.data as ProcessingEvent);
              break;
            case 'completion':
              onCompletion?.();
              break;
            case 'error':
              onError?.(message.data as string);
              break;
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        onError?.('WebSocket connection error');
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);

        // Attempt to reconnect with exponential backoff
        if (reconnectAttempts < 5) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
          reconnectTimeoutRef.current = setTimeout(() => {
            setReconnectAttempts(prev => prev + 1);
            connect();
          }, delay);
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      onError?.('Failed to create WebSocket connection');
    }
  }, [evaluationId, onAgentUpdate, onProgress, onLog, onCompletion, onError, reconnectAttempts]);

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  return {
    isConnected,
    disconnect,
  };
}
