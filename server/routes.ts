import type { Express } from "express";
import { createServer, type Server } from "http";

export async function registerRoutes(app: Express): Promise<Server> {
  // Health check endpoint
  app.get("/api/health", (req, res) => {
    res.json({ status: "ok", message: "LegalTech Pro API is running" });
  });

  // All main functionality is handled by Supabase and Edge Functions
  // Frontend connects directly to Supabase for:
  // - Authentication (supabase.auth)
  // - Database operations (supabase.from())
  // - Real-time subscriptions (supabase.channel())
  // - Edge Functions (supabase.functions.invoke())
  // - Storage (supabase.storage)

  const httpServer = createServer(app);
  return httpServer;
}
