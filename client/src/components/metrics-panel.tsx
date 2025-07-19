import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  BarChart3, 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  AlertTriangle,
  FileText,
  Activity,
  Zap
} from 'lucide-react';

interface MetricsPanelProps {
  metrics?: {
    totalTasks: number;
    activeTasks: number;
    completedTasks: number;
    failedTasks: number;
    avgCompletionTime?: number;
    successRate?: number;
    accuracyRate?: number;
  };
  eventCount: number;
  codeLines: number;
  filesGenerated: number;
}

export function MetricsPanel({ 
  metrics, 
  eventCount, 
  codeLines, 
  filesGenerated 
}: MetricsPanelProps) {
  const completionRate = metrics ? 
    (metrics.completedTasks / Math.max(metrics.totalTasks, 1)) * 100 : 0;
  
  const successRate = metrics?.successRate || 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center space-x-2 text-base">
            <BarChart3 className="w-5 h-5 text-primary" />
            <span>Session Metrics</span>
          </CardTitle>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {/* Key Stats */}
          <div className="grid grid-cols-2 gap-3">
            <motion.div
              className="bg-blue-50 dark:bg-blue-900/20 p-3 rounded-lg border border-blue-200 dark:border-blue-800"
              whileHover={{ scale: 1.02 }}
              transition={{ duration: 0.2 }}
            >
              <div className="flex items-center space-x-2">
                <Activity className="w-4 h-4 text-blue-600" />
                <span className="text-sm font-medium">Events</span>
              </div>
              <div className="text-2xl font-bold text-blue-600">{eventCount}</div>
            </motion.div>

            <motion.div
              className="bg-green-50 dark:bg-green-900/20 p-3 rounded-lg border border-green-200 dark:border-green-800"
              whileHover={{ scale: 1.02 }}
              transition={{ duration: 0.2 }}
            >
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4 text-green-600" />
                <span className="text-sm font-medium">Files</span>
              </div>
              <div className="text-2xl font-bold text-green-600">{filesGenerated}</div>
            </motion.div>

            <motion.div
              className="bg-purple-50 dark:bg-purple-900/20 p-3 rounded-lg border border-purple-200 dark:border-purple-800"
              whileHover={{ scale: 1.02 }}
              transition={{ duration: 0.2 }}
            >
              <div className="flex items-center space-x-2">
                <Zap className="w-4 h-4 text-purple-600" />
                <span className="text-sm font-medium">Lines</span>
              </div>
              <div className="text-2xl font-bold text-purple-600">{codeLines}</div>
            </motion.div>

            <motion.div
              className="bg-orange-50 dark:bg-orange-900/20 p-3 rounded-lg border border-orange-200 dark:border-orange-800"
              whileHover={{ scale: 1.02 }}
              transition={{ duration: 0.2 }}
            >
              <div className="flex items-center space-x-2">
                <TrendingUp className="w-4 h-4 text-orange-600" />
                <span className="text-sm font-medium">Success</span>
              </div>
              <div className="text-2xl font-bold text-orange-600">{Math.round(successRate)}%</div>
            </motion.div>
          </div>

          {/* Progress Bars */}
          {metrics && (
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-medium">Task Completion</span>
                  <span>{Math.round(completionRate)}%</span>
                </div>
                <Progress value={completionRate} className="h-2" />
                <div className="flex justify-between text-xs text-muted-foreground mt-1">
                  <span>{metrics.completedTasks} completed</span>
                  <span>{metrics.totalTasks} total</span>
                </div>
              </div>

              {successRate > 0 && (
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium">Success Rate</span>
                    <span>{Math.round(successRate)}%</span>
                  </div>
                  <Progress value={successRate} className="h-2" />
                </div>
              )}
            </div>
          )}

          {/* Task Breakdown */}
          {metrics && (
            <div className="grid grid-cols-3 gap-2 pt-2 border-t">
              <div className="text-center">
                <div className="flex items-center justify-center space-x-1 text-blue-600">
                  <Clock className="w-3 h-3" />
                  <span className="text-xs font-medium">Active</span>
                </div>
                <div className="text-sm font-bold">{metrics.activeTasks}</div>
              </div>

              <div className="text-center">
                <div className="flex items-center justify-center space-x-1 text-green-600">
                  <CheckCircle className="w-3 h-3" />
                  <span className="text-xs font-medium">Done</span>
                </div>
                <div className="text-sm font-bold">{metrics.completedTasks}</div>
              </div>

              <div className="text-center">
                <div className="flex items-center justify-center space-x-1 text-red-600">
                  <AlertTriangle className="w-3 h-3" />
                  <span className="text-xs font-medium">Failed</span>
                </div>
                <div className="text-sm font-bold">{metrics.failedTasks}</div>
              </div>
            </div>
          )}

          {/* Average Completion Time */}
          {metrics?.avgCompletionTime && (
            <div className="pt-2 border-t">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium">Avg. Completion Time</span>
                <Badge variant="secondary">
                  {Math.round(metrics.avgCompletionTime)}s
                </Badge>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}