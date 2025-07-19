import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Download, Pause, RefreshCw, Play } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import type { SessionData } from '@/types/agent';

interface GlobalStatusBarProps {
  session: SessionData;
  onDownload: () => void;
  onPause: () => void;
  onRegenerate: () => void;
}

export function GlobalStatusBar({ session, onDownload, onPause, onRegenerate }: GlobalStatusBarProps) {
  const { metrics } = session;
  const overallProgress = metrics.totalTasks > 0 
    ? Math.round((metrics.completedTasks / metrics.totalTasks) * 100)
    : 0;

  const getStatusBadge = () => {
    switch (session.status) {
      case 'running':
        return (
          <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
            <Play className="mr-1 h-3 w-3" />
            Running
          </Badge>
        );
      case 'completed':
        return (
          <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
            Completed
          </Badge>
        );
      case 'failed':
        return (
          <Badge className="bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
            Failed
          </Badge>
        );
      default:
        return (
          <Badge className="bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">
            Pending
          </Badge>
        );
    }
  };

  return (
    <Card className="bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
      <CardContent className="p-6">
        <div className="flex items-center justify-between mb-4">
          <CardTitle className="text-gray-900 dark:text-white">
            Session: <span className="text-primary">{session.id.slice(0, 12)}...</span>
          </CardTitle>
          <div className="flex items-center space-x-2">
            {getStatusBadge()}
            <span className="text-sm text-gray-500 dark:text-gray-400">
              Started {formatDistanceToNow(new Date(session.createdAt))} ago
            </span>
          </div>
        </div>

        {/* Progress Overview */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900 dark:text-white">
              {metrics.totalTasks}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Total Tasks</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-primary">
              {metrics.activeTasks}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Active</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {metrics.completedTasks}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Completed</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">
              {metrics.failedTasks}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">Failed</div>
          </div>
        </div>

        {/* Overall Progress */}
        <div className="mb-4">
          <div className="flex justify-between text-sm mb-2">
            <span className="text-gray-600 dark:text-gray-400">Overall Progress</span>
            <span className="font-medium text-gray-900 dark:text-white">{overallProgress}%</span>
          </div>
          <Progress value={overallProgress} className="h-2" />
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end space-x-3">
          <Button
            variant="ghost"
            onClick={onPause}
            disabled={session.status !== 'running'}
            className="text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
          >
            <Pause className="mr-2 h-4 w-4" />
            Pause
          </Button>
          <Button
            variant="ghost"
            onClick={onDownload}
            className="text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
          >
            <Download className="mr-2 h-4 w-4" />
            Download Artifacts
          </Button>
          <Button
            onClick={onRegenerate}
            className="bg-accent-500 hover:bg-accent-600 text-white"
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            Regenerate
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
