import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Code, 
  Copy, 
  Download, 
  Maximize2, 
  X, 
  FileCode, 
  FileText,
  Columns
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import type { ArtifactFile } from '@/types/agent';

interface CodeEditorPanelProps {
  artifacts: ArtifactFile[];
  selectedArtifact?: ArtifactFile;
  onClose?: () => void;
}

export function CodeEditorPanel({ artifacts, selectedArtifact, onClose }: CodeEditorPanelProps) {
  const [openTabs, setOpenTabs] = useState<ArtifactFile[]>([]);
  const [activeTab, setActiveTab] = useState<string>('');
  const [isDiffMode, setIsDiffMode] = useState(false);
  const editorRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  // Initialize Monaco Editor
  useEffect(() => {
    // In a real implementation, you would initialize Monaco Editor here
    // For now, we'll use a simple textarea with syntax highlighting
  }, []);

  // Handle selected artifact changes
  useEffect(() => {
    if (selectedArtifact && !openTabs.find(tab => tab.id === selectedArtifact.id)) {
      const newTabs = [...openTabs, selectedArtifact];
      setOpenTabs(newTabs);
      setActiveTab(selectedArtifact.id);
    } else if (selectedArtifact) {
      setActiveTab(selectedArtifact.id);
    }
  }, [selectedArtifact, openTabs]);

  const closeTab = (artifactId: string) => {
    const newTabs = openTabs.filter(tab => tab.id !== artifactId);
    setOpenTabs(newTabs);
    
    if (activeTab === artifactId && newTabs.length > 0) {
      setActiveTab(newTabs[0].id);
    } else if (newTabs.length === 0) {
      setActiveTab('');
    }
  };

  const copyToClipboard = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content);
      toast({
        title: "Copied",
        description: "Code copied to clipboard",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to copy code",
        variant: "destructive",
      });
    }
  };

  const downloadFile = (artifact: ArtifactFile) => {
    const blob = new Blob([artifact.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = artifact.filePath.split('/').pop() || 'file.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast({
      title: "Downloaded",
      description: `File ${a.download} downloaded successfully`,
    });
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

  const getLanguage = (filePath: string): string => {
    const extension = filePath.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'py':
        return 'python';
      case 'js':
        return 'javascript';
      case 'ts':
        return 'typescript';
      case 'md':
        return 'markdown';
      case 'json':
        return 'json';
      case 'html':
        return 'html';
      case 'css':
        return 'css';
      default:
        return 'text';
    }
  };

  const activeArtifact = openTabs.find(tab => tab.id === activeTab);

  return (
    <Card className="bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
      <CardHeader className="p-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center text-gray-900 dark:text-white">
            <Code className="mr-2 h-5 w-5 text-primary" />
            Code Editor
          </CardTitle>
          <div className="flex items-center space-x-2">
            <Button
              size="sm"
              variant="ghost"
              onClick={() => activeArtifact && copyToClipboard(activeArtifact.content)}
              disabled={!activeArtifact}
              className="h-8 w-8 p-0"
              title="Copy Code"
            >
              <Copy className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => activeArtifact && downloadFile(activeArtifact)}
              disabled={!activeArtifact}
              className="h-8 w-8 p-0"
              title="Download File"
            >
              <Download className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setIsDiffMode(!isDiffMode)}
              disabled={!activeArtifact}
              className="h-8 w-8 p-0"
              title="Toggle Diff View"
            >
              <Columns className="h-4 w-4" />
            </Button>
            <Button
              size="sm"
              variant="ghost"
              className="h-8 w-8 p-0"
              title="Maximize"
            >
              <Maximize2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="p-0">
        {openTabs.length === 0 ? (
          <div className="p-8 text-center text-gray-400 dark:text-gray-500">
            <Code className="h-12 w-12 mx-auto mb-4" />
            <p>Select a file from the file explorer to start editing</p>
          </div>
        ) : (
          <div>
            {/* File Tabs */}
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <div className="flex items-center border-b border-gray-200 dark:border-gray-700 overflow-x-auto">
                <TabsList className="h-auto p-0 bg-transparent rounded-none">
                  {openTabs.map((artifact) => (
                    <div key={artifact.id} className="flex items-center">
                      <TabsTrigger
                        value={artifact.id}
                        className="flex items-center px-4 py-2 hover:bg-gray-50 dark:hover:bg-gray-700 data-[state=active]:bg-gray-50 dark:data-[state=active]:bg-gray-700 data-[state=active]:border-b-2 data-[state=active]:border-primary rounded-none"
                      >
                        {getFileIcon(artifact.filePath)}
                        <span className="ml-2 text-sm">
                          {artifact.filePath.split('/').pop()}
                        </span>
                      </TabsTrigger>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={(e) => {
                          e.stopPropagation();
                          closeTab(artifact.id);
                        }}
                        className="h-6 w-6 p-0 ml-1 mr-2 hover:bg-gray-200 dark:hover:bg-gray-600"
                      >
                        <X className="h-3 w-3" />
                      </Button>
                    </div>
                  ))}
                </TabsList>
              </div>

              {/* Editor Content */}
              {openTabs.map((artifact) => (
                <TabsContent key={artifact.id} value={artifact.id} className="m-0">
                  <div className="h-96 bg-gray-900 text-gray-100 overflow-auto">
                    <div className="p-4 font-mono text-sm leading-relaxed">
                      {/* Simple syntax highlighting for demo - in production use Monaco */}
                      <pre className="whitespace-pre-wrap break-words">
                        {artifact.content.split('\n').map((line, index) => (
                          <div key={index} className="flex">
                            <span className="text-gray-500 w-12 text-right pr-4 select-none user-select-none flex-shrink-0">
                              {index + 1}
                            </span>
                            <span className="flex-1">
                              {line || ' '}
                            </span>
                          </div>
                        ))}
                      </pre>
                    </div>
                  </div>
                </TabsContent>
              ))}
            </Tabs>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
