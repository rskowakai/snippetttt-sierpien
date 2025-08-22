import { createClient } from '@supabase/supabase-js';
import fs from 'fs';
import path from 'path';

async function setupDatabase() {
  // Initialize Supabase client with service role key for admin operations
  const supabase = createClient(
    process.env.VITE_SUPABASE_URL,
    process.env.SUPABASE_SERVICE_ROLE_KEY
  );

  try {
    console.log('Testing Supabase connection...');
    
    // Test connection by trying to access profiles table
    const { data, error } = await supabase
      .from('profiles')
      .select('count', { count: 'exact' })
      .limit(1);
    
    if (error) {
      console.error('Connection failed:', error);
      return;
    }
    
    console.log('✓ Successfully connected to Supabase');
    console.log('Profiles table exists and can be queried');
    
    // Test if we can access other key tables
    const { data: docs, error: docsError } = await supabase
      .from('documents')
      .select('count', { count: 'exact' })
      .limit(1);
      
    if (docsError) {
      console.log('Documents table error:', docsError.message);
    } else {
      console.log('✓ Documents table exists');
    }
    
  } catch (error) {
    console.error('Error:', error);
  }
}

setupDatabase();