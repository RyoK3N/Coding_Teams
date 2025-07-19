// Simplified types for frontend use
export interface SessionData {
  id: string;
  userId: string;
  prompt: string;
  status: string;
  createdAt: string;
  updatedAt: string;
  includeTests: boolean;
  includeDocumentation: boolean;
  outputDir: string;
  duration?: number;
  filesCreated?: number;
  workPackagesTotal?: number;
  workPackagesCompleted?: number;
  metrics?: any;
}

export interface AgentStatus {
  id: string;
  sessionId: string;
  name: string;
  role: string;
  type: string;
  status: string;
  progress: number;
  currentStep?: string;
  workPackageId?: string;
  filesCreated?: number;
  completionTime?: number;
  createdAt: string;
  updatedAt: string;
}

export interface ArtifactFile {
  id: string;
  sessionId: string;
  agentId: string;
  filePath: string;
  fileName: string;
  language: string;
  content: string;
  size: number;
  createdAt: string;
}

export interface AgentEvent {
  id: string;
  sessionId: string;
  agentId: string;
  type: string;
  sequence: number;
  timestamp: string;
  payload: any;
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