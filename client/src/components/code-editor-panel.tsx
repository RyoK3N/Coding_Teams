import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Code, 
  Copy, 
  Download, 
  Eye,
  EyeOff,
  MaximizeIcon
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import type { Artifact } from '@shared/schema';

interface CodeEditorPanelProps {
  artifacts: Artifact[];
  selectedArtifact?: Artifact;
}

export function CodeEditorPanel({ artifacts, selectedArtifact }: CodeEditorPanelProps) {
  const [isMinimized, setIsMinimized] = useState(false);
  const { toast } = useToast();

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

  const downloadFile = (artifact: Artifact) => {
    const blob = new Blob([artifact.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = artifact.filePath?.split('/').pop() || 'file.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast({
      title: "Downloaded",
      description: `${a.download} downloaded successfully`,
    });
  };

  const getLanguageFromPath = (filePath: string) => {
    const ext = filePath.split('.').pop()?.toLowerCase();
    const languageMap: { [key: string]: string } = {
      'js': 'javascript',
      'ts': 'typescript',
      'jsx': 'javascript',
      'tsx': 'typescript',
      'py': 'python',
      'html': 'html',
      'css': 'css',
      'json': 'json',
      'md': 'markdown',
      'yml': 'yaml',
      'yaml': 'yaml',
      'sql': 'sql',
      'sh': 'bash',
    };
    return languageMap[ext || ''] || 'text';
  };

  const renderCodeWithSyntaxHighlight = (content: string, language: string) => {
    // Basic syntax highlighting for demonstration
    // In a real implementation, you'd use a proper syntax highlighter like Prism or Monaco
    return (
      <pre className="text-sm font-mono whitespace-pre-wrap break-words">
        <code>{content}</code>
      </pre>
    );
  };

  if (isMinimized) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
      >
        <Card className="cursor-pointer" onClick={() => setIsMinimized(false)}>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Code className="w-4 h-4 text-primary" />
                <span className="text-sm font-medium">Code Editor</span>
                {selectedArtifact && (
                  <Badge variant="secondary" className="text-xs">
                    {selectedArtifact.filePath?.split('/').pop()}
                  </Badge>
                )}
              </div>
              <MaximizeIcon className="w-4 h-4 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center space-x-2 text-base">
              <Code className="w-5 h-5 text-primary" />
              <span>Code Editor</span>
              {selectedArtifact && (
                <Badge variant="secondary" className="text-xs">
                  {getLanguageFromPath(selectedArtifact.filePath || '')}
                </Badge>
              )}
            </CardTitle>
            
            <div className="flex items-center space-x-1">
              {selectedArtifact && (
                <>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard(selectedArtifact.content)}
                  >
                    <Copy className="w-3 h-3" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => downloadFile(selectedArtifact)}
                  >
                    <Download className="w-3 h-3" />
                  </Button>
                </>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsMinimized(true)}
              >
                <EyeOff className="w-3 h-3" />
              </Button>
            </div>
          </div>
          
          {selectedArtifact && (
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>{selectedArtifact.filePath}</span>
              <span>
                {selectedArtifact.content.split('\n').length} lines • {
                  selectedArtifact.size ? `${Math.round(selectedArtifact.size / 1024)}KB` : 
                  `${new Blob([selectedArtifact.content]).size} bytes`
                }
              </span>
            </div>
          )}
        </CardHeader>
        
        <CardContent className="p-0">
          <ScrollArea className="h-96 w-full">
            <div className="p-4">
              {selectedArtifact ? (
                <motion.div
                  key={selectedArtifact.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.2 }}
                  className="bg-muted/30 rounded-lg p-4"
                >
                  {renderCodeWithSyntaxHighlight(
                    selectedArtifact.content, 
                    getLanguageFromPath(selectedArtifact.filePath || '')
                  )}
                </motion.div>
              ) : artifacts.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <Code className="w-12 h-12 mx-auto mb-4 opacity-30" />
                  <p className="text-lg font-medium mb-2">No Files Yet</p>
                  <p className="text-sm">Generated code will appear here</p>
                </div>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  <Eye className="w-12 h-12 mx-auto mb-4 opacity-30" />
                  <p className="text-lg font-medium mb-2">Select a File</p>
                  <p className="text-sm">Choose a file from the explorer to view its contents</p>
                </div>
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </motion.div>
  );
}