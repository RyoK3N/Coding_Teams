import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { 
  Copy, 
  Download, 
  FileText, 
  Code, 
  Maximize2,
  X
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import type { ArtifactFile } from '@/types/agent';

interface CodeEditorPanelProps {
  artifact?: ArtifactFile;
  onClose?: () => void;
}

export function CodeEditorPanel({ artifact, onClose }: CodeEditorPanelProps) {
  const { toast } = useToast();

  if (!artifact) {
    return (
      <motion.div
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
      >
        <Card className="h-full">
          <CardContent className="p-8 flex items-center justify-center">
            <div className="text-center">
              <Code className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">Select a file to view its contents</p>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    );
  }

  const handleCopyContent = async () => {
    try {
      await navigator.clipboard.writeText(artifact.content);
      toast({
        title: "Copied",
        description: "File content copied to clipboard",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to copy content",
        variant: "destructive",
      });
    }
  };

  const handleDownload = () => {
    const blob = new Blob([artifact.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = artifact.fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast({
      title: "Downloaded",
      description: `${artifact.fileName} downloaded successfully`,
    });
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getLanguageBadge = (language: string) => {
    const colorMap: Record<string, string> = {
      javascript: 'bg-yellow-100 text-yellow-800',
      typescript: 'bg-blue-100 text-blue-800',
      python: 'bg-green-100 text-green-800',
      java: 'bg-red-100 text-red-800',
      cpp: 'bg-purple-100 text-purple-800',
      html: 'bg-orange-100 text-orange-800',
      css: 'bg-pink-100 text-pink-800',
      markdown: 'bg-gray-100 text-gray-800',
    };
    
    return (
      <Badge className={colorMap[language.toLowerCase()] || 'bg-gray-100 text-gray-800'}>
        {language.toUpperCase()}
      </Badge>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="h-full">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <FileText className="h-5 w-5 text-primary" />
              <div>
                <CardTitle className="text-lg">{artifact.fileName}</CardTitle>
                <p className="text-sm text-muted-foreground">
                  {formatFileSize(artifact.size)} • {artifact.filePath}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {getLanguageBadge(artifact.language)}
              <Button variant="outline" size="sm" onClick={handleCopyContent}>
                <Copy className="h-4 w-4 mr-1" />
                Copy
              </Button>
              <Button variant="outline" size="sm" onClick={handleDownload}>
                <Download className="h-4 w-4 mr-1" />
                Download
              </Button>
              {onClose && (
                <Button variant="ghost" size="sm" onClick={onClose}>
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="p-0">
          <ScrollArea className="h-96 p-4">
            <pre className="text-sm font-mono bg-muted p-4 rounded-lg overflow-x-auto whitespace-pre-wrap">
              <code>{artifact.content}</code>
            </pre>
          </ScrollArea>
        </CardContent>
      </Card>
    </motion.div>
  );
}