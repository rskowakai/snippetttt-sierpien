import { sql } from "drizzle-orm";
import { pgTable, text, varchar, timestamp, jsonb, integer, boolean, pgEnum } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// Enums
export const userRoleEnum = pgEnum('user_role', ['admin', 'lawyer', 'paralegal', 'client']);
export const caseStatusEnum = pgEnum('case_status', ['active', 'pending', 'closed', 'archived']);
export const casePriorityEnum = pgEnum('case_priority', ['low', 'medium', 'high', 'urgent']);
export const processingStatusEnum = pgEnum('processing_status', ['pending', 'processing', 'completed', 'failed']);
export const documentTypeEnum = pgEnum('document_type', ['contract', 'brief', 'evidence', 'correspondence', 'research', 'other']);

// Profiles table
export const profiles = pgTable("profiles", {
  id: varchar("id").primaryKey(),
  email: text("email").notNull().unique(),
  firstName: text("first_name").notNull(),
  lastName: text("last_name").notNull(),
  organization: text("organization"),
  role: userRoleEnum("role").default('client'),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow()
});

// Cases table
export const cases = pgTable("cases", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  title: text("title").notNull(),
  description: text("description"),
  status: caseStatusEnum("status").default('pending'),
  priority: casePriorityEnum("priority").default('medium'),
  clientId: varchar("client_id").references(() => profiles.id),
  assignedLawyerId: varchar("assigned_lawyer_id").references(() => profiles.id),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow()
});

// Documents table
export const documents = pgTable("documents", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  filename: text("filename").notNull(),
  originalFilename: text("original_filename").notNull(),
  documentType: documentTypeEnum("document_type").default('other'),
  fileSize: integer("file_size"),
  mimeType: text("mime_type"),
  storagePath: text("storage_path"),
  caseId: varchar("case_id").references(() => cases.id),
  uploadedBy: varchar("uploaded_by").references(() => profiles.id),
  isEncrypted: boolean("is_encrypted").default(false),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow()
});

// Document encryption metadata
export const documentEncryption = pgTable("document_encryption", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  documentId: varchar("document_id").references(() => documents.id).notNull(),
  encryptedDEK: text("encrypted_dek").notNull(),
  iv: text("iv").notNull(),
  authTag: text("auth_tag").notNull(),
  encryptionAlgorithm: text("encryption_algorithm").default('AES-256-GCM'),
  createdAt: timestamp("created_at").defaultNow()
});

// Processing queue
export const processingQueue = pgTable("processing_queue", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  documentId: varchar("document_id").references(() => documents.id).notNull(),
  status: processingStatusEnum("status").default('pending'),
  errorMessage: text("error_message"),
  progress: integer("progress").default(0),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow()
});

// Vector documents for RAG
export const vectorDocuments = pgTable("vector_documents", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  documentId: varchar("document_id").references(() => documents.id).notNull(),
  chunkContent: text("chunk_content").notNull(),
  embedding: jsonb("embedding").notNull(),
  chunkIndex: integer("chunk_index"),
  createdAt: timestamp("created_at").defaultNow()
});

// AI conversations
export const aiConversations = pgTable("ai_conversations", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  userId: varchar("user_id").references(() => profiles.id).notNull(),
  caseId: varchar("case_id").references(() => cases.id),
  title: text("title"),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow()
});

// AI messages
export const aiMessages = pgTable("ai_messages", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  conversationId: varchar("conversation_id").references(() => aiConversations.id).notNull(),
  role: text("role").notNull(), // 'user' or 'assistant'
  content: text("content").notNull(),
  createdAt: timestamp("created_at").defaultNow()
});

// Insert schemas
export const insertProfileSchema = createInsertSchema(profiles).omit({
  id: true,
  createdAt: true,
  updatedAt: true
});

export const insertCaseSchema = createInsertSchema(cases).omit({
  id: true,
  createdAt: true,
  updatedAt: true
});

export const insertDocumentSchema = createInsertSchema(documents).omit({
  id: true,
  createdAt: true,
  updatedAt: true
});

export const insertProcessingQueueSchema = createInsertSchema(processingQueue).omit({
  id: true,
  createdAt: true,
  updatedAt: true
});

export const insertAiConversationSchema = createInsertSchema(aiConversations).omit({
  id: true,
  createdAt: true,
  updatedAt: true
});

export const insertAiMessageSchema = createInsertSchema(aiMessages).omit({
  id: true,
  createdAt: true
});

// Types
export type Profile = typeof profiles.$inferSelect;
export type InsertProfile = z.infer<typeof insertProfileSchema>;
export type Case = typeof cases.$inferSelect;
export type InsertCase = z.infer<typeof insertCaseSchema>;
export type Document = typeof documents.$inferSelect;
export type InsertDocument = z.infer<typeof insertDocumentSchema>;
export type DocumentEncryption = typeof documentEncryption.$inferSelect;
export type ProcessingQueue = typeof processingQueue.$inferSelect;
export type InsertProcessingQueue = z.infer<typeof insertProcessingQueueSchema>;
export type VectorDocument = typeof vectorDocuments.$inferSelect;
export type AiConversation = typeof aiConversations.$inferSelect;
export type InsertAiConversation = z.infer<typeof insertAiConversationSchema>;
export type AiMessage = typeof aiMessages.$inferSelect;
export type InsertAiMessage = z.infer<typeof insertAiMessageSchema>;

// Legacy user schema for compatibility
export const users = pgTable("users", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
});

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
});

export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;
