import { motion } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { 
  Play, 
  Pause, 
  Square, 
  Clock, 
  FileText, 
  Users, 
  Activity,
  CheckCircle,
  XCircle
} from 'lucide-react';
import type { SessionData, AgentStatus } from '@/types/agent';

interface GlobalStatusBarProps {
  session: SessionData;
  agents: AgentStatus[];
  onPause?: () => void;
  onResume?: () => void;
  onStop?: () => void;
}

export function GlobalStatusBar({ 
  session, 
  agents, 
  onPause, 
  onResume, 
  onStop 
}: GlobalStatusBarProps) {
  const runningAgents = agents.filter(agent => agent.status === 'running').length;
  const completedAgents = agents.filter(agent => agent.status === 'succeeded').length;
  const failedAgents = agents.filter(agent => agent.status === 'failed').length;
  const totalFiles = agents.reduce((sum, agent) => sum + (agent.filesCreated || 0), 0);
  
  const overallProgress = agents.length > 0 
    ? Math.round(agents.reduce((sum, agent) => sum + agent.progress, 0) / agents.length)
    : 0;

  const getStatusBadge = () => {
    switch (session.status) {
      case 'running':
        return <Badge className="bg-green-100 text-green-800 animate-pulse">Running</Badge>;
      case 'completed':
        return <Badge className="bg-blue-100 text-blue-800">Completed</Badge>;
      case 'failed':
        return <Badge className="bg-red-100 text-red-800">Failed</Badge>;
      case 'paused':
        return <Badge className="bg-yellow-100 text-yellow-800">Paused</Badge>;
      default:
        return <Badge className="bg-gray-100 text-gray-800">Pending</Badge>;
    }
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '0s';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card className="mb-6">
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-4">
              <div>
                <h2 className="text-xl font-semibold">Session Status</h2>
                <p className="text-sm text-muted-foreground">Overall Progress: {overallProgress}%</p>
              </div>
              {getStatusBadge()}
            </div>
            
            <div className="flex items-center space-x-2">
              {session.status === 'running' && (
                <>
                  <Button variant="outline" size="sm" onClick={onPause}>
                    <Pause className="h-4 w-4 mr-1" />
                    Pause
                  </Button>
                  <Button variant="outline" size="sm" onClick={onStop}>
                    <Square className="h-4 w-4 mr-1" />
                    Stop
                  </Button>
                </>
              )}
              
              {session.status === 'paused' && (
                <Button variant="outline" size="sm" onClick={onResume}>
                  <Play className="h-4 w-4 mr-1" />
                  Resume
                </Button>
              )}
            </div>
          </div>

          <Progress value={overallProgress} className="mb-4" />

          <div className="grid grid-cols-2 md:grid-cols-6 gap-4 text-sm">
            <div className="flex items-center space-x-2">
              <Users className="h-4 w-4 text-blue-600" />
              <div>
                <p className="font-medium">{agents.length}</p>
                <p className="text-muted-foreground">Total Agents</p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Activity className="h-4 w-4 text-green-600" />
              <div>
                <p className="font-medium">{runningAgents}</p>
                <p className="text-muted-foreground">Active</p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-blue-600" />
              <div>
                <p className="font-medium">{completedAgents}</p>
                <p className="text-muted-foreground">Completed</p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <XCircle className="h-4 w-4 text-red-600" />
              <div>
                <p className="font-medium">{failedAgents}</p>
                <p className="text-muted-foreground">Failed</p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <FileText className="h-4 w-4 text-purple-600" />
              <div>
                <p className="font-medium">{totalFiles}</p>
                <p className="text-muted-foreground">Files Created</p>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-orange-600" />
              <div>
                <p className="font-medium">{formatDuration(session.duration)}</p>
                <p className="text-muted-foreground">Duration</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}