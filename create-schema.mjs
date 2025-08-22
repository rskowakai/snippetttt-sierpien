import { createClient } from '@supabase/supabase-js';

async function createSchema() {
  const supabase = createClient(
    process.env.VITE_SUPABASE_URL,
    process.env.SUPABASE_SERVICE_ROLE_KEY
  );

  console.log('🚀 Creating database schema manually...');

  try {
    // First, let's verify we can access Supabase
    const { data: test } = await supabase.auth.getSession();
    console.log('✅ Connected to Supabase');

    // Since we can't run SQL directly, let's use the SQL Editor approach
    // Let's check what tables exist first
    console.log('📋 Please run the following SQL commands in your Supabase SQL Editor:');
    console.log('');
    console.log('1. Go to your Supabase Dashboard > SQL Editor');
    console.log('2. Run the following commands one by one:');
    console.log('');

    console.log('-- Enable extensions');
    console.log('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";');
    console.log('CREATE EXTENSION IF NOT EXISTS "vector";');
    console.log('');

    console.log('-- Create ENUMs');
    console.log("CREATE TYPE user_role AS ENUM ('admin', 'lawyer', 'paralegal', 'client');");
    console.log("CREATE TYPE case_status AS ENUM ('active', 'pending', 'closed', 'archived');");
    console.log("CREATE TYPE case_priority AS ENUM ('low', 'medium', 'high', 'urgent');");
    console.log("CREATE TYPE processing_status AS ENUM ('pending', 'processing', 'completed', 'failed');");
    console.log("CREATE TYPE document_type AS ENUM ('contract', 'brief', 'evidence', 'correspondence', 'research', 'other');");
    console.log('');

    console.log('-- Create profiles table');
    console.log(`CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    organization TEXT,
    role user_role DEFAULT 'client',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);`);
    console.log('');

    console.log('-- Enable RLS on profiles');
    console.log('ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;');
    console.log('');

    console.log('-- Create RLS policies for profiles');
    console.log(`CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (auth.uid() = id);`);
    console.log('');

    console.log(`CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (auth.uid() = id);`);
    console.log('');

    console.log('-- Create auth trigger function');
    console.log(`CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, first_name, last_name, organization)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'first_name', ''),
    COALESCE(NEW.raw_user_meta_data->>'last_name', ''),
    COALESCE(NEW.raw_user_meta_data->>'organization', '')
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;`);
    console.log('');

    console.log('-- Create auth trigger');
    console.log(`DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();`);
    console.log('');

    console.log('✅ After running these commands, the authentication should work!');
    console.log('');
    console.log('Then come back here and I will continue with the remaining tables...');

  } catch (error) {
    console.error('❌ Error:', error);
  }
}

createSchema();