import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Activity,
  Terminal,
  AlertTriangle,
  CheckCircle,
  Info,
  X,
  Download,
  Search,
  Filter,
  Pause,
  Play
} from 'lucide-react';
import { Input } from '@/components/ui/input';
import type { AgentEvent } from '@shared/schema';

interface LogEntry {
  id: string;
  timestamp: Date;
  level: string;
  message: string;
  component?: string;
  agentId?: string;
  agentName?: string;
  sequence: number;
}

interface RealTimeLogStreamProps {
  events: AgentEvent[];
  agents?: any[];
  className?: string;
  maxLogs?: number;
  autoScroll?: boolean;
}

const LogLevelColors = {
  ERROR: 'text-red-600 bg-red-50 border-red-200',
  WARN: 'text-yellow-600 bg-yellow-50 border-yellow-200',
  INFO: 'text-blue-600 bg-blue-50 border-blue-200',
  DEBUG: 'text-gray-600 bg-gray-50 border-gray-200',
  SUCCESS: 'text-green-600 bg-green-50 border-green-200'
};

const LogLevelIcons = {
  ERROR: AlertTriangle,
  WARN: AlertTriangle,
  INFO: Info,
  DEBUG: Terminal,
  SUCCESS: CheckCircle
};

export function RealTimeLogStream({
  events = [],
  agents = [],
  className = '',
  maxLogs = 500,
  autoScroll = true
}: RealTimeLogStreamProps) {
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const [isPaused, setIsPaused] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterLevel, setFilterLevel] = useState<string>('');
  const [isAtBottom, setIsAtBottom] = useState(true);

  // Convert events to log entries
  const logEntries: LogEntry[] = events
    .filter(event => event.type === 'LOG')
    .map(event => {
      const agent = agents.find(a => a.id === event.agentId);
      return {
        id: event.id,
        timestamp: new Date(event.timestamp),
        level: event.payload.level || 'INFO',
        message: event.payload.message || '',
        component: event.payload.component,
        agentId: event.agentId || undefined,
        agentName: agent?.name,
        sequence: event.sequence
      };
    })
    .sort((a, b) => a.sequence - b.sequence)
    .slice(-maxLogs);

  // Filter logs based on search and level
  const filteredLogs = logEntries.filter(log => {
    const matchesSearch = !searchQuery || 
      log.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.agentName?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.component?.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesLevel = !filterLevel || log.level === filterLevel;
    
    return matchesSearch && matchesLevel;
  });

  // Auto scroll to bottom when new logs arrive
  useEffect(() => {
    if (autoScroll && !isPaused && isAtBottom && scrollAreaRef.current) {
      const scrollElement = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollElement) {
        scrollElement.scrollTop = scrollElement.scrollHeight;
      }
    }
  }, [logEntries.length, autoScroll, isPaused, isAtBottom]);

  // Handle scroll to detect if user is at bottom
  const handleScroll = (e: React.UIEvent) => {
    const target = e.target as HTMLElement;
    const atBottom = target.scrollTop + target.clientHeight >= target.scrollHeight - 10;
    setIsAtBottom(atBottom);
  };

  const formatTimestamp = (timestamp: Date) => {
    return timestamp.toLocaleTimeString('en-US', { 
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      fractionalSecondDigits: 3
    });
  };

  const downloadLogs = () => {
    const logsText = filteredLogs
      .map(log => `[${formatTimestamp(log.timestamp)}] ${log.level} ${log.agentName || 'System'}: ${log.message}`)
      .join('\n');
    
    const blob = new Blob([logsText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `session-logs-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const levelCounts = logEntries.reduce((acc, log) => {
    acc[log.level] = (acc[log.level] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <Card className={className}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center space-x-2">
            <Activity className="w-5 h-5 text-primary" />
            <span>Real-time Logs</span>
            <Badge variant="secondary" className="text-xs">
              {filteredLogs.length} / {logEntries.length}
            </Badge>
          </CardTitle>
          
          <div className="flex items-center space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsPaused(!isPaused)}
              className="text-xs"
            >
              {isPaused ? <Play className="w-3 h-3" /> : <Pause className="w-3 h-3" />}
              {isPaused ? 'Resume' : 'Pause'}
            </Button>
            
            <Button
              variant="ghost"
              size="sm"
              onClick={downloadLogs}
              className="text-xs"
            >
              <Download className="w-3 h-3 mr-1" />
              Export
            </Button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center space-x-2 mt-3">
          <div className="relative flex-1">
            <Search className="absolute left-2 top-2.5 w-3 h-3 text-muted-foreground" />
            <Input
              placeholder="Search logs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-7 h-8 text-xs"
            />
            {searchQuery && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSearchQuery('')}
                className="absolute right-1 top-1 h-6 w-6 p-0"
              >
                <X className="w-3 h-3" />
              </Button>
            )}
          </div>
          
          <select
            value={filterLevel}
            onChange={(e) => setFilterLevel(e.target.value)}
            className="h-8 text-xs border rounded px-2 bg-background"
          >
            <option value="">All Levels</option>
            <option value="ERROR">Error</option>
            <option value="WARN">Warning</option>
            <option value="INFO">Info</option>
            <option value="DEBUG">Debug</option>
            <option value="SUCCESS">Success</option>
          </select>
        </div>

        {/* Level statistics */}
        <div className="flex items-center space-x-2 mt-2">
          {Object.entries(levelCounts).map(([level, count]) => (
            <Badge
              key={level}
              variant="outline"
              className={`text-xs ${LogLevelColors[level as keyof typeof LogLevelColors] || LogLevelColors.INFO}`}
            >
              {level}: {count}
            </Badge>
          ))}
        </div>
      </CardHeader>

      <CardContent className="p-0">
        <ScrollArea 
          ref={scrollAreaRef}
          className="h-96 w-full"
          onScrollCapture={handleScroll}
        >
          <div className="p-4 space-y-1">
            <AnimatePresence mode="popLayout">
              {filteredLogs.length === 0 ? (
                <motion.div
                  className="text-center py-8 text-muted-foreground"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <Terminal className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">
                    {searchQuery || filterLevel ? 'No matching logs found' : 'No logs yet...'}
                  </p>
                </motion.div>
              ) : (
                filteredLogs.map((log, index) => {
                  const IconComponent = LogLevelIcons[log.level as keyof typeof LogLevelIcons] || Info;
                  const colorClasses = LogLevelColors[log.level as keyof typeof LogLevelColors] || LogLevelColors.INFO;
                  
                  return (
                    <motion.div
                      key={log.id}
                      className="flex items-start space-x-2 text-xs font-mono p-2 rounded border hover:bg-muted/50 transition-colors"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      transition={{ duration: 0.2, delay: Math.min(index * 0.02, 0.5) }}
                    >
                      <div className={`flex items-center space-x-1 px-2 py-1 rounded text-xs border ${colorClasses}`}>
                        <IconComponent className="w-3 h-3" />
                        <span className="font-medium">{log.level}</span>
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2 mb-1">
                          <span className="text-muted-foreground">
                            {formatTimestamp(log.timestamp)}
                          </span>
                          
                          {log.agentName && (
                            <Badge variant="outline" className="text-xs">
                              {log.agentName}
                            </Badge>
                          )}
                          
                          {log.component && (
                            <Badge variant="secondary" className="text-xs">
                              {log.component}
                            </Badge>
                          )}
                        </div>
                        
                        <div className="text-foreground break-words">
                          {log.message}
                        </div>
                      </div>
                    </motion.div>
                  );
                })
              )}
            </AnimatePresence>
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}