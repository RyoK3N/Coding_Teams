import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiRequest } from '@/lib/queryClient';
// import { useWebSocket } from './use-websocket';
import type { SessionData, AgentStatus, AgentEvent, ArtifactFile } from '@/types/agent';

export function useSession(sessionId: string | null) {
  const queryClient = useQueryClient();
  // const { subscribe, subscribeToSession } = useWebSocket();
  const [events, setEvents] = useState<AgentEvent[]>([]);

  // Fetch session data
  const sessionQuery = useQuery({
    queryKey: ['/api/sessions', sessionId],
    enabled: !!sessionId,
  });

  // Fetch agents
  const agentsQuery = useQuery({
    queryKey: ['/api/sessions', sessionId, 'agents'],
    enabled: !!sessionId,
  });

  // Fetch artifacts
  const artifactsQuery = useQuery({
    queryKey: ['/api/sessions', sessionId, 'artifacts'],
    enabled: !!sessionId,
  });

  // Subscribe to real-time events - temporarily disabled for debugging
  useEffect(() => {
    if (!sessionId) return;

    // subscribeToSession(sessionId);

    // const unsubscribe = subscribe('agent_event', (message: any) => {
    //   if (message.event) {
    //     setEvents(prev => [...prev, message.event]);
        
    //     // Invalidate relevant queries to refresh data
    //     queryClient.invalidateQueries({ queryKey: ['/api/sessions', sessionId, 'agents'] });
    //     queryClient.invalidateQueries({ queryKey: ['/api/sessions', sessionId, 'artifacts'] });
    //     queryClient.invalidateQueries({ queryKey: ['/api/sessions', sessionId] });
    //   }
    // });

    // return unsubscribe;
  }, [sessionId, queryClient]);

  // Create session mutation
  const createSessionMutation = useMutation({
    mutationFn: async (data: { prompt: string; includeTests: boolean; includeDocumentation: boolean }) => {
      const response = await apiRequest('POST', '/api/sessions', data);
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/sessions'] });
    },
  });

  return {
    session: sessionQuery.data as SessionData | undefined,
    agents: agentsQuery.data as AgentStatus[] | undefined,
    artifacts: artifactsQuery.data as ArtifactFile[] | undefined,
    events,
    isLoading: sessionQuery.isLoading || agentsQuery.isLoading,
    error: sessionQuery.error || agentsQuery.error,
    createSession: createSessionMutation.mutateAsync,
    isCreatingSession: createSessionMutation.isPending,
  };
}

export function useSessions() {
  return useQuery({
    queryKey: ['/api/sessions'],
  });
}
