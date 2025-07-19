import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { 
  TrendingUp, 
  Clock, 
  Target, 
  Activity,
  CheckCircle,
  XCircle,
  Users,
  FileText
} from 'lucide-react';
import type { SessionData, AgentStatus } from '@/types/agent';

interface MetricsPanelProps {
  session: SessionData;
  agents: AgentStatus[];
}

export function MetricsPanel({ session, agents }: MetricsPanelProps) {
  const metrics = session.metrics || {
    totalTasks: 0,
    activeTasks: 0,
    completedTasks: 0,
    failedTasks: 0,
    avgCompletionTime: 0,
    successRate: 0,
    accuracyRate: 0,
  };

  const totalFiles = agents.reduce((sum, agent) => sum + (agent.filesCreated || 0), 0);
  const avgProgress = agents.length > 0 
    ? Math.round(agents.reduce((sum, agent) => sum + agent.progress, 0) / agents.length)
    : 0;
  
  const completedAgents = agents.filter(agent => agent.status === 'succeeded').length;
  const failedAgents = agents.filter(agent => agent.status === 'failed').length;
  const runningAgents = agents.filter(agent => agent.status === 'running').length;

  const successRate = agents.length > 0 
    ? Math.round((completedAgents / agents.length) * 100)
    : 0;

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '0s';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
  };

  const metricCards = [
    {
      title: 'Overall Progress',
      value: `${avgProgress}%`,
      icon: TrendingUp,
      color: 'text-blue-600',
      progress: avgProgress,
    },
    {
      title: 'Success Rate',
      value: `${successRate}%`,
      icon: Target,
      color: 'text-green-600',
      progress: successRate,
    },
    {
      title: 'Active Agents',
      value: runningAgents.toString(),
      icon: Activity,
      color: 'text-orange-600',
      subtitle: `of ${agents.length} total`,
    },
    {
      title: 'Files Created',
      value: totalFiles.toString(),
      icon: FileText,
      color: 'text-purple-600',
      subtitle: 'across all agents',
    },
    {
      title: 'Completed Tasks',
      value: completedAgents.toString(),
      icon: CheckCircle,
      color: 'text-green-600',
      subtitle: 'agents finished',
    },
    {
      title: 'Failed Tasks',
      value: failedAgents.toString(),
      icon: XCircle,
      color: 'text-red-600',
      subtitle: 'require attention',
    },
    {
      title: 'Session Duration',
      value: formatDuration(session.duration),
      icon: Clock,
      color: 'text-gray-600',
      subtitle: 'total time',
    },
    {
      title: 'Work Packages',
      value: `${session.workPackagesCompleted || 0}/${session.workPackagesTotal || 0}`,
      icon: Users,
      color: 'text-indigo-600',
      subtitle: 'completed',
    },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5" />
            <span>Session Metrics</span>
          </CardTitle>
        </CardHeader>
        
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {metricCards.map((metric, index) => (
              <motion.div
                key={metric.title}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
              >
                <Card className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <metric.icon className={`h-5 w-5 ${metric.color}`} />
                    <span className="text-2xl font-bold">{metric.value}</span>
                  </div>
                  
                  <div className="space-y-1">
                    <p className="text-sm font-medium">{metric.title}</p>
                    {metric.subtitle && (
                      <p className="text-xs text-muted-foreground">{metric.subtitle}</p>
                    )}
                    
                    {metric.progress !== undefined && (
                      <Progress value={metric.progress} className="h-1 mt-2" />
                    )}
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}