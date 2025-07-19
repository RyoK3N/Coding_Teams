import { motion } from 'framer-motion';
import { EnhancedAgentCard } from './enhanced-agent-card';
import type { AgentStatus, ArtifactFile, LogEntry } from '@/types/agent';

interface AgentGridProps {
  agents: AgentStatus[];
  artifacts?: ArtifactFile[];
  logs?: LogEntry[];
  onArtifactSelect?: (artifact: ArtifactFile) => void;
}

export function AgentGrid({ 
  agents, 
  artifacts = [], 
  logs = [], 
  onArtifactSelect 
}: AgentGridProps) {
  if (!agents || agents.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">No agents found for this session.</p>
      </div>
    );
  }

  return (
    <motion.div
      className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      {agents.map((agent, index) => (
        <motion.div
          key={agent.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: index * 0.1 }}
        >
          <EnhancedAgentCard
            agent={agent}
            artifacts={artifacts}
            logs={logs}
            onArtifactSelect={onArtifactSelect}
          />
        </motion.div>
      ))}
    </motion.div>
  );
}