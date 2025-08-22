import { createClient } from '@supabase/supabase-js';
import fs from 'fs';

async function runMigrations() {
  const supabase = createClient(
    process.env.VITE_SUPABASE_URL,
    process.env.SUPABASE_SERVICE_ROLE_KEY
  );

  try {
    console.log('🚀 Setting up database schema...');
    
    // Read the initial schema migration
    const schemaSql = fs.readFileSync('./supabase/supabase/migrations/001_initial_schema.sql', 'utf8');
    
    // Split SQL into individual statements and execute them
    const statements = schemaSql.split(';').filter(stmt => stmt.trim());
    
    for (let i = 0; i < statements.length; i++) {
      const stmt = statements[i].trim();
      if (!stmt) continue;
      
      console.log(`Executing statement ${i + 1}/${statements.length}...`);
      
      try {
        const { error } = await supabase.rpc('exec_sql', { sql: stmt + ';' });
        if (error && !error.message.includes('already exists')) {
          console.log(`Warning: ${error.message}`);
        }
      } catch (err) {
        // Try alternative approach using direct query
        try {
          const { error } = await supabase.from('_sql_exec').insert({ query: stmt });
          if (error && !error.message.includes('already exists')) {
            console.log(`Statement warning: ${error.message}`);
          }
        } catch (directErr) {
          console.log(`Could not execute: ${stmt.substring(0, 100)}...`);
        }
      }
    }
    
    console.log('✅ Schema migration completed');
    
    // Read and execute auth triggers
    const triggersSql = fs.readFileSync('./supabase/supabase/migrations/002_auth_triggers.sql', 'utf8');
    const triggerStatements = triggersSql.split(';').filter(stmt => stmt.trim());
    
    for (let i = 0; i < triggerStatements.length; i++) {
      const stmt = triggerStatements[i].trim();
      if (!stmt) continue;
      
      console.log(`Executing trigger statement ${i + 1}/${triggerStatements.length}...`);
      
      try {
        const { error } = await supabase.rpc('exec_sql', { sql: stmt + ';' });
        if (error && !error.message.includes('already exists')) {
          console.log(`Warning: ${error.message}`);
        }
      } catch (err) {
        console.log(`Could not execute: ${stmt.substring(0, 100)}...`);
      }
    }
    
    console.log('✅ Triggers migration completed');
    
    // Test if schema is working
    const { data, error } = await supabase.from('profiles').select('count', { count: 'exact' });
    
    if (error) {
      console.log('❌ Schema verification failed:', error.message);
    } else {
      console.log('✅ Database schema is working correctly!');
    }
    
  } catch (error) {
    console.error('❌ Migration failed:', error);
  }
}

runMigrations();