import { pgTable, text, serial, integer, boolean, timestamp, jsonb, uuid } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
});

export const sessions = pgTable("sessions", {
  id: uuid("id").primaryKey().defaultRandom(),
  prompt: text("prompt").notNull(),
  status: text("status").notNull().default("pending"), // pending, running, completed, failed
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
  includeTests: boolean("include_tests").default(false),
  includeDocumentation: boolean("include_documentation").default(false),
  metrics: jsonb("metrics").$type<{
    totalTasks: number;
    activeTasks: number;
    completedTasks: number;
    failedTasks: number;
    avgCompletionTime?: number;
    successRate?: number;
  }>(),
});

export const agents = pgTable("agents", {
  id: uuid("id").primaryKey().defaultRandom(),
  sessionId: uuid("session_id").references(() => sessions.id).notNull(),
  name: text("name").notNull(),
  role: text("role").notNull(),
  status: text("status").notNull().default("idle"), // idle, running, succeeded, failed
  progress: integer("progress").default(0),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const agentEvents = pgTable("agent_events", {
  id: uuid("id").primaryKey().defaultRandom(),
  sessionId: uuid("session_id").references(() => sessions.id).notNull(),
  agentId: uuid("agent_id").references(() => agents.id),
  type: text("type").notNull(), // TASK_CREATED, TASK_STARTED, PROGRESS, LOG, ARTIFACT, STEP_SUCCESS, STEP_ERROR, SESSION_COMPLETE
  timestamp: timestamp("timestamp").defaultNow().notNull(),
  payload: jsonb("payload").notNull(),
  sequence: integer("sequence").notNull(),
});

export const artifacts = pgTable("artifacts", {
  id: uuid("id").primaryKey().defaultRandom(),
  sessionId: uuid("session_id").references(() => sessions.id).notNull(),
  agentId: uuid("agent_id").references(() => agents.id),
  filePath: text("file_path").notNull(),
  content: text("content").notNull(),
  size: integer("size").notNull(),
  language: text("language"),
  checksum: text("checksum"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

// Zod schemas
export const insertSessionSchema = createInsertSchema(sessions).pick({
  prompt: true,
  includeTests: true,
  includeDocumentation: true,
}).extend({
  prompt: z.string().min(20, "Prompt must be at least 20 characters").max(2000, "Prompt must not exceed 2000 characters"),
});

export const insertAgentSchema = createInsertSchema(agents).pick({
  sessionId: true,
  name: true,
  role: true,
});

export const insertAgentEventSchema = createInsertSchema(agentEvents).pick({
  sessionId: true,
  agentId: true,
  type: true,
  payload: true,
  sequence: true,
});

export const insertArtifactSchema = createInsertSchema(artifacts).pick({
  sessionId: true,
  agentId: true,
  filePath: true,
  content: true,
  size: true,
  language: true,
  checksum: true,
});

// Types
export type User = typeof users.$inferSelect;
export type InsertUser = z.infer<typeof insertUserSchema>;
export type Session = typeof sessions.$inferSelect;
export type InsertSession = z.infer<typeof insertSessionSchema>;
export type Agent = typeof agents.$inferSelect;
export type InsertAgent = z.infer<typeof insertAgentSchema>;
export type AgentEvent = typeof agentEvents.$inferSelect;
export type InsertAgentEvent = z.infer<typeof insertAgentEventSchema>;
export type Artifact = typeof artifacts.$inferSelect;
export type InsertArtifact = z.infer<typeof insertArtifactSchema>;

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
});

// Event payload types
export interface LogPayload {
  level: "DEBUG" | "INFO" | "WARN" | "ERROR";
  message: string;
  sequence: number;
}

export interface ProgressPayload {
  percent: number;
  message?: string;
}

export interface ArtifactPayload {
  file_path: string;
  size: number;
  checksum: string;
  language?: string;
}

export interface TaskPayload {
  taskId: string;
  description: string;
}
