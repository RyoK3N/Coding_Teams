import { AgentCard } from './agent-card';
import { Network } from 'lucide-react';
import type { AgentStatus, LogEntry, ArtifactFile } from '@/types/agent';

interface AgentGridProps {
  agents: AgentStatus[];
  logs: LogEntry[];
  artifacts: ArtifactFile[];
  onArtifactClick: (artifact: ArtifactFile) => void;
}

export function AgentGrid({ agents, logs, artifacts, onArtifactClick }: AgentGridProps) {
  if (!agents || agents.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-400 dark:text-gray-500">
          <Network className="h-12 w-12 mx-auto mb-4" />
          <p>No agents found for this session</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        <Network className="inline mr-2 h-5 w-5 text-primary" />
        Agent Network
      </h2>
      
      {agents.map((agent) => (
        <AgentCard
          key={agent.id}
          agent={agent}
          logs={logs}
          artifacts={artifacts.filter(artifact => artifact.agentId === agent.id)}
          onArtifactClick={onArtifactClick}
        />
      ))}
    </div>
  );
}
