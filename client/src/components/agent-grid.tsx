import { motion } from 'framer-motion';
import { EnhancedAgentCard } from './enhanced-agent-card';
import type { Agent } from '@shared/schema';
import type { LogEntry, ArtifactFile } from '@/types/agent';

interface AgentGridProps {
  agents: Agent[];
  logs: LogEntry[];
  artifacts: ArtifactFile[];
  onArtifactClick?: (artifact: ArtifactFile) => void;
}

export function AgentGrid({ agents, logs, artifacts, onArtifactClick }: AgentGridProps) {
  return (
    <motion.div
      className="grid grid-cols-1 md:grid-cols-2 gap-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      {agents.map((agent, index) => {
        const agentLogs = logs
          .filter(log => log.agentId === agent.id)
          .map(log => log.message);
        
        const agentArtifacts = artifacts.filter(artifact => 
          artifact.filePath?.toLowerCase().includes(agent.name.toLowerCase().split(' ')[0]) ||
          artifact.filePath?.includes(agent.type)
        );
        
        return (
          <motion.div
            key={agent.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <EnhancedAgentCard
              agent={agent}
              logs={agentLogs}
              artifacts={agentArtifacts}
              isActive={agent.status === 'running'}
              className="h-full"
            />
          </motion.div>
        );
      })}
    </motion.div>
  );
}