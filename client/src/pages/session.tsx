import { useState, useEffect } from 'react';
import { useRoute } from 'wouter';
import { useSession } from '@/hooks/use-session';
import { GlobalStatusBar } from '@/components/global-status-bar';
import { AgentGrid } from '@/components/agent-grid';
import { FileExplorer } from '@/components/file-explorer';
import { CodeEditorPanel } from '@/components/code-editor-panel';
import { MetricsPanel } from '@/components/metrics-panel';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Download } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { apiRequest } from '@/lib/queryClient';
import type { ArtifactFile, LogEntry } from '@/types/agent';

export default function SessionPage() {
  const [, params] = useRoute('/session/:id');
  const sessionId = params?.id;
  const [selectedArtifact, setSelectedArtifact] = useState<ArtifactFile>();
  const { toast } = useToast();

  const { 
    session, 
    agents, 
    artifacts, 
    events,
    isLoading,
    error 
  } = useSession(sessionId || null);

  // Convert events to log entries
  const logs: LogEntry[] = events
    .filter(event => event.type === 'LOG')
    .map(event => ({
      id: event.id,
      timestamp: new Date(event.timestamp),
      level: event.payload.level,
      message: event.payload.message,
      sequence: event.sequence,
      agentId: event.agentId,
    }));

  const handleDownloadAll = async () => {
    if (!sessionId) return;
    
    try {
      const response = await apiRequest('GET', `/api/sessions/${sessionId}/download`);
      const blob = await response.blob();
      
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `session-${sessionId}-artifacts.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      
      toast({
        title: "Downloaded",
        description: "All artifacts downloaded successfully",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to download artifacts",
        variant: "destructive",
      });
    }
  };

  const handlePause = () => {
    // TODO: Implement pause functionality
    toast({
      title: "Pause",
      description: "Pause functionality not yet implemented",
    });
  };

  const handleRegenerate = () => {
    // TODO: Implement regenerate functionality
    toast({
      title: "Regenerate",
      description: "Regenerate functionality not yet implemented",
    });
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded-xl"></div>
        </div>
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          <div className="xl:col-span-2 space-y-4">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="h-96 bg-gray-200 dark:bg-gray-700 rounded-xl"></div>
              </div>
            ))}
          </div>
          <div className="space-y-6">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="animate-pulse">
                <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded-xl"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-500 dark:text-red-400 mb-4">
          <p>Error loading session: {error.message}</p>
        </div>
        <Button onClick={() => window.location.reload()}>
          Retry
        </Button>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500 dark:text-gray-400">Session not found</p>
        <Button onClick={() => window.history.back()} className="mt-4">
          <ArrowLeft className="mr-2 h-4 w-4" />
          Go Back
        </Button>
      </div>
    );
  }

  // Calculate metrics for the metrics panel
  const eventCount = events.length;
  const codeLines = artifacts?.reduce((total, artifact) => {
    return total + (artifact.content.split('\n').length || 0);
  }, 0) || 0;
  const filesGenerated = artifacts?.length || 0;

  return (
    <div className="space-y-6">
      {/* Navigation */}
      <div className="flex items-center space-x-4">
        <Button 
          variant="ghost" 
          onClick={() => window.history.back()}
          className="text-gray-600 dark:text-gray-400"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </Button>
      </div>

      {/* Global Status */}
      <GlobalStatusBar
        session={session}
        onDownload={handleDownloadAll}
        onPause={handlePause}
        onRegenerate={handleRegenerate}
      />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Left Column: Agent Grid */}
        <div className="xl:col-span-2">
          <AgentGrid
            agents={agents || []}
            logs={logs}
            artifacts={artifacts || []}
            onArtifactClick={setSelectedArtifact}
          />
        </div>

        {/* Right Column: File Explorer, Code Editor, Metrics */}
        <div className="space-y-6">
          <FileExplorer
            artifacts={artifacts || []}
            onFileClick={setSelectedArtifact}
            selectedFile={selectedArtifact?.filePath}
          />

          <CodeEditorPanel
            artifacts={artifacts || []}
            selectedArtifact={selectedArtifact}
          />

          <MetricsPanel
            metrics={session.metrics}
            eventCount={eventCount}
            codeLines={codeLines}
            filesGenerated={filesGenerated}
          />
        </div>
      </div>
    </div>
  );
}
