import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { 
  ChevronDown, 
  ChevronUp, 
  Bot, 
  FileText, 
  Clock, 
  CheckCircle, 
  XCircle, 
  Loader2,
  Play,
  Pause
} from 'lucide-react';
import type { AgentStatus, ArtifactFile, LogEntry } from '@/types/agent';

interface EnhancedAgentCardProps {
  agent: AgentStatus;
  artifacts?: ArtifactFile[];
  logs?: LogEntry[];
  onArtifactSelect?: (artifact: ArtifactFile) => void;
}

export function EnhancedAgentCard({ 
  agent, 
  artifacts = [], 
  logs = [], 
  onArtifactSelect 
}: EnhancedAgentCardProps) {
  const [isLogsExpanded, setIsLogsExpanded] = useState(false);
  const [isArtifactsExpanded, setIsArtifactsExpanded] = useState(false);

  const getStatusIcon = () => {
    switch (agent.status) {
      case 'running':
        return <Loader2 className="h-4 w-4 animate-spin text-blue-600" />;
      case 'succeeded':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-600" />;
      case 'idle':
        return <Pause className="h-4 w-4 text-gray-600" />;
      default:
        return <Clock className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusBadge = () => {
    switch (agent.status) {
      case 'running':
        return <Badge className="bg-blue-100 text-blue-800">Running</Badge>;
      case 'succeeded':
        return <Badge className="bg-green-100 text-green-800">Completed</Badge>;
      case 'failed':
        return <Badge className="bg-red-100 text-red-800">Failed</Badge>;
      case 'idle':
        return <Badge className="bg-gray-100 text-gray-800">Idle</Badge>;
      default:
        return <Badge className="bg-gray-100 text-gray-800">Pending</Badge>;
    }
  };

  const agentLogs = logs.filter(log => log.agentId === agent.id).slice(-10);
  const agentArtifacts = artifacts.filter(artifact => artifact.agentId === agent.id);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="h-full">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <Bot className="h-8 w-8 text-primary" />
                <div className="absolute -top-1 -right-1">
                  {getStatusIcon()}
                </div>
              </div>
              <div>
                <CardTitle className="text-lg">{agent.name}</CardTitle>
                <p className="text-sm text-muted-foreground">{agent.role}</p>
              </div>
            </div>
            {getStatusBadge()}
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Progress */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>Progress</span>
              <span>{agent.progress}%</span>
            </div>
            <Progress value={agent.progress} className="h-2" />
          </div>

          {/* Current Step */}
          {agent.currentStep && (
            <div className="p-3 bg-muted rounded-lg">
              <p className="text-sm font-medium">Current Step:</p>
              <p className="text-sm text-muted-foreground">{agent.currentStep}</p>
            </div>
          )}

          {/* Stats */}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="text-center p-2 bg-muted rounded">
              <p className="font-medium">{agent.filesCreated || 0}</p>
              <p className="text-muted-foreground">Files</p>
            </div>
            <div className="text-center p-2 bg-muted rounded">
              <p className="font-medium">{agent.completionTime || 0}s</p>
              <p className="text-muted-foreground">Time</p>
            </div>
          </div>

          {/* Artifacts */}
          {agentArtifacts.length > 0 && (
            <Collapsible open={isArtifactsExpanded} onOpenChange={setIsArtifactsExpanded}>
              <CollapsibleTrigger asChild>
                <Button variant="ghost" className="w-full justify-between p-2">
                  <span className="flex items-center space-x-2">
                    <FileText className="h-4 w-4" />
                    <span>Artifacts ({agentArtifacts.length})</span>
                  </span>
                  {isArtifactsExpanded ? (
                    <ChevronUp className="h-4 w-4" />
                  ) : (
                    <ChevronDown className="h-4 w-4" />
                  )}
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent className="space-y-1">
                {agentArtifacts.map((artifact) => (
                  <Button
                    key={artifact.id}
                    variant="ghost"
                    size="sm"
                    className="w-full justify-start text-left"
                    onClick={() => onArtifactSelect?.(artifact)}
                  >
                    <FileText className="h-4 w-4 mr-2" />
                    <span className="truncate">{artifact.fileName}</span>
                  </Button>
                ))}
              </CollapsibleContent>
            </Collapsible>
          )}

          {/* Logs */}
          {agentLogs.length > 0 && (
            <Collapsible open={isLogsExpanded} onOpenChange={setIsLogsExpanded}>
              <CollapsibleTrigger asChild>
                <Button variant="ghost" className="w-full justify-between p-2">
                  <span>Recent Logs ({agentLogs.length})</span>
                  {isLogsExpanded ? (
                    <ChevronUp className="h-4 w-4" />
                  ) : (
                    <ChevronDown className="h-4 w-4" />
                  )}
                </Button>
              </CollapsibleTrigger>
              <CollapsibleContent className="space-y-1 max-h-32 overflow-y-auto">
                {agentLogs.map((log) => (
                  <div key={log.id} className="text-xs p-2 bg-muted rounded">
                    <div className="flex items-center justify-between mb-1">
                      <Badge variant="outline" className="text-xs">
                        {log.level}
                      </Badge>
                      <span className="text-muted-foreground">
                        {log.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-muted-foreground">{log.message}</p>
                  </div>
                ))}
              </CollapsibleContent>
            </Collapsible>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}