import { useMemo, useState } from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, Pin } from 'lucide-react';
import { Button } from '@/components/ui/button';
import type { LogEntry } from '@/types/agent';

interface VirtualizedLogListProps {
  logs: LogEntry[];
  className?: string;
}

export function VirtualizedLogList({ logs, className }: VirtualizedLogListProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [levelFilter, setLevelFilter] = useState<string>('all');
  const [pinnedLogs, setPinnedLogs] = useState<Set<string>>(new Set());

  const filteredLogs = useMemo(() => {
    return logs.filter(log => {
      const matchesSearch = log.message.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesLevel = levelFilter === 'all' || log.level === levelFilter;
      return matchesSearch && matchesLevel;
    });
  }, [logs, searchTerm, levelFilter]);

  const togglePin = (logId: string) => {
    const newPinned = new Set(pinnedLogs);
    if (newPinned.has(logId)) {
      newPinned.delete(logId);
    } else {
      newPinned.add(logId);
    }
    setPinnedLogs(newPinned);
  };

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'ERROR':
        return 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200';
      case 'WARN':
        return 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200';
      case 'INFO':
        return 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200';
      case 'DEBUG':
        return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200';
      default:
        return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200';
    }
  };

  const formatTimestamp = (timestamp: Date) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  return (
    <div className={className}>
      {/* Search and Filter Controls */}
      <div className="flex items-center space-x-2 mb-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search logs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9 text-sm bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600"
          />
        </div>
        <select
          value={levelFilter}
          onChange={(e) => setLevelFilter(e.target.value)}
          className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          <option value="all">All Levels</option>
          <option value="ERROR">Error</option>
          <option value="WARN">Warning</option>
          <option value="INFO">Info</option>
          <option value="DEBUG">Debug</option>
        </select>
      </div>

      {/* Log Display */}
      <ScrollArea className="h-48 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700">
        <div className="p-3 font-mono text-sm space-y-1">
          {filteredLogs.length === 0 ? (
            <div className="text-center text-gray-400 dark:text-gray-500 py-8">
              {logs.length === 0 ? 'No logs available' : 'No logs match your filters'}
            </div>
          ) : (
            filteredLogs.map((log) => (
              <div
                key={log.id}
                className={`flex items-start space-x-2 p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-800 group ${
                  pinnedLogs.has(log.id) ? 'bg-yellow-50 dark:bg-yellow-900/10' : ''
                }`}
              >
                <span className="text-xs text-gray-400 w-16 flex-shrink-0 mt-0.5">
                  {formatTimestamp(log.timestamp)}
                </span>
                <Badge
                  className={`text-xs px-1.5 py-0.5 font-medium ${getLevelColor(log.level)}`}
                >
                  {log.level}
                </Badge>
                <span className="text-gray-700 dark:text-gray-300 flex-1 break-words">
                  {log.message}
                </span>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => togglePin(log.id)}
                  className={`h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity ${
                    pinnedLogs.has(log.id) ? 'opacity-100 text-yellow-600' : ''
                  }`}
                >
                  <Pin className="h-3 w-3" />
                </Button>
              </div>
            ))
          )}
        </div>
      </ScrollArea>

      {/* Pinned Logs Section */}
      {pinnedLogs.size > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
            Pinned Logs ({pinnedLogs.size})
          </h4>
          <div className="space-y-1">
            {Array.from(pinnedLogs).map(logId => {
              const log = logs.find(l => l.id === logId);
              if (!log) return null;
              
              return (
                <div
                  key={logId}
                  className="flex items-start space-x-2 p-2 bg-yellow-50 dark:bg-yellow-900/10 rounded text-sm"
                >
                  <span className="text-xs text-gray-400 w-16 flex-shrink-0">
                    {formatTimestamp(log.timestamp)}
                  </span>
                  <Badge className={`text-xs ${getLevelColor(log.level)}`}>
                    {log.level}
                  </Badge>
                  <span className="text-gray-700 dark:text-gray-300 flex-1">
                    {log.message}
                  </span>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => togglePin(log.id)}
                    className="h-5 w-5 p-0 text-yellow-600"
                  >
                    <Pin className="h-3 w-3" />
                  </Button>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
