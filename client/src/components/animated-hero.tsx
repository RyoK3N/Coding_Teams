import { motion } from 'framer-motion';
import { Bot, Users, Code, Zap, Brain, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function AnimatedHero() {
  return (
    <div className="relative overflow-hidden bg-gradient-to-br from-primary/5 via-blue-50 to-purple-50 dark:from-gray-900 dark:via-blue-900/20 dark:to-purple-900/20 rounded-2xl p-8 mb-8">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          className="absolute -top-4 -right-4 w-72 h-72 bg-primary/10 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 4,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
        <motion.div
          className="absolute -bottom-8 -left-8 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl"
          animate={{
            scale: [1.2, 1, 1.2],
            opacity: [0.2, 0.4, 0.2],
          }}
          transition={{
            duration: 5,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      </div>

      <div className="relative z-10">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <motion.div
              className="flex items-center space-x-4 mb-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <div className="relative">
                <motion.div
                  className="w-16 h-16 bg-gradient-to-br from-primary to-blue-600 rounded-xl flex items-center justify-center"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Bot className="w-8 h-8 text-white" />
                </motion.div>
                <motion.div
                  className="absolute -top-1 -right-1 w-6 h-6 bg-green-400 rounded-full flex items-center justify-center"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  <div className="w-2 h-2 bg-white rounded-full" />
                </motion.div>
              </div>
              
              <div>
                <motion.h1
                  className="text-4xl font-bold text-gray-900 dark:text-white"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.6, delay: 0.1 }}
                >
                  Coding-Team
                </motion.h1>
                <motion.p
                  className="text-lg text-primary font-semibold"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.6, delay: 0.2 }}
                >
                  powered by Synexian
                </motion.p>
              </div>
            </motion.div>

            <motion.p
              className="text-xl text-gray-600 dark:text-gray-300 mb-6 max-w-2xl leading-relaxed"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              Transform your ideas into production-ready code with our{' '}
              <span className="text-primary font-semibold">AI-powered multi-agent development platform</span>.
              Watch as specialized AI agents collaborate to build, test, and deploy your software.
            </motion.p>

            <motion.div
              className="flex flex-wrap items-center gap-6 mb-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-300">
                <Users className="w-5 h-5 text-primary" />
                <span className="font-medium">8 AI Specialists</span>
              </div>
              <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-300">
                <Code className="w-5 h-5 text-green-500" />
                <span className="font-medium">Real-time Coding</span>
              </div>
              <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-300">
                <Zap className="w-5 h-5 text-yellow-500" />
                <span className="font-medium">Instant Deployment</span>
              </div>
            </motion.div>
          </div>

          {/* Animated statistics */}
          <motion.div
            className="flex flex-col space-y-4 ml-8"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            <div className="bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm rounded-lg p-4 text-center">
              <motion.div
                className="text-2xl font-bold text-primary"
                animate={{ scale: [1, 1.05, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <Brain className="w-6 h-6 mx-auto mb-1" />
                AI-First
              </motion.div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Architecture</div>
            </div>

            <div className="bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm rounded-lg p-4 text-center">
              <motion.div
                className="text-2xl font-bold text-green-600"
                animate={{ opacity: [0.7, 1, 0.7] }}
                transition={{ duration: 3, repeat: Infinity }}
              >
                <Sparkles className="w-6 h-6 mx-auto mb-1" />
                Smart
              </motion.div>
              <div className="text-sm text-gray-600 dark:text-gray-400">Collaboration</div>
            </div>
          </motion.div>
        </div>

        {/* Action buttons */}
        <motion.div
          className="flex items-center space-x-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <Button
            size="lg"
            className="bg-gradient-to-r from-primary to-blue-600 hover:from-primary/90 hover:to-blue-600/90 text-white shadow-lg hover:shadow-xl transition-all duration-300"
          >
            <motion.div
              className="flex items-center space-x-2"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Sparkles className="w-5 h-5" />
              <span>Start Building</span>
            </motion.div>
          </Button>
          
          <Button
            variant="outline"
            size="lg"
            className="border-2 border-primary/20 hover:border-primary/40 hover:bg-primary/5 transition-all duration-300"
          >
            <motion.div
              className="flex items-center space-x-2"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Code className="w-5 h-5" />
              <span>View Examples</span>
            </motion.div>
          </Button>
        </motion.div>
      </div>
    </div>
  );
}