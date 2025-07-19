import { useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { ChevronDown, User, Clock, FileCode, FileText } from 'lucide-react';
import { VirtualizedLogList } from './virtualized-log-list';
import type { AgentStatus, LogEntry, ArtifactFile } from '@/types/agent';

interface AgentCardProps {
  agent: AgentStatus;
  logs: LogEntry[];
  artifacts: ArtifactFile[];
  onArtifactClick: (artifact: ArtifactFile) => void;
}

export function AgentCard({ agent, logs, artifacts, onArtifactClick }: AgentCardProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  const getStatusIcon = () => {
    switch (agent.status) {
      case 'running':
        return <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />;
      case 'succeeded':
        return <div className="w-1.5 h-1.5 bg-blue-500 rounded-full" />;
      case 'failed':
        return <div className="w-1.5 h-1.5 bg-red-500 rounded-full" />;
      default:
        return <div className="w-1.5 h-1.5 bg-gray-400 rounded-full" />;
    }
  };

  const getStatusBadge = () => {
    switch (agent.status) {
      case 'running':
        return (
          <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
            {getStatusIcon()}
            <span className="ml-1">Running</span>
          </Badge>
        );
      case 'succeeded':
        return (
          <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
            {getStatusIcon()}
            <span className="ml-1">Succeeded</span>
          </Badge>
        );
      case 'failed':
        return (
          <Badge className="bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
            {getStatusIcon()}
            <span className="ml-1">Failed</span>
          </Badge>
        );
      default:
        return (
          <Badge className="bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">
            {getStatusIcon()}
            <span className="ml-1">Idle</span>
          </Badge>
        );
    }
  };

  const getRoleIcon = () => {
    if (agent.name.includes('Principal')) {
      return <User className="h-5 w-5 text-primary" />;
    }
    if (agent.name.includes('Python')) {
      return <FileCode className="h-5 w-5 text-green-600" />;
    }
    if (agent.name.includes('Test')) {
      return <FileText className="h-5 w-5 text-purple-600" />;
    }
    return <User className="h-5 w-5 text-gray-500" />;
  };

  const getFileIcon = (filePath: string) => {
    const extension = filePath.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'py':
        return <FileCode className="h-4 w-4 text-blue-500" />;
      case 'md':
        return <FileText className="h-4 w-4 text-blue-500" />;
      case 'txt':
        return <FileText className="h-4 w-4 text-gray-500" />;
      default:
        return <FileCode className="h-4 w-4 text-gray-500" />;
    }
  };

  const formatFileSize = (size: number) => {
    if (size < 1024) return `${size} B`;
    if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
    return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <Card className="bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
      <Collapsible open={isExpanded} onOpenChange={setIsExpanded}>
        <CardHeader className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                {getRoleIcon()}
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white">
                  {agent.name}
                </h3>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {agent.role}
                </span>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {getStatusBadge()}
              <CollapsibleTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-8 w-8 p-0 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
                >
                  <ChevronDown
                    className={`h-4 w-4 transition-transform ${
                      isExpanded ? 'rotate-180' : ''
                    }`}
                  />
                </Button>
              </CollapsibleTrigger>
            </div>
          </div>
        </CardHeader>

        <CollapsibleContent>
          <CardContent className="p-4">
            {/* Progress Bar */}
            <div className="mb-4">
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-600 dark:text-gray-400">Task Progress</span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {agent.progress}%
                </span>
              </div>
              <Progress 
                value={agent.progress} 
                className="h-1.5"
                // Apply different colors based on status
                style={{
                  backgroundColor: agent.status === 'failed' ? 'rgb(239, 68, 68)' : undefined
                }}
              />
            </div>

            {/* Log Pane */}
            <VirtualizedLogList 
              logs={logs.filter(log => log.agentId === agent.id)}
              className="mb-4"
            />

            {/* Artifacts List */}
            <div>
              <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                Generated Artifacts
              </h4>
              {artifacts.length === 0 ? (
                <div className="text-center text-gray-400 dark:text-gray-500 py-4">
                  <Clock className="h-8 w-8 mx-auto mb-2" />
                  <div className="text-sm">
                    {agent.status === 'idle' ? 'Waiting for implementation to complete...' : 'No artifacts yet'}
                  </div>
                </div>
              ) : (
                <div className="space-y-1">
                  {artifacts.map((artifact) => (
                    <div
                      key={artifact.id}
                      className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-900 rounded text-sm cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                      onClick={() => onArtifactClick(artifact)}
                    >
                      <div className="flex items-center space-x-2">
                        {getFileIcon(artifact.filePath)}
                        <span className="text-gray-700 dark:text-gray-300">
                          {artifact.filePath}
                        </span>
                        <Badge className="text-xs bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200">
                          new
                        </Badge>
                      </div>
                      <span className="text-xs text-gray-500">
                        {formatFileSize(artifact.size)}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  );
}
