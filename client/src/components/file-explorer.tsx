import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FolderTree, ChevronRight, ChevronDown, FileCode, FileText, Folder } from 'lucide-react';
import type { ArtifactFile } from '@/types/agent';

interface FileNode {
  name: string;
  path: string;
  type: 'file' | 'folder';
  children?: FileNode[];
  artifact?: ArtifactFile;
}

interface FileExplorerProps {
  artifacts: ArtifactFile[];
  onFileClick: (artifact: ArtifactFile) => void;
  selectedFile?: string;
}

export function FileExplorer({ artifacts, onFileClick, selectedFile }: FileExplorerProps) {
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());

  // Build file tree from artifacts
  const buildFileTree = (artifacts: ArtifactFile[]): FileNode[] => {
    const root: FileNode[] = [];
    const folderMap = new Map<string, FileNode>();

    artifacts.forEach(artifact => {
      const parts = artifact.filePath.split('/');
      let currentPath = '';
      let currentLevel = root;

      for (let i = 0; i < parts.length; i++) {
        const part = parts[i];
        currentPath = currentPath ? `${currentPath}/${part}` : part;
        
        if (i === parts.length - 1) {
          // This is a file
          currentLevel.push({
            name: part,
            path: currentPath,
            type: 'file',
            artifact
          });
        } else {
          // This is a folder
          let folder = folderMap.get(currentPath);
          if (!folder) {
            folder = {
              name: part,
              path: currentPath,
              type: 'folder',
              children: []
            };
            folderMap.set(currentPath, folder);
            currentLevel.push(folder);
          }
          currentLevel = folder.children!;
        }
      }
    });

    return root;
  };

  const fileTree = buildFileTree(artifacts);

  const toggleFolder = (path: string) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedFolders(newExpanded);
  };

  const getFileIcon = (name: string) => {
    const extension = name.split('.').pop()?.toLowerCase();
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

  const renderNode = (node: FileNode, depth = 0): React.ReactNode => {
    const paddingLeft = depth * 24;
    const isExpanded = expandedFolders.has(node.path);
    const isSelected = selectedFile === node.path;

    if (node.type === 'folder') {
      return (
        <div key={node.path}>
          <div
            className={`flex items-center space-x-2 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded cursor-pointer text-sm ${
              isSelected ? 'bg-primary/10' : ''
            }`}
            style={{ paddingLeft: paddingLeft + 8 }}
            onClick={() => toggleFolder(node.path)}
          >
            {isExpanded ? (
              <ChevronDown className="h-4 w-4 text-gray-400" />
            ) : (
              <ChevronRight className="h-4 w-4 text-gray-400" />
            )}
            <Folder className="h-4 w-4 text-blue-500" />
            <span className="text-gray-700 dark:text-gray-300">{node.name}</span>
          </div>
          {isExpanded && node.children && (
            <div>
              {node.children.map(child => renderNode(child, depth + 1))}
            </div>
          )}
        </div>
      );
    }

    return (
      <div
        key={node.path}
        className={`flex items-center space-x-2 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded cursor-pointer text-sm ${
          isSelected ? 'bg-primary/10' : ''
        }`}
        style={{ paddingLeft: paddingLeft + 32 }}
        onClick={() => node.artifact && onFileClick(node.artifact)}
      >
        {getFileIcon(node.name)}
        <span className="text-gray-700 dark:text-gray-300">{node.name}</span>
        {node.artifact && (
          <span className="ml-auto px-1.5 py-0.5 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded text-xs">
            new
          </span>
        )}
      </div>
    );
  };

  return (
    <Card className="bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
      <CardHeader className="p-4 border-b border-gray-200 dark:border-gray-700">
        <CardTitle className="text-gray-900 dark:text-white">
          <FolderTree className="inline mr-2 h-5 w-5 text-primary" />
          Project Files
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4">
        {fileTree.length === 0 ? (
          <div className="text-center text-gray-400 dark:text-gray-500 py-8">
            <FolderTree className="h-8 w-8 mx-auto mb-2" />
            <p className="text-sm">No files generated yet</p>
          </div>
        ) : (
          <div className="space-y-1">
            {fileTree.map(node => renderNode(node))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
