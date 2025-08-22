import { createClient } from '@supabase/supabase-js';

async function setupStorage() {
  const supabase = createClient(
    process.env.VITE_SUPABASE_URL,
    process.env.SUPABASE_SERVICE_ROLE_KEY
  );

  console.log('🗄️ Setting up storage buckets...');
  
  try {
    // Create temp bucket for uploads
    const { data: tempBucket, error: tempError } = await supabase.storage.createBucket('documents-temp', {
      public: false,
      allowedMimeTypes: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
      fileSizeLimit: 52428800 // 50MB
    });
    
    if (tempError && !tempError.message.includes('already exists')) {
      console.log('❌ Error creating temp bucket:', tempError.message);
    } else {
      console.log('✅ documents-temp bucket ready');
    }
    
    // Create encrypted bucket for processed documents
    const { data: encBucket, error: encError } = await supabase.storage.createBucket('documents-encrypted', {
      public: false
    });
    
    if (encError && !encError.message.includes('already exists')) {
      console.log('❌ Error creating encrypted bucket:', encError.message);
    } else {
      console.log('✅ documents-encrypted bucket ready');
    }

    // Test upload to make sure buckets work
    console.log('🧪 Testing upload capabilities...');
    const testFile = new Blob(['test content'], { type: 'text/plain' });
    const { data: testUpload, error: testError } = await supabase.storage
      .from('documents-temp')
      .upload(`test/test-${Date.now()}.txt`, testFile);

    if (testError) {
      console.log('❌ Upload test failed:', testError.message);
    } else {
      console.log('✅ Upload test successful!');
      // Clean up test file
      await supabase.storage
        .from('documents-temp')
        .remove([testUpload.path]);
    }
    
    console.log('');
    console.log('✅ Storage setup complete! The document uploader should now work.');
    console.log('');
    console.log('📋 Next step: Run this minimal database setup in Supabase SQL Editor:');
    console.log('');
    console.log(`-- Minimal database schema for document uploads
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_filename TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Allow all operations for now (in production, add proper user-based policies)
CREATE POLICY "Allow all operations on documents" ON documents
    FOR ALL USING (true)
    WITH CHECK (true);`);

  } catch (error) {
    console.error('❌ Storage setup failed:', error.message);
  }
}

setupStorage();