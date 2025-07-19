import { useEffect, useCallback } from 'react';
import { websocketService } from '@/lib/websocket-service';

type EventCallback = (data: any) => void;

export function useWebSocket() {
  useEffect(() => {
    websocketService.connect().catch(console.error);
    
    return () => {
      websocketService.disconnect();
    };
  }, []);

  const subscribe = useCallback((eventType: string, callback: EventCallback) => {
    websocketService.on(eventType, callback);
    
    return () => {
      websocketService.off(eventType, callback);
    };
  }, []);

  const subscribeToSession = useCallback((sessionId: string) => {
    websocketService.subscribeToSession(sessionId);
  }, []);

  return {
    subscribe,
    subscribeToSession,
  };
}
