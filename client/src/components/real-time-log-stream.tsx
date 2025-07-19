import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { 
  Play, 
  Pause, 
  Download, 
  Filter, 
  Search,
  AlertCircle,
  Info,
  CheckCircle,
  XCircle,
  Activity
} from 'lucide-react';
import type { LogEntry } from '@/types/agent';

interface RealTimeLogStreamProps {
  logs: LogEntry[];
  isStreaming?: boolean;
  onToggleStreaming?: () => void;
}

export function RealTimeLogStream({ 
  logs, 
  isStreaming = true, 
  onToggleStreaming 
}: RealTimeLogStreamProps) {
  const [filter, setFilter] = useState('');
  const [levelFilter, setLevelFilter] = useState<string>('all');
  const [isPaused, setIsPaused] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const shouldAutoScroll = useRef(true);

  const filteredLogs = logs.filter(log => {
    const matchesText = filter === '' || 
      log.message.toLowerCase().includes(filter.toLowerCase()) ||
      log.agentName?.toLowerCase().includes(filter.toLowerCase());
    
    const matchesLevel = levelFilter === 'all' || log.level.toLowerCase() === levelFilter;
    
    return matchesText && matchesLevel;
  });

  useEffect(() => {
    if (!isPaused && shouldAutoScroll.current && scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [filteredLogs, isPaused]);

  const handleScroll = () => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        const { scrollTop, scrollHeight, clientHeight } = scrollContainer;
        shouldAutoScroll.current = scrollTop + clientHeight >= scrollHeight - 10;
      }
    }
  };

  const getLogIcon = (level: string) => {
    switch (level.toLowerCase()) {
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'warning':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'info':
        return <Info className="h-4 w-4 text-blue-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getLevelBadge = (level: string) => {
    const colorMap: Record<string, string> = {
      error: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      success: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      info: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      debug: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
    };

    return (
      <Badge 
        variant="outline" 
        className={`text-xs ${colorMap[level.toLowerCase()] || colorMap.debug}`}
      >
        {level.toUpperCase()}
      </Badge>
    );
  };

  const exportLogs = () => {
    const logContent = filteredLogs
      .map(log => `[${log.timestamp.toISOString()}] [${log.level}] ${log.agentName || 'System'}: ${log.message}`)
      .join('\n');
    
    const blob = new Blob([logContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `session-logs-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const levelCounts = logs.reduce((acc, log) => {
    const level = log.level.toLowerCase();
    acc[level] = (acc[level] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center space-x-2">
              <Activity className={`h-5 w-5 ${isStreaming ? 'text-green-500 animate-pulse' : 'text-gray-500'}`} />
              <span>Real-time Logs</span>
              {isStreaming && (
                <Badge className="bg-green-100 text-green-800 animate-pulse">
                  Live
                </Badge>
              )}
            </CardTitle>
            
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsPaused(!isPaused)}
              >
                {isPaused ? (
                  <Play className="h-4 w-4 mr-1" />
                ) : (
                  <Pause className="h-4 w-4 mr-1" />
                )}
                {isPaused ? 'Resume' : 'Pause'}
              </Button>
              
              <Button variant="outline" size="sm" onClick={exportLogs}>
                <Download className="h-4 w-4 mr-1" />
                Export
              </Button>
            </div>
          </div>
          
          {/* Filters */}
          <div className="flex items-center space-x-4 mt-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search logs..."
                  value={filter}
                  onChange={(e) => setFilter(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button
                variant={levelFilter === 'all' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setLevelFilter('all')}
              >
                All ({logs.length})
              </Button>
              {Object.entries(levelCounts).map(([level, count]) => (
                <Button
                  key={level}
                  variant={levelFilter === level ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setLevelFilter(level)}
                  className="capitalize"
                >
                  {level} ({count})
                </Button>
              ))}
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="p-0">
          <ScrollArea 
            ref={scrollAreaRef}
            className="h-96 px-4 pb-4"
            onScrollCapture={handleScroll}
          >
            <div className="space-y-2">
              <AnimatePresence>
                {filteredLogs.map((log, index) => (
                  <motion.div
                    key={log.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ duration: 0.2 }}
                    className="flex items-start space-x-3 p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
                  >
                    <div className="mt-0.5">
                      {getLogIcon(log.level)}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center space-x-2">
                          {getLevelBadge(log.level)}
                          {log.agentName && (
                            <Badge variant="outline" className="text-xs">
                              {log.agentName}
                            </Badge>
                          )}
                        </div>
                        <span className="text-xs text-muted-foreground">
                          {log.timestamp.toLocaleTimeString()}
                        </span>
                      </div>
                      
                      <p className="text-sm break-words">{log.message}</p>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              
              {filteredLogs.length === 0 && (
                <div className="text-center py-8">
                  <p className="text-muted-foreground">
                    {filter || levelFilter !== 'all' 
                      ? 'No logs match the current filters' 
                      : 'No logs available yet'
                    }
                  </p>
                </div>
              )}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </motion.div>
  );
}