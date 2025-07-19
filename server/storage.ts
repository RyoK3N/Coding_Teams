import { 
  users, sessions, agents, agentEvents, artifacts,
  type User, type InsertUser, type Session, type InsertSession,
  type Agent, type InsertAgent, type AgentEvent, type InsertAgentEvent,
  type Artifact, type InsertArtifact
} from "@shared/schema";

export interface IStorage {
  // User operations
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  
  // Session operations
  getSession(id: string): Promise<Session | undefined>;
  createSession(session: InsertSession): Promise<Session>;
  updateSession(id: string, updates: Partial<Session>): Promise<Session | undefined>;
  getSessions(): Promise<Session[]>;
  
  // Agent operations
  getAgentsBySession(sessionId: string): Promise<Agent[]>;
  createAgent(agent: InsertAgent): Promise<Agent>;
  updateAgent(id: string, updates: Partial<Agent>): Promise<Agent | undefined>;
  
  // Event operations
  createAgentEvent(event: InsertAgentEvent): Promise<AgentEvent>;
  getEventsBySession(sessionId: string, limit?: number, offset?: number): Promise<AgentEvent[]>;
  
  // Artifact operations
  getArtifactsBySession(sessionId: string): Promise<Artifact[]>;
  createArtifact(artifact: InsertArtifact): Promise<Artifact>;
  getArtifact(id: string): Promise<Artifact | undefined>;
}

export class MemStorage implements IStorage {
  private users: Map<number, User> = new Map();
  private sessions: Map<string, Session> = new Map();
  private agents: Map<string, Agent> = new Map();
  private agentEvents: Map<string, AgentEvent> = new Map();
  private artifacts: Map<string, Artifact> = new Map();
  private currentUserId = 1;
  private eventSequence = 1;

  // User operations
  async getUser(id: number): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(user => user.username === username);
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = this.currentUserId++;
    const user: User = { ...insertUser, id };
    this.users.set(id, user);
    return user;
  }

  // Session operations
  async getSession(id: string): Promise<Session | undefined> {
    return this.sessions.get(id);
  }

  async createSession(insertSession: InsertSession): Promise<Session> {
    const id = crypto.randomUUID();
    const now = new Date();
    const session: Session = {
      ...insertSession,
      id,
      status: "pending",
      createdAt: now,
      updatedAt: now,
      metrics: {
        totalTasks: 0,
        activeTasks: 0,
        completedTasks: 0,
        failedTasks: 0,
      },
    };
    this.sessions.set(id, session);
    return session;
  }

  async updateSession(id: string, updates: Partial<Session>): Promise<Session | undefined> {
    const session = this.sessions.get(id);
    if (!session) return undefined;
    
    const updatedSession = { ...session, ...updates, updatedAt: new Date() };
    this.sessions.set(id, updatedSession);
    return updatedSession;
  }

  async getSessions(): Promise<Session[]> {
    return Array.from(this.sessions.values()).sort((a, b) => 
      new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
    );
  }

  // Agent operations
  async getAgentsBySession(sessionId: string): Promise<Agent[]> {
    return Array.from(this.agents.values()).filter(agent => agent.sessionId === sessionId);
  }

  async createAgent(insertAgent: InsertAgent): Promise<Agent> {
    const id = crypto.randomUUID();
    const now = new Date();
    const agent: Agent = {
      ...insertAgent,
      id,
      status: "idle",
      progress: 0,
      createdAt: now,
      updatedAt: now,
    };
    this.agents.set(id, agent);
    return agent;
  }

  async updateAgent(id: string, updates: Partial<Agent>): Promise<Agent | undefined> {
    const agent = this.agents.get(id);
    if (!agent) return undefined;
    
    const updatedAgent = { ...agent, ...updates, updatedAt: new Date() };
    this.agents.set(id, updatedAgent);
    return updatedAgent;
  }

  // Event operations
  async createAgentEvent(insertEvent: InsertAgentEvent): Promise<AgentEvent> {
    const id = crypto.randomUUID();
    const event: AgentEvent = {
      ...insertEvent,
      id,
      timestamp: new Date(),
      sequence: this.eventSequence++,
    };
    this.agentEvents.set(id, event);
    return event;
  }

  async getEventsBySession(sessionId: string, limit = 1000, offset = 0): Promise<AgentEvent[]> {
    return Array.from(this.agentEvents.values())
      .filter(event => event.sessionId === sessionId)
      .sort((a, b) => a.sequence - b.sequence)
      .slice(offset, offset + limit);
  }

  // Artifact operations
  async getArtifactsBySession(sessionId: string): Promise<Artifact[]> {
    return Array.from(this.artifacts.values()).filter(artifact => artifact.sessionId === sessionId);
  }

  async createArtifact(insertArtifact: InsertArtifact): Promise<Artifact> {
    const id = crypto.randomUUID();
    const artifact: Artifact = {
      ...insertArtifact,
      id,
      createdAt: new Date(),
    };
    this.artifacts.set(id, artifact);
    return artifact;
  }

  async getArtifact(id: string): Promise<Artifact | undefined> {
    return this.artifacts.get(id);
  }
}

export const storage = new MemStorage();
