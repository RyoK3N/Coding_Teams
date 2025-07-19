import { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Folder, 
  File, 
  ChevronDown, 
  ChevronRight, 
  FileText, 
  FileCode, 
  FileImage,
  Download
} from 'lucide-react';
import type { ArtifactFile } from '@/types/agent';

interface FileExplorerProps {
  artifacts: ArtifactFile[];
  onFileSelect?: (artifact: ArtifactFile) => void;
  selectedFile?: ArtifactFile;
}

interface FileNode {
  name: string;
  type: 'file' | 'folder';
  children?: FileNode[];
  artifact?: ArtifactFile;
}

export function FileExplorer({ artifacts, onFileSelect, selectedFile }: FileExplorerProps) {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());

  const buildFileTree = (artifacts: ArtifactFile[]): FileNode[] => {
    const root: FileNode[] = [];
    const pathMap = new Map<string, FileNode>();

    artifacts.forEach(artifact => {
      const parts = artifact.filePath.split('/').filter(Boolean);
      let currentPath = '';
      let currentLevel = root;

      parts.forEach((part, index) => {
        currentPath = currentPath ? `${currentPath}/${part}` : part;
        
        let node = pathMap.get(currentPath);
        if (!node) {
          node = {
            name: part,
            type: index === parts.length - 1 ? 'file' : 'folder',
            children: index === parts.length - 1 ? undefined : [],
            artifact: index === parts.length - 1 ? artifact : undefined,
          };
          pathMap.set(currentPath, node);
          currentLevel.push(node);
        }
        
        if (node.children) {
          currentLevel = node.children;
        }
      });
    });

    return root;
  };

  const toggleFolder = (path: string) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedFolders(newExpanded);
  };

  const getFileIcon = (fileName: string) => {
    const ext = fileName.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'js':
      case 'ts':
      case 'jsx':
      case 'tsx':
      case 'py':
      case 'java':
      case 'cpp':
      case 'c':
      case 'cs':
        return <FileCode className="h-4 w-4 text-blue-600" />;
      case 'png':
      case 'jpg':
      case 'jpeg':
      case 'gif':
      case 'svg':
        return <FileImage className="h-4 w-4 text-green-600" />;
      case 'md':
      case 'txt':
      case 'doc':
      case 'docx':
        return <FileText className="h-4 w-4 text-gray-600" />;
      default:
        return <File className="h-4 w-4 text-gray-600" />;
    }
  };

  const renderNode = (node: FileNode, path: string = '', level: number = 0) => {
    const fullPath = path ? `${path}/${node.name}` : node.name;
    const isExpanded = expandedFolders.has(fullPath);
    const isSelected = selectedFile?.id === node.artifact?.id;

    return (
      <div key={fullPath}>
        <Button
          variant={isSelected ? "secondary" : "ghost"}
          size="sm"
          className={`w-full justify-start text-left mb-1 ${level > 0 ? `ml-${level * 4}` : ''}`}
          onClick={() => {
            if (node.type === 'folder') {
              toggleFolder(fullPath);
            } else if (node.artifact && onFileSelect) {
              onFileSelect(node.artifact);
            }
          }}
        >
          <div className="flex items-center space-x-2" style={{ paddingLeft: `${level * 16}px` }}>
            {node.type === 'folder' ? (
              <>
                {isExpanded ? (
                  <ChevronDown className="h-4 w-4" />
                ) : (
                  <ChevronRight className="h-4 w-4" />
                )}
                <Folder className="h-4 w-4 text-yellow-600" />
              </>
            ) : (
              getFileIcon(node.name)
            )}
            <span className="truncate">{node.name}</span>
          </div>
        </Button>
        
        {node.type === 'folder' && isExpanded && node.children && (
          <div>
            {node.children.map(child => renderNode(child, fullPath, level + 1))}
          </div>
        )}
      </div>
    );
  };

  const fileTree = buildFileTree(artifacts);

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card className="h-full">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">File Explorer</CardTitle>
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-1" />
              Download All
            </Button>
          </div>
          <p className="text-sm text-muted-foreground">
            {artifacts.length} file{artifacts.length !== 1 ? 's' : ''} generated
          </p>
        </CardHeader>
        
        <CardContent className="p-0">
          <ScrollArea className="h-96 px-4 pb-4">
            {fileTree.length > 0 ? (
              <div className="space-y-1">
                {fileTree.map(node => renderNode(node))}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-muted-foreground">No files generated yet</p>
              </div>
            )}
          </ScrollArea>
        </CardContent>
      </Card>
    </motion.div>
  );
}