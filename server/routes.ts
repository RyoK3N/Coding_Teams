import type { Express } from "express";
import { createServer, type Server } from "http";
import { WebSocketServer, WebSocket } from "ws";
import { storage } from "./storage";
import { pythonAgentService } from "./python-agent-service";
import { insertSessionSchema, insertAgentEventSchema, loginSchema, type LogPayload, type ProgressPayload, type ArtifactPayload } from "@shared/schema";
import { z } from "zod";
import { randomUUID } from "crypto";
import { authService } from "./auth";
import { requireAuth, type AuthRequest } from "./middleware/auth";

export async function registerRoutes(app: Express): Promise<Server> {
  const httpServer = createServer(app);

  // Initialize admin user on startup
  await authService.createAdminUser();

  // Auth Routes
  app.post("/api/auth/login", async (req, res) => {
    try {
      const credentials = loginSchema.parse(req.body);
      const result = await authService.login(credentials.username, credentials.password);
      
      if (!result) {
        return res.status(401).json({ message: "Invalid username or password" });
      }

      const { user, token } = result;
      res.json({
        token,
        user: {
          id: user.id,
          username: user.username,
          role: user.role,
          email: user.email,
        }
      });
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ message: "Validation error", errors: error.errors });
      }
      console.error('Login error:', error);
      res.status(500).json({ message: "Login failed" });
    }
  });

  app.get("/api/auth/me", requireAuth, async (req: AuthRequest, res) => {
    try {
      const user = await storage.getUser(req.user!.id);
      if (!user) {
        return res.status(404).json({ message: "User not found" });
      }
      
      res.json({
        id: user.id,
        username: user.username,
        role: user.role,
        email: user.email,
      });
    } catch (error) {
      console.error('Get user error:', error);
      res.status(500).json({ message: "Failed to get user" });
    }
  });

  // REST API Routes
  
  // Create a new session (protected)
  app.post("/api/sessions", requireAuth, async (req: AuthRequest, res) => {
    try {
      const sessionData = insertSessionSchema.parse(req.body);
      
      // Generate output directory path
      const outputDir = `temp/session_${Date.now()}_${randomUUID().slice(0, 8)}`;
      
      const session = await storage.createSession({
        ...sessionData,
        userId: req.user!.id,
        outputDir,
      });
      
      // Start the Python agent service
      try {
        await pythonAgentService.startCodingSession(session.id, sessionData.prompt, {
          includeTests: sessionData.includeTests,
          includeDocumentation: sessionData.includeDocumentation,
          timeout: 300 // 5 minutes default timeout
        });
      } catch (agentError) {
        console.error('Failed to start Python agents:', agentError);
        // Update session to failed status but still return the session
        await storage.updateSession(session.id, { status: 'failed' });
      }
      
      res.json(session);
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ message: "Validation error", errors: error.errors });
      }
      console.error('Session creation error:', error);
      res.status(500).json({ message: "Failed to create session" });
    }
  });

  // Get session by ID (protected)
  app.get("/api/sessions/:id", requireAuth, async (req: AuthRequest, res) => {
    try {
      const session = await storage.getSession(req.params.id);
      if (!session) {
        return res.status(404).json({ message: "Session not found" });
      }
      res.json(session);
    } catch (error) {
      res.status(500).json({ message: "Failed to get session" });
    }
  });

  // Get all sessions (protected)
  app.get("/api/sessions", requireAuth, async (req: AuthRequest, res) => {
    try {
      const sessions = await storage.getSessions();
      res.json(sessions);
    } catch (error) {
      res.status(500).json({ message: "Failed to get sessions" });
    }
  });

  // Get agents for a session (protected)
  app.get("/api/sessions/:id/agents", requireAuth, async (req: AuthRequest, res) => {
    try {
      const agents = await storage.getAgentsBySession(req.params.id);
      res.json(agents);
    } catch (error) {
      res.status(500).json({ message: "Failed to get agents" });
    }
  });

  // Get events for a session (protected)
  app.get("/api/sessions/:id/events", requireAuth, async (req: AuthRequest, res) => {
    try {
      const limit = parseInt(req.query.limit as string) || 1000;
      const offset = parseInt(req.query.offset as string) || 0;
      const events = await storage.getEventsBySession(req.params.id, limit, offset);
      res.json(events);
    } catch (error) {
      res.status(500).json({ message: "Failed to get events" });
    }
  });

  // Get artifacts for a session (protected)
  app.get("/api/sessions/:id/artifacts", requireAuth, async (req: AuthRequest, res) => {
    try {
      const artifacts = await storage.getArtifactsBySession(req.params.id);
      res.json(artifacts);
    } catch (error) {
      res.status(500).json({ message: "Failed to get artifacts" });
    }
  });

  // Get work packages for a session
  app.get("/api/sessions/:id/work-packages", async (req, res) => {
    try {
      const workPackages = await storage.getWorkPackagesBySession(req.params.id);
      res.json(workPackages);
    } catch (error) {
      res.status(500).json({ message: "Failed to get work packages" });
    }
  });

  // Stop a running session
  app.post("/api/sessions/:id/stop", async (req, res) => {
    try {
      await pythonAgentService.stopCodingSession(req.params.id);
      await storage.updateSession(req.params.id, { status: 'failed' });
      res.json({ message: "Session stopped" });
    } catch (error) {
      console.error('Failed to stop session:', error);
      res.status(500).json({ message: "Failed to stop session" });
    }
  });

  // Get session progress with real-time data
  app.get("/api/sessions/:id/progress", async (req, res) => {
    try {
      const progress = await pythonAgentService.getSessionProgress(req.params.id);
      res.json(progress);
    } catch (error) {
      console.error('Failed to get session progress:', error);
      res.status(500).json({ message: "Failed to get session progress" });
    }
  });

  // Download artifact
  app.get("/api/artifacts/:id/download", async (req, res) => {
    try {
      const artifact = await storage.getArtifact(req.params.id);
      if (!artifact) {
        return res.status(404).json({ message: "Artifact not found" });
      }
      
      res.setHeader('Content-Disposition', `attachment; filename="${artifact.filePath}"`);
      res.setHeader('Content-Type', 'application/octet-stream');
      res.send(artifact.content);
    } catch (error) {
      res.status(500).json({ message: "Failed to download artifact" });
    }
  });

  // Download all artifacts as zip
  app.get("/api/sessions/:id/download", async (req, res) => {
    try {
      const artifacts = await storage.getArtifactsBySession(req.params.id);
      if (artifacts.length === 0) {
        return res.status(404).json({ message: "No artifacts found" });
      }
      
      // Simple implementation - in production, use a proper zip library
      const zipContent = artifacts.map(artifact => 
        `// File: ${artifact.filePath}\n${artifact.content}\n\n`
      ).join("");
      
      res.setHeader('Content-Disposition', `attachment; filename="session-${req.params.id}-artifacts.txt"`);
      res.setHeader('Content-Type', 'application/octet-stream');
      res.send(zipContent);
    } catch (error) {
      res.status(500).json({ message: "Failed to download artifacts" });
    }
  });

  // WebSocket Setup
  const wss = new WebSocketServer({ server: httpServer, path: '/ws' });
  
  const sessionClients = new Map<string, Set<WebSocket>>();

  wss.on('connection', (ws, req) => {
    console.log('WebSocket client connected');
    
    ws.on('message', async (data) => {
      try {
        const message = JSON.parse(data.toString());
        
        if (message.type === 'subscribe' && message.sessionId) {
          // Subscribe client to session updates
          if (!sessionClients.has(message.sessionId)) {
            sessionClients.set(message.sessionId, new Set());
          }
          sessionClients.get(message.sessionId)!.add(ws);
          
          ws.send(JSON.stringify({
            type: 'subscribed',
            sessionId: message.sessionId
          }));
        }
        
        if (message.type === 'agent_event') {
          // Handle incoming agent events and broadcast to subscribers
          const event = await storage.createAgentEvent(message.event);
          
          // Broadcast to all clients subscribed to this session
          const clients = sessionClients.get(message.event.sessionId);
          if (clients) {
            const eventMessage = JSON.stringify({
              type: 'agent_event',
              event
            });
            
            clients.forEach(client => {
              if (client.readyState === WebSocket.OPEN) {
                client.send(eventMessage);
              }
            });
          }
          
          // Update agent status if this is a progress event
          if (message.event.type === 'PROGRESS' && message.event.agentId) {
            const payload = message.event.payload as ProgressPayload;
            await storage.updateAgent(message.event.agentId, {
              progress: payload.percent,
              status: payload.percent === 100 ? 'succeeded' : 'running'
            });
          }
        }
        
      } catch (error) {
        console.error('WebSocket message error:', error);
      }
    });

    ws.on('close', () => {
      // Remove client from all session subscriptions
      sessionClients.forEach((clients, sessionId) => {
        clients.delete(ws);
        if (clients.size === 0) {
          sessionClients.delete(sessionId);
        }
      });
    });
  });

  return httpServer;
}
