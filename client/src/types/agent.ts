export interface AgentStatus {
  id: string;
  sessionId: string;
  name: string;
  role: string;
  status: 'idle' | 'running' | 'succeeded' | 'failed';
  progress: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface LogEntry {
  id: string;
  timestamp: Date;
  level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR';
  message: string;
  sequence: number;
  agentId?: string;
}

export interface AgentEvent {
  id: string;
  sessionId: string;
  agentId?: string;
  type: 'TASK_CREATED' | 'TASK_STARTED' | 'PROGRESS' | 'LOG' | 'ARTIFACT' | 'STEP_SUCCESS' | 'STEP_ERROR' | 'SESSION_COMPLETE';
  timestamp: Date;
  payload: any;
  sequence: number;
}

export interface ArtifactFile {
  id: string;
  sessionId: string;
  agentId?: string;
  filePath: string;
  content: string;
  size: number;
  language?: string;
  checksum?: string;
  createdAt: Date;
}

export interface SessionMetrics {
  totalTasks: number;
  activeTasks: number;
  completedTasks: number;
  failedTasks: number;
  avgCompletionTime?: number;
  successRate?: number;
}

export interface SessionData {
  id: string;
  prompt: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  createdAt: Date;
  updatedAt: Date;
  includeTests: boolean;
  includeDocumentation: boolean;
  metrics: SessionMetrics;
}
