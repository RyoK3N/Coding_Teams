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
  status: text("status").notNull().default("pending"), // pending, analyzing, running, completed, failed
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
  includeTests: boolean("include_tests").default(false),
  includeDocumentation: boolean("include_documentation").default(false),
  outputDir: text("output_dir").notNull(), // Temp directory for generated code
  duration: integer("duration"), // Total execution time in seconds
  filesCreated: integer("files_created").default(0),
  workPackagesTotal: integer("work_packages_total").default(0),
  workPackagesCompleted: integer("work_packages_completed").default(0),
  metrics: jsonb("metrics").$type<{
    totalTasks: number;
    activeTasks: number;
    completedTasks: number;
    failedTasks: number;
    avgCompletionTime?: number;
    successRate?: number;
    accuracyRate?: number;
  }>(),
});

export const agents = pgTable("agents", {
  id: uuid("id").primaryKey().defaultRandom(),
  sessionId: uuid("session_id").references(() => sessions.id).notNull(),
  name: text("name").notNull(),
  role: text("role").notNull(),
  type: text("type").notNull().default("specialist"), // principle, specialist
  status: text("status").notNull().default("idle"), // idle, analyzing, running, succeeded, failed
  progress: integer("progress").default(0),
  currentStep: text("current_step"),
  workPackageId: text("work_package_id"),
  filesCreated: integer("files_created").default(0),
  completionTime: integer("completion_time"), // Time in seconds
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const workPackages = pgTable("work_packages", {
  id: text("id").primaryKey(), // WP001, WP002, etc.
  sessionId: uuid("session_id").references(() => sessions.id).notNull(),
  title: text("title").notNull(),
  description: text("description").notNull(),
  assignedAgentId: uuid("assigned_agent_id").references(() => agents.id),
  status: text("status").notNull().default("pending"), // pending, in_progress, completed, failed
  priority: integer("priority").default(1),
  dependencies: jsonb("dependencies").$type<string[]>().default([]),
  estimatedTime: integer("estimated_time"), // Estimated time in seconds
  actualTime: integer("actual_time"), // Actual completion time
  artifacts: jsonb("artifacts").$type<string[]>().default([]), // List of file paths created
  createdAt: timestamp("created_at").defaultNow().notNull(),
  completedAt: timestamp("completed_at"),
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

export const insertWorkPackageSchema = createInsertSchema(workPackages).pick({
  id: true,
  sessionId: true,
  title: true,
  description: true,
  assignedAgentId: true,
  priority: true,
  dependencies: true,
  estimatedTime: true,
});

// Types
export type User = typeof users.$inferSelect;
export type InsertUser = z.infer<typeof insertUserSchema>;
export type Session = typeof sessions.$inferSelect;
export type InsertSession = z.infer<typeof insertSessionSchema>;
export type Agent = typeof agents.$inferSelect;
export type InsertAgent = z.infer<typeof insertAgentSchema>;
export type WorkPackage = typeof workPackages.$inferSelect;
export type InsertWorkPackage = z.infer<typeof insertWorkPackageSchema>;
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
