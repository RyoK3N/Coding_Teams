import { useState } from 'react';
import { useLocation } from 'wouter';
import { SessionPromptForm } from '@/components/session-prompt-form';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useSession, useSessions } from '@/hooks/use-session';
import { formatDistanceToNow } from 'date-fns';
import { ArrowRight, Clock, CheckCircle, XCircle, Play } from 'lucide-react';

export default function Home() {
  const [, setLocation] = useLocation();
  const { createSession, isCreatingSession } = useSession(null);
  const sessionsQuery = useSessions();

  const handleCreateSession = async (data: {
    prompt: string;
    includeTests: boolean;
    includeDocumentation: boolean;
  }) => {
    const session = await createSession(data);
    setLocation(`/session/${session.id}`);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <Play className="h-4 w-4 text-green-600" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-blue-600" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-600" />;
      default:
        return <Clock className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'running':
        return <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Running</Badge>;
      case 'completed':
        return <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">Completed</Badge>;
      case 'failed':
        return <Badge className="bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">Failed</Badge>;
      default:
        return <Badge className="bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">Pending</Badge>;
    }
  };

  return (
    <div className="space-y-8">
      {/* Prompt Form */}
      <SessionPromptForm 
        onSubmit={handleCreateSession}
        isLoading={isCreatingSession}
      />

      {/* Recent Sessions */}
      <Card className="bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
        <CardHeader>
          <CardTitle className="text-gray-900 dark:text-white">Recent Sessions</CardTitle>
        </CardHeader>
        <CardContent>
          {sessionsQuery.isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-16 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
                </div>
              ))}
            </div>
          ) : sessionsQuery.data?.length === 0 ? (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">
              <Clock className="h-12 w-12 mx-auto mb-4" />
              <p>No sessions yet. Create your first one above!</p>
            </div>
          ) : (
            <div className="space-y-3">
              {sessionsQuery.data?.map((session: any) => (
                <div
                  key={session.id}
                  className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      {getStatusIcon(session.status)}
                      <span className="font-medium text-gray-900 dark:text-white">
                        {session.id.slice(0, 8)}...
                      </span>
                      {getStatusBadge(session.status)}
                      <span className="text-sm text-gray-500 dark:text-gray-400">
                        {formatDistanceToNow(new Date(session.createdAt))} ago
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
                      {session.prompt}
                    </p>
                    {session.metrics && (
                      <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500 dark:text-gray-400">
                        <span>{session.metrics.totalTasks} tasks</span>
                        <span>{session.metrics.completedTasks} completed</span>
                        {session.metrics.failedTasks > 0 && (
                          <span className="text-red-500">{session.metrics.failedTasks} failed</span>
                        )}
                      </div>
                    )}
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setLocation(`/session/${session.id}`)}
                    className="ml-4"
                  >
                    View <ArrowRight className="ml-1 h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
