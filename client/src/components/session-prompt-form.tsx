import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Play, Wand2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

const formSchema = z.object({
  prompt: z.string()
    .min(20, 'Prompt must be at least 20 characters')
    .max(2000, 'Prompt must not exceed 2000 characters'),
  includeTests: z.boolean().default(false),
  includeDocumentation: z.boolean().default(false),
});

type FormData = z.infer<typeof formSchema>;

interface SessionPromptFormProps {
  onSubmit: (data: FormData) => Promise<void>;
  isLoading?: boolean;
}

export function SessionPromptForm({ onSubmit, isLoading }: SessionPromptFormProps) {
  const [charCount, setCharCount] = useState(0);
  const { toast } = useToast();

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      prompt: '',
      includeTests: false,
      includeDocumentation: false,
    },
  });

  const handleSubmit = async (data: FormData) => {
    try {
      await onSubmit(data);
      form.reset();
      setCharCount(0);
      toast({
        title: "Session Created",
        description: "Your software generation session has been started.",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create session. Please try again.",
        variant: "destructive",
      });
    }
  };

  const promptValue = form.watch('prompt');

  return (
    <Card className="bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
      <CardHeader>
        <CardTitle className="flex items-center text-gray-900 dark:text-white">
          <Wand2 className="mr-2 h-5 w-5 text-primary" />
          Generate Software
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="prompt"
              render={({ field }) => (
                <FormItem>
                  <FormLabel className="text-gray-700 dark:text-gray-300">
                    Describe the software you want to create
                  </FormLabel>
                  <FormControl>
                    <Textarea
                      {...field}
                      placeholder="e.g., Create a simple password generator CLI tool with customizable length and character sets..."
                      className="h-32 resize-none bg-white dark:bg-gray-700 border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400"
                      onChange={(e) => {
                        field.onChange(e);
                        setCharCount(e.target.value.length);
                      }}
                    />
                  </FormControl>
                  <div className="flex justify-between text-sm">
                    <span className={`${charCount < 20 ? 'text-red-500' : 'text-gray-500 dark:text-gray-400'}`}>
                      Minimum 20 characters required
                    </span>
                    <span className="text-gray-500 dark:text-gray-400">
                      {charCount} / 2000
                    </span>
                  </div>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <FormField
                  control={form.control}
                  name="includeTests"
                  render={({ field }) => (
                    <FormItem className="flex items-center space-x-2">
                      <FormControl>
                        <Checkbox
                          checked={field.value}
                          onCheckedChange={field.onChange}
                          className="border-gray-300 dark:border-gray-600"
                        />
                      </FormControl>
                      <FormLabel className="text-sm text-gray-600 dark:text-gray-400 font-normal">
                        Include tests
                      </FormLabel>
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="includeDocumentation"
                  render={({ field }) => (
                    <FormItem className="flex items-center space-x-2">
                      <FormControl>
                        <Checkbox
                          checked={field.value}
                          onCheckedChange={field.onChange}
                          className="border-gray-300 dark:border-gray-600"
                        />
                      </FormControl>
                      <FormLabel className="text-sm text-gray-600 dark:text-gray-400 font-normal">
                        Include documentation
                      </FormLabel>
                    </FormItem>
                  )}
                />
              </div>

              <Button
                type="submit"
                disabled={isLoading || !form.formState.isValid}
                className="bg-primary hover:bg-primary/90 text-white"
              >
                <Play className="mr-2 h-4 w-4" />
                Generate Code
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
