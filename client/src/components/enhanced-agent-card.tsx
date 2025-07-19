import { motion, AnimatePresence } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Button } from '@/components/ui/button';
import { 
  Bot, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Play, 
  FileText, 
  Activity,
  ChevronDown,
  ChevronUp,
  Loader2,
  Zap,
  Brain,
  Code,
  Database,
  Shield,
  Server,
  TestTube,
  Palette
} from 'lucide-react';
import { useState, useEffect } from 'react';
import type { Agent } from '@shared/schema';

interface EnhancedAgentCardProps {
  agent: Agent;
  logs?: string[];
  artifacts?: any[];
  isActive?: boolean;
  className?: string;
}

// Agent type to icon mapping
const agentIcons = {
  principle: Brain,
  backend: Server,
  frontend: Palette,
  database: Database,
  api: Zap,
  test: TestTube,
  devops: Server,
  security: Shield,
  specialist: Code
};

// Status colors
const statusColors = {
  idle: 'bg-gray-100 text-gray-700 border-gray-300',
  running: 'bg-blue-100 text-blue-700 border-blue-300 animate-pulse',
  succeeded: 'bg-green-100 text-green-700 border-green-300',
  failed: 'bg-red-100 text-red-700 border-red-300'
};

const statusIcons = {
  idle: Clock,
  running: Loader2,
  succeeded: CheckCircle,
  failed: AlertCircle
};

export function EnhancedAgentCard({ 
  agent, 
  logs = [], 
  artifacts = [], 
  isActive = false,
  className 
}: EnhancedAgentCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [animatedProgress, setAnimatedProgress] = useState(0);

  const IconComponent = agentIcons[agent.type] || Code;
  const StatusIcon = statusIcons[agent.status];

  // Animate progress changes
  useEffect(() => {
    if (agent.progress !== undefined) {
      const timer = setTimeout(() => {
        setAnimatedProgress(agent.progress || 0);
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [agent.progress]);

  // Card hover and click animations
  const cardVariants = {
    idle: { 
      scale: 1, 
      boxShadow: "0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)",
      borderColor: "transparent"
    },
    hover: { 
      scale: 1.02,
      boxShadow: "0 4px 12px rgba(0,0,0,0.15), 0 2px 4px rgba(0,0,0,0.12)",
      borderColor: isActive ? "#3B82F6" : "rgba(59, 130, 246, 0.2)"
    },
    active: {
      scale: 1,
      boxShadow: "0 0 0 2px #3B82F6, 0 4px 12px rgba(59, 130, 246, 0.25)",
      borderColor: "#3B82F6"
    }
  };

  return (
    <motion.div
      className={`relative ${className}`}
      variants={cardVariants}
      initial="idle"
      whileHover="hover"
      animate={isActive ? "active" : "idle"}
      transition={{ duration: 0.2 }}
    >
      <Card className="h-full border-2 transition-colors duration-200">
        {/* Status indicator bar */}
        <motion.div
          className={`h-1 w-full ${
            agent.status === 'running' ? 'bg-blue-500' : 
            agent.status === 'succeeded' ? 'bg-green-500' : 
            agent.status === 'failed' ? 'bg-red-500' : 'bg-gray-300'
          }`}
          initial={{ width: 0 }}
          animate={{ width: '100%' }}
          transition={{ duration: 0.5 }}
        />

        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3">
              <motion.div
                className={`p-2 rounded-lg ${
                  agent.status === 'running' ? 'bg-blue-100' :
                  agent.status === 'succeeded' ? 'bg-green-100' :
                  agent.status === 'failed' ? 'bg-red-100' : 'bg-gray-100'
                }`}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <IconComponent className={`w-5 h-5 ${
                  agent.status === 'running' ? 'text-blue-600' :
                  agent.status === 'succeeded' ? 'text-green-600' :
                  agent.status === 'failed' ? 'text-red-600' : 'text-gray-600'
                }`} />
              </motion.div>
              
              <div>
                <CardTitle className="text-lg">{agent.name}</CardTitle>
                <p className="text-sm text-muted-foreground">{agent.role}</p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Badge 
                variant="outline" 
                className={statusColors[agent.status]}
              >
                <StatusIcon className={`w-3 h-3 mr-1 ${
                  agent.status === 'running' ? 'animate-spin' : ''
                }`} />
                {agent.status}
              </Badge>
              
              {/* Activity pulse */}
              {agent.status === 'running' && (
                <motion.div
                  className="w-3 h-3 bg-blue-400 rounded-full"
                  animate={{ 
                    scale: [1, 1.5, 1],
                    opacity: [0.5, 1, 0.5]
                  }}
                  transition={{ 
                    duration: 2, 
                    repeat: Infinity,
                    ease: "easeInOut"
                  }}
                />
              )}
            </div>
          </div>

          {/* Progress bar */}
          {agent.progress !== undefined && (
            <div className="mt-3">
              <div className="flex justify-between text-sm text-muted-foreground mb-1">
                <span>Progress</span>
                <span>{Math.round(animatedProgress)}%</span>
              </div>
              <Progress 
                value={animatedProgress} 
                className="h-2"
              />
            </div>
          )}

          {/* Current step */}
          {agent.currentStep && (
            <motion.div
              className="mt-2 text-sm text-muted-foreground flex items-center space-x-1"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <Activity className="w-3 h-3" />
              <span>{agent.currentStep}</span>
            </motion.div>
          )}
        </CardHeader>

        <CardContent className="pt-0">
          {/* Stats */}
          <div className="flex justify-between items-center text-sm text-muted-foreground mb-4">
            <div className="flex items-center space-x-1">
              <FileText className="w-3 h-3" />
              <span>{artifacts.length} files</span>
            </div>
            
            {agent.completionTime && (
              <div className="flex items-center space-x-1">
                <Clock className="w-3 h-3" />
                <span>{Math.round((agent.completionTime - new Date(agent.createdAt).getTime()) / 1000)}s</span>
              </div>
            )}
          </div>

          {/* Expandable logs section */}
          <Collapsible 
            open={isExpanded} 
            onOpenChange={setIsExpanded}
          >
            <CollapsibleTrigger asChild>
              <Button 
                variant="ghost" 
                size="sm" 
                className="w-full justify-between p-2 h-8"
              >
                <span className="flex items-center space-x-1">
                  <Activity className="w-3 h-3" />
                  <span>Activity ({logs.length})</span>
                </span>
                <motion.div
                  animate={{ rotate: isExpanded ? 180 : 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <ChevronDown className="w-4 h-4" />
                </motion.div>
              </Button>
            </CollapsibleTrigger>

            <CollapsibleContent>
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.2 }}
              >
                <ScrollArea className="h-32 w-full border rounded mt-2">
                  <div className="p-2 space-y-1">
                    <AnimatePresence>
                      {logs.length === 0 ? (
                        <motion.div
                          className="text-xs text-muted-foreground text-center py-4"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          exit={{ opacity: 0 }}
                        >
                          No activity yet...
                        </motion.div>
                      ) : (
                        logs.slice(-20).map((log, index) => (
                          <motion.div
                            key={index}
                            className="text-xs font-mono bg-muted/50 p-1 rounded break-all"
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.02 }}
                          >
                            {log}
                          </motion.div>
                        ))
                      )}
                    </AnimatePresence>
                  </div>
                </ScrollArea>
              </motion.div>
            </CollapsibleContent>
          </Collapsible>

          {/* Artifact preview */}
          {artifacts.length > 0 && (
            <motion.div
              className="mt-3 p-2 bg-muted/30 rounded-lg"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
            >
              <div className="text-xs font-medium text-muted-foreground mb-1">
                Latest Files:
              </div>
              <div className="flex flex-wrap gap-1">
                {artifacts.slice(-3).map((artifact, index) => (
                  <motion.div
                    key={artifact.id || index}
                    className="text-xs bg-white dark:bg-gray-800 px-2 py-1 rounded border"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    {artifact.filePath?.split('/').pop() || 'unnamed'}
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}