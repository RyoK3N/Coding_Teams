import { exec, spawn } from 'child_process';
import { promisify } from 'util';
import { mkdir, rmdir, readdir, readFile, stat } from 'fs/promises';
import { join, resolve, relative } from 'path';
import { randomUUID } from 'crypto';
import { storage } from './storage';
import type { Session, Agent, WorkPackage } from '@shared/schema';

const execAsync = promisify(exec);

export class PythonAgentService {
  private activeProcesses = new Map<string, any>();
  private tempBaseDir = resolve('./temp');

  constructor() {
    this.initTempDirectory();
  }

  private async initTempDirectory() {
    try {
      await mkdir(this.tempBaseDir, { recursive: true });
    } catch (error) {
      console.error('Failed to create temp directory:', error);
    }
  }

  async startCodingSession(sessionId: string, prompt: string, options: {
    includeTests?: boolean;
    includeDocumentation?: boolean;
    timeout?: number;
  } = {}): Promise<string> {
    const outputDir = join(this.tempBaseDir, `session_${sessionId}_${Date.now()}`);
    
    try {
      await mkdir(outputDir, { recursive: true });
      
      // Update session with output directory
      await storage.updateSession(sessionId, { 
        outputDir,
        status: 'analyzing' as const
      });

      // Create default agents (matching the Python system structure)
      const agents = await this.createDefaultAgents(sessionId);
      
      // Construct Python command
      const pythonCmd = [
        'python',
        'main.py',
        'solve',
        `"${prompt}"`,
        '--timeout', (options.timeout || 300).toString(),
        '--output-dir', outputDir
      ];

      if (options.includeTests) pythonCmd.push('--include-tests');
      if (options.includeDocumentation) pythonCmd.push('--include-docs');

      // Start the Python process
      const process = spawn(pythonCmd[0], pythonCmd.slice(1), {
        cwd: process.env.CODING_TEAMS_PATH || './coding_teams',
        stdio: ['pipe', 'pipe', 'pipe']
      });

      this.activeProcesses.set(sessionId, process);

      // Handle real-time output
      this.handlePythonProcessOutput(sessionId, process, agents);

      // Handle process completion
      process.on('close', async (code) => {
        this.activeProcesses.delete(sessionId);
        await this.handleProcessCompletion(sessionId, code, outputDir);
      });

      return outputDir;
    } catch (error) {
      console.error('Failed to start coding session:', error);
      await storage.updateSession(sessionId, { status: 'failed' as const });
      throw error;
    }
  }

  private async createDefaultAgents(sessionId: string): Promise<Agent[]> {
    const agentConfigs = [
      { name: 'Principle Software Engineer', role: 'Architecture & Problem Analysis', type: 'principle' as const },
      { name: 'Backend Specialist', role: 'Core Implementation', type: 'specialist' as const },
      { name: 'Frontend Specialist', role: 'UI/UX Development', type: 'specialist' as const },
      { name: 'Database Specialist', role: 'Data Management', type: 'specialist' as const },
      { name: 'API Specialist', role: 'Service Integration', type: 'specialist' as const },
      { name: 'Test Specialist', role: 'Quality Assurance', type: 'specialist' as const },
      { name: 'DevOps Specialist', role: 'Deployment & Infrastructure', type: 'specialist' as const },
      { name: 'Security Specialist', role: 'Security & Compliance', type: 'specialist' as const }
    ];

    const agents: Agent[] = [];
    for (const config of agentConfigs) {
      const agent = await storage.createAgent({
        sessionId,
        ...config
      });
      agents.push(agent);
    }

    return agents;
  }

  private handlePythonProcessOutput(sessionId: string, process: any, agents: Agent[]) {
    let logBuffer = '';
    
    // Parse stdout for structured logs and progress
    process.stdout.on('data', async (data: Buffer) => {
      const output = data.toString();
      logBuffer += output;
      
      const lines = logBuffer.split('\n');
      logBuffer = lines.pop() || ''; // Keep incomplete line for next iteration

      for (const line of lines) {
        await this.parsePythonLog(sessionId, line, agents);
      }
    });

    // Handle errors
    process.stderr.on('data', async (data: Buffer) => {
      const error = data.toString();
      await this.createLogEvent(sessionId, 'ERROR', error);
    });
  }

  private async parsePythonLog(sessionId: string, line: string, agents: Agent[]) {
    try {
      // Parse different log patterns from the Python system
      
      // Progress updates: "2025-07-19 15:54:40,773 - progress_tracker - INFO - Completed task: ..."
      const progressMatch = line.match(/(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\w+) - (\w+) - (.+)/);
      if (progressMatch) {
        const [, timestamp, component, level, message] = progressMatch;
        await this.createLogEvent(sessionId, level, message, component);
        
        // Update agent status based on log content
        if (message.includes('Started task:')) {
          const agentName = this.extractAgentName(message);
          const agent = agents.find(a => a.name.toLowerCase().includes(agentName?.toLowerCase() || ''));
          if (agent) {
            await storage.updateAgent(agent.id, { 
              status: 'running', 
              currentStep: this.extractStepName(message) 
            });
          }
        }
        
        if (message.includes('Completed task:')) {
          const agentName = this.extractAgentName(message);
          const agent = agents.find(a => a.name.toLowerCase().includes(agentName?.toLowerCase() || ''));
          if (agent) {
            await storage.updateAgent(agent.id, { 
              status: 'succeeded',
              progress: 100,
              completionTime: Date.now()
            });
          }
        }
      }

      // File creation: "File written: src/main.py"
      if (line.includes('File written:')) {
        const filePath = line.split('File written:')[1]?.trim();
        if (filePath) {
          await this.handleFileCreation(sessionId, filePath, agents);
        }
      }

      // Work package completion
      if (line.includes('Work package') && line.includes('completed')) {
        await this.handleWorkPackageCompletion(sessionId, line);
      }

    } catch (error) {
      console.error('Error parsing Python log:', error);
    }
  }

  private async createLogEvent(sessionId: string, level: string, message: string, component?: string) {
    const sequence = Date.now();
    
    await storage.createAgentEvent({
      sessionId,
      type: 'LOG',
      payload: { level, message, component },
      sequence
    });
  }

  private extractAgentName(message: string): string | null {
    const patterns = [
      /(\w+_specialist)/i,
      /Principle Software Engineer/i,
      /Backend Specialist/i,
      /Frontend Specialist/i,
      /Test Specialist/i
    ];
    
    for (const pattern of patterns) {
      const match = message.match(pattern);
      if (match) return match[1] || match[0];
    }
    
    return null;
  }

  private extractStepName(message: string): string | null {
    const stepMatch = message.match(/task: (.+)/);
    return stepMatch ? stepMatch[1] : null;
  }

  private async handleFileCreation(sessionId: string, filePath: string, agents: Agent[]) {
    try {
      const session = await storage.getSession(sessionId);
      if (!session) return;

      const fullPath = join(session.outputDir, filePath);
      const stats = await stat(fullPath);
      const content = await readFile(fullPath, 'utf-8');
      
      // Determine file language
      const language = this.getLanguageFromPath(filePath);
      
      // Create artifact
      await storage.createArtifact({
        sessionId,
        filePath,
        content,
        size: stats.size,
        language,
        checksum: this.generateChecksum(content)
      });

      // Update session file count
      await storage.updateSession(sessionId, {
        filesCreated: (session.filesCreated || 0) + 1
      });

    } catch (error) {
      console.error('Error handling file creation:', error);
    }
  }

  private async handleWorkPackageCompletion(sessionId: string, logLine: string) {
    // Extract work package info and update status
    // This would parse work package completion from logs
  }

  private async handleProcessCompletion(sessionId: string, exitCode: number, outputDir: string) {
    try {
      const finalStatus = exitCode === 0 ? 'completed' : 'failed';
      
      // Scan output directory for any remaining files
      await this.scanOutputDirectory(sessionId, outputDir);
      
      // Update session final status
      const session = await storage.getSession(sessionId);
      if (session) {
        await storage.updateSession(sessionId, {
          status: finalStatus,
          duration: Math.floor((Date.now() - new Date(session.createdAt).getTime()) / 1000)
        });
      }

      // Clean up old temp directories (keep last 10 sessions)
      await this.cleanupTempDirectories();

    } catch (error) {
      console.error('Error handling process completion:', error);
    }
  }

  private async scanOutputDirectory(sessionId: string, outputDir: string) {
    try {
      const files = await this.getAllFiles(outputDir);
      
      for (const filePath of files) {
        const relativePath = relative(outputDir, filePath);
        const stats = await stat(filePath);
        const content = await readFile(filePath, 'utf-8');
        
        // Check if artifact already exists
        const artifacts = await storage.getArtifactsBySession(sessionId);
        const exists = artifacts.some(a => a.filePath === relativePath);
        
        if (!exists) {
          await storage.createArtifact({
            sessionId,
            filePath: relativePath,
            content,
            size: stats.size,
            language: this.getLanguageFromPath(relativePath),
            checksum: this.generateChecksum(content)
          });
        }
      }
    } catch (error) {
      console.error('Error scanning output directory:', error);
    }
  }

  private async getAllFiles(dir: string): Promise<string[]> {
    const files: string[] = [];
    const entries = await readdir(dir, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = join(dir, entry.name);
      if (entry.isDirectory()) {
        files.push(...await this.getAllFiles(fullPath));
      } else {
        files.push(fullPath);
      }
    }
    
    return files;
  }

  private getLanguageFromPath(filePath: string): string {
    const ext = filePath.split('.').pop()?.toLowerCase();
    const languageMap: Record<string, string> = {
      'py': 'python',
      'js': 'javascript',
      'ts': 'typescript',
      'jsx': 'jsx',
      'tsx': 'tsx',
      'html': 'html',
      'css': 'css',
      'json': 'json',
      'md': 'markdown',
      'yml': 'yaml',
      'yaml': 'yaml',
      'sql': 'sql',
      'sh': 'bash',
      'dockerfile': 'docker'
    };
    
    return languageMap[ext || ''] || 'text';
  }

  private generateChecksum(content: string): string {
    // Simple hash for content verification
    let hash = 0;
    for (let i = 0; i < content.length; i++) {
      const char = content.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }
    return hash.toString(16);
  }

  private async cleanupTempDirectories() {
    try {
      const entries = await readdir(this.tempBaseDir, { withFileTypes: true });
      const sessionDirs = entries
        .filter(entry => entry.isDirectory() && entry.name.startsWith('session_'))
        .sort((a, b) => b.name.localeCompare(a.name))
        .slice(10); // Keep only latest 10 sessions
      
      for (const dir of sessionDirs) {
        await rmdir(join(this.tempBaseDir, dir.name), { recursive: true });
      }
    } catch (error) {
      console.error('Error cleaning up temp directories:', error);
    }
  }

  async stopCodingSession(sessionId: string): Promise<void> {
    const process = this.activeProcesses.get(sessionId);
    if (process) {
      process.kill('SIGTERM');
      this.activeProcesses.delete(sessionId);
      
      // Update session status
      await storage.updateSession(sessionId, { status: 'failed' });
    }
  }

  async getSessionProgress(sessionId: string) {
    const session = await storage.getSession(sessionId);
    const agents = await storage.getAgentsBySession(sessionId);
    const events = await storage.getEventsBySession(sessionId, 100);
    
    return {
      session,
      agents,
      events,
      isActive: this.activeProcesses.has(sessionId)
    };
  }
}

export const pythonAgentService = new PythonAgentService();