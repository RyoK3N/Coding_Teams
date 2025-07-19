import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp } from 'lucide-react';
import type { SessionMetrics } from '@/types/agent';

interface MetricsPanelProps {
  metrics: SessionMetrics;
  eventCount?: number;
  codeLines?: number;
  filesGenerated?: number;
}

export function MetricsPanel({ 
  metrics, 
  eventCount = 0, 
  codeLines = 0, 
  filesGenerated = 0 
}: MetricsPanelProps) {
  const successRate = metrics.totalTasks > 0 
    ? Math.round((metrics.completedTasks / metrics.totalTasks) * 100)
    : 0;

  const avgTaskTime = metrics.avgCompletionTime || 0;

  // Simple timeline data for demonstration
  const timelineData = Array.from({ length: 12 }, (_, i) => ({
    height: Math.floor(Math.random() * 48) + 16,
    isActive: i === 11,
  }));

  return (
    <Card className="bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
      <CardHeader className="p-4 border-b border-gray-200 dark:border-gray-700">
        <CardTitle className="text-gray-900 dark:text-white">
          <TrendingUp className="inline mr-2 h-5 w-5 text-primary" />
          Session Metrics
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4">
        {/* Key Metrics */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="text-center">
            <div className="text-lg font-bold text-gray-900 dark:text-white">
              {avgTaskTime.toFixed(1)}s
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">
              Avg Task Time
            </div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-green-600">
              {successRate}%
            </div>
            <div className="text-xs text-gray-500 dark:text-gray-400">
              Success Rate
            </div>
          </div>
        </div>

        {/* Timeline Chart */}
        <div className="mb-4">
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">
            Event Timeline
          </div>
          <div className="h-16 bg-gray-50 dark:bg-gray-900 rounded-lg p-2">
            <div className="flex items-end justify-between h-full">
              {timelineData.map((bar, index) => (
                <div
                  key={index}
                  className={`w-1 rounded-t transition-all duration-300 ${
                    bar.isActive 
                      ? 'bg-green-500 animate-pulse' 
                      : 'bg-primary'
                  }`}
                  style={{ height: `${bar.height}px` }}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Detailed Stats */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-600 dark:text-gray-400">Log Events</span>
            <span className="font-medium text-gray-900 dark:text-white">
              {eventCount.toLocaleString()}
            </span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600 dark:text-gray-400">Code Lines</span>
            <span className="font-medium text-gray-900 dark:text-white">
              {codeLines.toLocaleString()}
            </span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-gray-600 dark:text-gray-400">Files Generated</span>
            <span className="font-medium text-gray-900 dark:text-white">
              {filesGenerated}
            </span>
          </div>
          {metrics.avgCompletionTime && (
            <div className="flex justify-between text-sm">
              <span className="text-gray-600 dark:text-gray-400">Avg Completion</span>
              <span className="font-medium text-gray-900 dark:text-white">
                {metrics.avgCompletionTime.toFixed(1)}s
              </span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
