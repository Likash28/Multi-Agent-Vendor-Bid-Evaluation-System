"use client"

import { useEffect, useRef, useState, useCallback } from 'react';
import { WS_BASE_URL } from '@/lib/constants';
import { getToken } from '@/lib/auth';
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
  const shouldReconnectRef = useRef(true);

  const connect = useCallback(() => {
    if (!shouldReconnectRef.current) {
      return;
    }

    try {
      // Get authentication token if available
      const token = getToken();
      const url = token 
        ? `${WS_BASE_URL}/ws/evaluation/${evaluationId}?token=${encodeURIComponent(token)}`
        : `${WS_BASE_URL}/ws/evaluation/${evaluationId}`;

      const ws = new WebSocket(url);

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setReconnectAttempts(0);
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);

          switch (message.type) {
            case 'connected':
            case 'subscribed':
              // Connection confirmed
              break;
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
            case 'pong':
              // Keep-alive response
              break;
            default:
              console.warn('Unknown WebSocket message type:', message.type);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        // Don't call onError here as onclose will handle it
      };

      ws.onclose = (event) => {
        console.log('WebSocket disconnected', { code: event.code, reason: event.reason });
        setIsConnected(false);

        // Don't reconnect if it was a clean close or policy violation
        if (event.code === 1000 || event.code === 1008) {
          shouldReconnectRef.current = false;
          if (event.code === 1008) {
            onError?.('Authentication failed. Please refresh the page.');
          }
          return;
        }

        // Attempt to reconnect with exponential backoff
        if (shouldReconnectRef.current && reconnectAttempts < 5) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
          console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttempts + 1}/5)`);
          reconnectTimeoutRef.current = setTimeout(() => {
            setReconnectAttempts(prev => prev + 1);
            connect();
          }, delay);
        } else if (reconnectAttempts >= 5) {
          onError?.('Failed to connect to server. Please refresh the page.');
        }
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      onError?.('Failed to create WebSocket connection');
      
      // Attempt to reconnect
      if (shouldReconnectRef.current && reconnectAttempts < 5) {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
        reconnectTimeoutRef.current = setTimeout(() => {
          setReconnectAttempts(prev => prev + 1);
          connect();
        }, delay);
      }
    }
  }, [evaluationId, onAgentUpdate, onProgress, onLog, onCompletion, onError, reconnectAttempts]);

  useEffect(() => {
    shouldReconnectRef.current = true;
    connect();

    return () => {
      shouldReconnectRef.current = false;
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmounting');
        wsRef.current = null;
      }
    };
  }, [connect]);

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect');
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  return {
    isConnected,
    disconnect,
  };
}
