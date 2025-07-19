import { useState } from 'react';
import { useLocation } from 'wouter';
import { ModernSessionForm } from '@/components/modern-session-form';
import { AnimatedHero } from '@/components/animated-hero';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useSession, useSessions } from '@/hooks/use-session';
import { formatDistanceToNow } from 'date-fns';
import { motion } from 'framer-motion';
import { ArrowRight, Clock, CheckCircle, XCircle, Play, Bot, Users, FileText } from 'lucide-react';

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
      {/* Hero Section */}
      <AnimatedHero />
      
      {/* Prompt Form */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
      >
        <ModernSessionForm 
          onSubmit={handleCreateSession}
          isLoading={isCreatingSession}
        />
      </motion.div>

      {/* Recent Sessions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
      >
        <Card className="bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-gray-900 dark:text-white flex items-center space-x-2">
                <Bot className="w-5 h-5 text-primary" />
                <span>Recent Sessions</span>
              </CardTitle>
              {sessionsQuery.data?.length > 0 && (
                <Badge variant="secondary" className="text-xs">
                  {sessionsQuery.data.length} total
                </Badge>
              )}
            </div>
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
              {sessionsQuery.data?.map((session: any, index: number) => (
                <motion.div
                  key={session.id}
                  className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors cursor-pointer"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  whileHover={{ scale: 1.01 }}
                  onClick={() => setLocation(`/session/${session.id}`)}
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
                    <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500 dark:text-gray-400">
                      <div className="flex items-center space-x-1">
                        <Users className="w-3 h-3" />
                        <span>{session.agentCount || 8} agents</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <FileText className="w-3 h-3" />
                        <span>{session.filesCreated || 0} files</span>
                      </div>
                      {session.duration && (
                        <div className="flex items-center space-x-1">
                          <Clock className="w-3 h-3" />
                          <span>{Math.round(session.duration)}s</span>
                        </div>
                      )}
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="ml-4 hover:bg-primary/10"
                    onClick={(e) => {
                      e.stopPropagation();
                      setLocation(`/session/${session.id}`);
                    }}
                  >
                    View <ArrowRight className="ml-1 h-4 w-4" />
                  </Button>
                </motion.div>
              ))}
            </div>
          )}
        </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}
