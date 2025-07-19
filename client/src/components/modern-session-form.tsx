import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage, FormDescription } from '@/components/ui/form';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  Bot, 
  Sparkles, 
  FileText, 
  TestTube, 
  Clock, 
  Users, 
  Zap,
  Brain,
  Code,
  Database,
  Shield,
  Server,
  Palette,
  Loader2
} from 'lucide-react';
import { z } from 'zod';

interface ModernSessionFormProps {
  onSubmit: (data: {
    prompt: string;
    includeTests: boolean;
    includeDocumentation: boolean;
  }) => Promise<void>;
  isLoading?: boolean;
}

const formSchema = z.object({
  prompt: z.string().min(10, "Prompt must be at least 10 characters"),
  includeTests: z.boolean().default(false),
  includeDocumentation: z.boolean().default(false),
});

const agentSpecs = [
  { name: 'Principal Engineer', icon: Brain, description: 'Architecture & Problem Analysis', color: 'bg-purple-100 text-purple-700' },
  { name: 'Backend Specialist', icon: Server, description: 'Core Implementation', color: 'bg-blue-100 text-blue-700' },
  { name: 'Frontend Specialist', icon: Palette, description: 'UI/UX Development', color: 'bg-pink-100 text-pink-700' },
  { name: 'Database Specialist', icon: Database, description: 'Data Management', color: 'bg-green-100 text-green-700' },
  { name: 'API Specialist', icon: Zap, description: 'Service Integration', color: 'bg-yellow-100 text-yellow-700' },
  { name: 'Test Specialist', icon: TestTube, description: 'Quality Assurance', color: 'bg-red-100 text-red-700' },
  { name: 'DevOps Specialist', icon: Server, description: 'Deployment & Infrastructure', color: 'bg-indigo-100 text-indigo-700' },
  { name: 'Security Specialist', icon: Shield, description: 'Security & Compliance', color: 'bg-orange-100 text-orange-700' }
];

const examplePrompts = [
  "Create a REST API for managing a book library with authentication and CRUD operations",
  "Build a real-time chat application with WebSocket support and user presence",
  "Develop a task management system with drag-and-drop functionality and team collaboration",
  "Create an e-commerce platform with payment integration and inventory management"
];

export function ModernSessionForm({ onSubmit, isLoading = false }: ModernSessionFormProps) {
  const [selectedExample, setSelectedExample] = useState<string>('');

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      prompt: '',
      includeTests: true,
      includeDocumentation: true,
    },
  });

  const handleSubmit = async (data: z.infer<typeof formSchema>) => {
    await onSubmit(data);
  };

  const insertExample = (example: string) => {
    form.setValue('prompt', example);
    setSelectedExample(example);
  };

  return (
    <Card className="w-full bg-gradient-to-br from-white to-gray-50 dark:from-gray-900 dark:to-gray-800 border-2 border-primary/10 shadow-xl">
      <CardHeader className="pb-4">
        <motion.div
          className="flex items-center space-x-3"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="relative">
            <div className="w-12 h-12 bg-gradient-to-br from-primary to-blue-600 rounded-xl flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <motion.div
              className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full flex items-center justify-center"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <div className="w-2 h-2 bg-white rounded-full" />
            </motion.div>
          </div>
          
          <div>
            <CardTitle className="text-2xl font-bold">Create New Project</CardTitle>
            <p className="text-muted-foreground">Let our AI agents bring your ideas to life</p>
          </div>
        </motion.div>
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Agent Team Preview */}
        <motion.div
          className="space-y-3"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <div className="flex items-center space-x-2 mb-3">
            <Users className="w-4 h-4 text-primary" />
            <h3 className="font-semibold text-sm">Your AI Development Team</h3>
            <Badge className="bg-primary/10 text-primary">8 Specialists</Badge>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {agentSpecs.map((agent, index) => (
              <motion.div
                key={agent.name}
                className={`p-3 rounded-lg border transition-all duration-200 hover:shadow-md ${agent.color.replace('text-', 'border-').replace('-700', '-200')}`}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                whileHover={{ scale: 1.02 }}
              >
                <div className="flex flex-col items-center text-center space-y-1">
                  <agent.icon className={`w-5 h-5 ${agent.color.split(' ')[1]}`} />
                  <div className="text-xs font-medium">{agent.name.split(' ')[0]}</div>
                  <div className="text-xs text-muted-foreground hidden md:block">
                    {agent.description}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        <Separator />

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            {/* Example prompts */}
            <motion.div
              className="space-y-3"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <div className="flex items-center space-x-2">
                <Code className="w-4 h-4 text-primary" />
                <h3 className="font-semibold text-sm">Try an Example</h3>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {examplePrompts.map((example, index) => (
                  <motion.button
                    key={index}
                    type="button"
                    className={`p-3 text-left text-xs border rounded-lg transition-all duration-200 hover:shadow-md hover:border-primary/40 ${
                      selectedExample === example 
                        ? 'border-primary bg-primary/5 text-primary' 
                        : 'border-gray-200 dark:border-gray-700 text-muted-foreground hover:text-foreground'
                    }`}
                    onClick={() => insertExample(example)}
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.99 }}
                  >
                    {example}
                  </motion.button>
                ))}
              </div>
            </motion.div>

            <Separator />

            {/* Main prompt field */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
            >
              <FormField
                control={form.control}
                name="prompt"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="flex items-center space-x-2">
                      <Bot className="w-4 h-4" />
                      <span>Project Description</span>
                    </FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Describe what you want to build. Be as specific as possible about features, technology preferences, and requirements..."
                        className="min-h-[120px] resize-none border-2 focus:border-primary/50 transition-colors"
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      The more detailed your description, the better our AI agents can understand and implement your vision.
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </motion.div>

            {/* Options */}
            <motion.div
              className="grid grid-cols-1 md:grid-cols-2 gap-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
            >
              <FormField
                control={form.control}
                name="includeTests"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4 space-y-0">
                    <div className="space-y-0.5">
                      <FormLabel className="flex items-center space-x-2">
                        <TestTube className="w-4 h-4 text-green-600" />
                        <span>Include Tests</span>
                      </FormLabel>
                      <FormDescription className="text-xs">
                        Generate comprehensive test suites
                      </FormDescription>
                    </div>
                    <FormControl>
                      <Switch
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="includeDocumentation"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-4 space-y-0">
                    <div className="space-y-0.5">
                      <FormLabel className="flex items-center space-x-2">
                        <FileText className="w-4 h-4 text-blue-600" />
                        <span>Include Documentation</span>
                      </FormLabel>
                      <FormDescription className="text-xs">
                        Generate README and API docs
                      </FormDescription>
                    </div>
                    <FormControl>
                      <Switch
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />
            </motion.div>

            {/* Submit button */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.5 }}
            >
              <Button 
                type="submit" 
                size="lg"
                disabled={isLoading || !form.watch('prompt')}
                className="w-full bg-gradient-to-r from-primary to-blue-600 hover:from-primary/90 hover:to-blue-600/90 text-white shadow-lg hover:shadow-xl transition-all duration-300 h-12"
              >
                {isLoading ? (
                  <motion.div
                    className="flex items-center space-x-2"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                  >
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Starting AI Team...</span>
                  </motion.div>
                ) : (
                  <motion.div
                    className="flex items-center space-x-2"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Sparkles className="w-5 h-5" />
                    <span>Start Building</span>
                    <Clock className="w-4 h-4 ml-2 opacity-70" />
                    <span className="text-sm opacity-70">~2-5 min</span>
                  </motion.div>
                )}
              </Button>
              
              {form.watch('prompt') && (
                <motion.p
                  className="text-xs text-muted-foreground text-center mt-2"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.2 }}
                >
                  Our AI agents will analyze your requirements and start coding immediately
                </motion.p>
              )}
            </motion.div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}