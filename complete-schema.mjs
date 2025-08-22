import { createClient } from '@supabase/supabase-js';

async function showCompleteSchema() {
  console.log('📋 Complete Database Schema - Run these SQL commands in Supabase SQL Editor:');
  console.log('');
  
  console.log('-- Part 2: Documents and Cases Tables');
  console.log(`
-- Cases table
CREATE TABLE cases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    client_name TEXT NOT NULL,
    status case_status DEFAULT 'active',
    priority case_priority DEFAULT 'medium',
    assigned_lawyer_id UUID REFERENCES profiles(id),
    created_by UUID REFERENCES profiles(id) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    original_filename TEXT NOT NULL,
    filename TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    mime_type TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    encrypted_storage_path TEXT,
    encryption_key_id TEXT,
    document_type document_type DEFAULT 'other',
    case_id UUID REFERENCES cases(id),
    uploaded_by UUID REFERENCES profiles(id) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Processing queue table
CREATE TABLE processing_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE NOT NULL,
    status processing_status DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
`);

  console.log('-- Enable RLS on all tables');
  console.log(`
ALTER TABLE cases ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE processing_queue ENABLE ROW LEVEL SECURITY;
`);

  console.log('-- RLS Policies for Cases');
  console.log(`
CREATE POLICY "Users can view cases they're involved in" ON cases
    FOR SELECT USING (
        created_by = auth.uid() OR 
        assigned_lawyer_id = auth.uid() OR
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = auth.uid() 
            AND role IN ('admin', 'lawyer')
        )
    );

CREATE POLICY "Lawyers can create cases" ON cases
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = auth.uid() 
            AND role IN ('admin', 'lawyer')
        )
    );

CREATE POLICY "Users can update their cases" ON cases
    FOR UPDATE USING (
        created_by = auth.uid() OR 
        assigned_lawyer_id = auth.uid() OR
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = auth.uid() 
            AND role IN ('admin', 'lawyer')
        )
    );
`);

  console.log('-- RLS Policies for Documents');
  console.log(`
CREATE POLICY "Users can view their documents" ON documents
    FOR SELECT USING (
        uploaded_by = auth.uid() OR
        EXISTS (
            SELECT 1 FROM cases 
            WHERE id = documents.case_id 
            AND (created_by = auth.uid() OR assigned_lawyer_id = auth.uid())
        ) OR
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = auth.uid() 
            AND role IN ('admin', 'lawyer')
        )
    );

CREATE POLICY "Users can upload documents" ON documents
    FOR INSERT WITH CHECK (uploaded_by = auth.uid());

CREATE POLICY "Users can update their documents" ON documents
    FOR UPDATE USING (
        uploaded_by = auth.uid() OR
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = auth.uid() 
            AND role IN ('admin', 'lawyer')
        )
    );
`);

  console.log('-- RLS Policies for Processing Queue');
  console.log(`
CREATE POLICY "Users can view their processing items" ON processing_queue
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM documents 
            WHERE id = processing_queue.document_id 
            AND uploaded_by = auth.uid()
        ) OR
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE id = auth.uid() 
            AND role IN ('admin', 'lawyer')
        )
    );

CREATE POLICY "System can manage processing queue" ON processing_queue
    FOR ALL USING (true)
    WITH CHECK (true);
`);

  console.log('-- Storage Buckets (run these in Supabase Dashboard > Storage)');
  console.log(`
-- Create storage buckets (go to Storage tab in Supabase Dashboard):
-- 1. Create bucket: documents-temp (public: false)
-- 2. Create bucket: documents-encrypted (public: false)
`);

  console.log('-- Storage Policies');
  console.log(`
-- For documents-temp bucket
CREATE POLICY "Users can upload to temp bucket" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'documents-temp' AND
        auth.uid() IS NOT NULL
    );

CREATE POLICY "Users can read their temp files" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'documents-temp' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- For documents-encrypted bucket  
CREATE POLICY "System can manage encrypted documents" ON storage.objects
    FOR ALL USING (bucket_id = 'documents-encrypted');
`);

  console.log('');
  console.log('✅ After running these commands:');
  console.log('1. Create the two storage buckets in Supabase Dashboard > Storage');
  console.log('2. Let me know and I will continue with the Edge Functions setup!');
}

showCompleteSchema();