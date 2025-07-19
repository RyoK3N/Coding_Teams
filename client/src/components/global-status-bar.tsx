import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { 
  Play, 
  Pause, 
  Square, 
  RotateCcw, 
  Download, 
  Clock, 
  Users, 
  FileText,
  Activity
} from 'lucide-react';
import type { Session } from '@shared/schema';

interface GlobalStatusBarProps {
  session: Session;
  onDownload: () => void;
  onPause: () => void;
  onRegenerate: () => void;
}

export function GlobalStatusBar({ 
  session, 
  onDownload, 
  onPause, 
  onRegenerate 
}: GlobalStatusBarProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'failed':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'analyzing':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = () => {
    switch (session.status) {
      case 'running':
        return <Activity className="w-4 h-4 animate-pulse" />;
      case 'completed':
        return <Play className="w-4 h-4" />;
      case 'failed':
        return <Square className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card className="bg-gradient-to-r from-white to-gray-50 dark:from-gray-800 dark:to-gray-900 border-primary/20">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            {/* Status and Info */}
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-3">
                <motion.div
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg border ${getStatusColor(session.status)}`}
                  whileHover={{ scale: 1.02 }}
                >
                  {getStatusIcon()}
                  <span className="font-medium capitalize">{session.status}</span>
                </motion.div>
                
                <div className="text-sm text-muted-foreground">
                  Session: {session.id.slice(0, 8)}...
                </div>
              </div>

              {/* Metrics */}
              <div className="flex items-center space-x-4 text-sm">
                <div className="flex items-center space-x-1">
                  <Users className="w-4 h-4 text-primary" />
                  <span>8 Agents</span>
                </div>
                
                <div className="flex items-center space-x-1">
                  <FileText className="w-4 h-4 text-green-600" />
                  <span>{session.filesCreated || 0} Files</span>
                </div>
                
                {session.duration && (
                  <div className="flex items-center space-x-1">
                    <Clock className="w-4 h-4 text-blue-600" />
                    <span>{Math.round(session.duration)}s</span>
                  </div>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center space-x-2">
              {session.status === 'running' && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onPause}
                  className="text-yellow-600 border-yellow-300 hover:bg-yellow-50"
                >
                  <Pause className="w-4 h-4 mr-1" />
                  Pause
                </Button>
              )}

              <Button
                variant="outline"
                size="sm"
                onClick={onRegenerate}
                className="text-blue-600 border-blue-300 hover:bg-blue-50"
              >
                <RotateCcw className="w-4 h-4 mr-1" />
                Regenerate
              </Button>

              <Button
                variant="default"
                size="sm"
                onClick={onDownload}
                className="bg-primary hover:bg-primary/90"
              >
                <Download className="w-4 h-4 mr-1" />
                Download All
              </Button>
            </div>
          </div>

          {/* Progress bar for running sessions */}
          {session.status === 'running' && session.workPackagesTotal && (
            <motion.div
              className="mt-4"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              transition={{ delay: 0.3 }}
            >
              <div className="flex justify-between text-sm text-muted-foreground mb-2">
                <span>Work Packages Progress</span>
                <span>
                  {session.workPackagesCompleted || 0} / {session.workPackagesTotal}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <motion.div
                  className="bg-primary h-2 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ 
                    width: `${((session.workPackagesCompleted || 0) / session.workPackagesTotal) * 100}%`
                  }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            </motion.div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}