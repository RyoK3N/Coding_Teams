import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { 
  Folder, 
  FolderOpen, 
  File, 
  ChevronDown, 
  ChevronRight,
  FileText,
  Code,
  Database,
  Settings
} from 'lucide-react';
import type { Artifact } from '@shared/schema';

interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'folder';
  children?: FileNode[];
  artifact?: Artifact;
}

interface FileExplorerProps {
  artifacts: Artifact[];
  onFileClick?: (artifact: Artifact) => void;
  selectedFile?: string;
}

export function FileExplorer({ artifacts, onFileClick, selectedFile }: FileExplorerProps) {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());

  // Build file tree from artifacts
  const buildFileTree = (artifacts: Artifact[]): FileNode[] => {
    const root: { [key: string]: FileNode } = {};

    artifacts.forEach(artifact => {
      if (!artifact.filePath) return;

      const parts = artifact.filePath.split('/').filter(part => part.length > 0);
      let current = root;

      parts.forEach((part, index) => {
        const isFile = index === parts.length - 1;
        const path = parts.slice(0, index + 1).join('/');

        if (!current[part]) {
          current[part] = {
            name: part,
            path,
            type: isFile ? 'file' : 'folder',
            children: isFile ? undefined : {},
            artifact: isFile ? artifact : undefined
          };
        }

        if (!isFile) {
          current = current[part].children!;
        }
      });
    });

    const convertToArray = (obj: { [key: string]: FileNode }): FileNode[] => {
      return Object.values(obj).map(node => ({
        ...node,
        children: node.children ? convertToArray(node.children) : undefined
      })).sort((a, b) => {
        // Folders first, then files
        if (a.type !== b.type) {
          return a.type === 'folder' ? -1 : 1;
        }
        return a.name.localeCompare(b.name);
      });
    };

    return convertToArray(root);
  };

  const getFileIcon = (fileName: string) => {
    const ext = fileName.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'js':
      case 'ts':
      case 'jsx':
      case 'tsx':
        return Code;
      case 'json':
        return Database;
      case 'md':
        return FileText;
      case 'yml':
      case 'yaml':
        return Settings;
      default:
        return File;
    }
  };

  const toggleFolder = (path: string) => {
    setExpandedFolders(prev => {
      const next = new Set(prev);
      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }
      return next;
    });
  };

  const renderNode = (node: FileNode, depth = 0) => {
    const isExpanded = expandedFolders.has(node.path);
    const isSelected = selectedFile === node.path;

    if (node.type === 'folder') {
      return (
        <div key={node.path}>
          <motion.div
            className={`flex items-center space-x-2 px-2 py-1 rounded cursor-pointer hover:bg-muted/50 transition-colors`}
            style={{ paddingLeft: `${depth * 12 + 8}px` }}
            onClick={() => toggleFolder(node.path)}
            whileHover={{ backgroundColor: 'var(--muted)' }}
            whileTap={{ scale: 0.98 }}
          >
            <motion.div
              animate={{ rotate: isExpanded ? 90 : 0 }}
              transition={{ duration: 0.2 }}
            >
              <ChevronRight className="w-4 h-4 text-muted-foreground" />
            </motion.div>
            {isExpanded ? (
              <FolderOpen className="w-4 h-4 text-blue-500" />
            ) : (
              <Folder className="w-4 h-4 text-blue-500" />
            )}
            <span className="text-sm font-medium">{node.name}</span>
          </motion.div>
          
          <AnimatePresence>
            {isExpanded && node.children && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.2 }}
              >
                {node.children.map(child => renderNode(child, depth + 1))}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      );
    }

    const IconComponent = getFileIcon(node.name);

    return (
      <motion.div
        key={node.path}
        className={`flex items-center space-x-2 px-2 py-1 rounded cursor-pointer transition-colors ${
          isSelected 
            ? 'bg-primary/10 text-primary border-l-2 border-primary' 
            : 'hover:bg-muted/50'
        }`}
        style={{ paddingLeft: `${depth * 12 + 24}px` }}
        onClick={() => node.artifact && onFileClick?.(node.artifact)}
        whileHover={{ backgroundColor: isSelected ? undefined : 'var(--muted)' }}
        whileTap={{ scale: 0.98 }}
      >
        <IconComponent className={`w-4 h-4 ${isSelected ? 'text-primary' : 'text-muted-foreground'}`} />
        <span className={`text-sm ${isSelected ? 'font-medium' : ''}`}>{node.name}</span>
        {node.artifact && (
          <span className="text-xs text-muted-foreground ml-auto">
            {node.artifact.size ? `${Math.round(node.artifact.size / 1024)}KB` : ''}
          </span>
        )}
      </motion.div>
    );
  };

  const fileTree = buildFileTree(artifacts);

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center space-x-2 text-base">
          <Folder className="w-5 h-5 text-primary" />
          <span>Project Files</span>
          <span className="text-xs text-muted-foreground ml-auto">
            {artifacts.length} files
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <ScrollArea className="h-64 w-full">
          <div className="p-2">
            {fileTree.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Folder className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No files generated yet</p>
              </div>
            ) : (
              <div className="space-y-1">
                {fileTree.map(node => renderNode(node))}
              </div>
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}