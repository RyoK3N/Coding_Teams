import type { Express } from "express";
import { createServer, type Server } from "http";
import { WebSocketServer, WebSocket } from "ws";
import { storage } from "./storage";
import { insertSessionSchema, insertAgentEventSchema, type LogPayload, type ProgressPayload, type ArtifactPayload } from "@shared/schema";
import { z } from "zod";

export async function registerRoutes(app: Express): Promise<Server> {
  const httpServer = createServer(app);

  // REST API Routes
  
  // Create a new session
  app.post("/api/sessions", async (req, res) => {
    try {
      const sessionData = insertSessionSchema.parse(req.body);
      const session = await storage.createSession(sessionData);
      
      // Create default agents for the session
      const agents = [
        { sessionId: session.id, name: "Principal Engineer", role: "Architecture & Design" },
        { sessionId: session.id, name: "Python Specialist", role: "Core Implementation" },
        { sessionId: session.id, name: "Test Specialist", role: "Quality Assurance" },
      ];
      
      for (const agentData of agents) {
        await storage.createAgent(agentData);
      }
      
      res.json(session);
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ message: "Validation error", errors: error.errors });
      }
      res.status(500).json({ message: "Failed to create session" });
    }
  });

  // Get session by ID
  app.get("/api/sessions/:id", async (req, res) => {
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

  // Get all sessions
  app.get("/api/sessions", async (req, res) => {
    try {
      const sessions = await storage.getSessions();
      res.json(sessions);
    } catch (error) {
      res.status(500).json({ message: "Failed to get sessions" });
    }
  });

  // Get agents for a session
  app.get("/api/sessions/:id/agents", async (req, res) => {
    try {
      const agents = await storage.getAgentsBySession(req.params.id);
      res.json(agents);
    } catch (error) {
      res.status(500).json({ message: "Failed to get agents" });
    }
  });

  // Get events for a session
  app.get("/api/sessions/:id/events", async (req, res) => {
    try {
      const limit = parseInt(req.query.limit as string) || 1000;
      const offset = parseInt(req.query.offset as string) || 0;
      const events = await storage.getEventsBySession(req.params.id, limit, offset);
      res.json(events);
    } catch (error) {
      res.status(500).json({ message: "Failed to get events" });
    }
  });

  // Get artifacts for a session
  app.get("/api/sessions/:id/artifacts", async (req, res) => {
    try {
      const artifacts = await storage.getArtifactsBySession(req.params.id);
      res.json(artifacts);
    } catch (error) {
      res.status(500).json({ message: "Failed to get artifacts" });
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
