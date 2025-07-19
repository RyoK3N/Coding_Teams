import type { Agent, Session, AgentEvent, Artifact } from '@shared/schema';

export interface SessionData extends Session {
  // Extended session data
}

export interface AgentStatus extends Agent {
  // Extended agent status
}

export interface ArtifactFile extends Artifact {
  // Extended artifact data
}

export interface LogEntry {
  id: string;
  timestamp: Date;
  level: string;
  message: string;
  sequence: number;
  agentId?: string;
  agentName?: string;
}

export interface WebSocketMessage {
  type: string;
  sessionId?: string;
  data?: any;
}

export { AgentEvent };