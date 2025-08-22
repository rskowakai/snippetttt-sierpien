import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL!;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
  }
});

export type Database = {
  public: {
    Tables: {
      profiles: {
        Row: {
          id: string;
          email: string;
          first_name: string;
          last_name: string;
          organization: string | null;
          role: 'admin' | 'lawyer' | 'paralegal' | 'client';
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id: string;
          email: string;
          first_name: string;
          last_name: string;
          organization?: string | null;
          role?: 'admin' | 'lawyer' | 'paralegal' | 'client';
        };
      };
      processing_queue: {
        Row: {
          id: string;
          document_id: string;
          status: 'pending' | 'processing' | 'completed' | 'failed';
          error_message: string | null;
          progress: number;
          created_at: string;
          updated_at: string;
        };
      };
    };
  };
};
