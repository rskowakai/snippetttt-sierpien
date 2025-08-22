import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

interface ProcessingRequest {
  document_id: string;
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  try {
    // Initialize Supabase client
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    );

    const { document_id } = await req.json() as ProcessingRequest;

    // Update status to processing
    await supabase
      .from('processing_queue')
      .update({ status: 'processing', progress: 10 })
      .eq('document_id', document_id);

    // Get document details
    const { data: document, error: docError } = await supabase
      .from('documents')
      .select('*')
      .eq('id', document_id)
      .single();

    if (docError) throw docError;

    // Download file from temporary storage
    const { data: fileData, error: downloadError } = await supabase.storage
      .from('documents-temp')
      .download(document.storage_path);

    if (downloadError) throw downloadError;

    // Update progress
    await supabase
      .from('processing_queue')
      .update({ progress: 30 })
      .eq('document_id', document_id);

    // Simulate KMS - Generate DEK (Data Encryption Key)
    const kekKey = Deno.env.get('KEK_KEY') || 'default-kek-key-for-simulation';
    const dek = crypto.getRandomValues(new Uint8Array(32)); // 256-bit key
    const iv = crypto.getRandomValues(new Uint8Array(12)); // 96-bit IV for GCM

    // Update progress
    await supabase
      .from('processing_queue')
      .update({ progress: 50 })
      .eq('document_id', document_id);

    // Encrypt file content using AES-256-GCM
    const keyMaterial = await crypto.subtle.importKey(
      "raw",
      dek,
      { name: "AES-GCM" },
      false,
      ["encrypt"]
    );

    const fileBuffer = await fileData.arrayBuffer();
    
    const encryptedData = await crypto.subtle.encrypt(
      {
        name: "AES-GCM",
        iv: iv,
      },
      keyMaterial,
      fileBuffer
    );

    // Extract auth tag (last 16 bytes)
    const encryptedBuffer = new Uint8Array(encryptedData);
    const authTag = encryptedBuffer.slice(-16);
    const ciphertext = encryptedBuffer.slice(0, -16);

    // Update progress
    await supabase
      .from('processing_queue')
      .update({ progress: 70 })
      .eq('document_id', document_id);

    // Encrypt DEK with KEK (simplified simulation)
    const kekBuffer = new TextEncoder().encode(kekKey.padEnd(32, '0').slice(0, 32));
    const kekKeyMaterial = await crypto.subtle.importKey(
      "raw",
      kekBuffer,
      { name: "AES-GCM" },
      false,
      ["encrypt"]
    );

    const kekIv = crypto.getRandomValues(new Uint8Array(12));
    const encryptedDEK = await crypto.subtle.encrypt(
      {
        name: "AES-GCM",
        iv: kekIv,
      },
      kekKeyMaterial,
      dek
    );

    // Store encrypted file in secure storage
    const secureFilename = `encrypted/${document_id}-${Date.now()}.enc`;
    const { error: uploadError } = await supabase.storage
      .from('documents-encrypted')
      .upload(secureFilename, ciphertext);

    if (uploadError) throw uploadError;

    // Update progress
    await supabase
      .from('processing_queue')
      .update({ progress: 85 })
      .eq('document_id', document_id);

    // Store encryption metadata in the documents table
    const encryptedDEKArray = new Uint8Array(encryptedDEK);
    const encryptedDEKWithIv = new Uint8Array(12 + encryptedDEKArray.length);
    encryptedDEKWithIv.set(kekIv);
    encryptedDEKWithIv.set(encryptedDEKArray, 12);

    const encryptionKeyId = btoa(String.fromCharCode(...encryptedDEKWithIv)) + '|' + 
                           btoa(String.fromCharCode(...iv)) + '|' + 
                           btoa(String.fromCharCode(...authTag));

    // Update document record
    await supabase
      .from('documents')
      .update({
        encrypted_storage_path: secureFilename,
        encryption_key_id: encryptionKeyId
      })
      .eq('id', document_id);

    // Delete temporary file
    await supabase.storage
      .from('documents-temp')
      .remove([document.storage_path]);

    // Mark as completed
    await supabase
      .from('processing_queue')
      .update({ status: 'completed', progress: 100 })
      .eq('document_id', document_id);

    return new Response(
      JSON.stringify({ success: true, message: 'Document encrypted successfully' }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200,
      }
    );

  } catch (error) {
    console.error('Error processing document:', error);

    // Update status to failed
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    );

    const { document_id } = await req.json().catch(() => ({}));
    
    if (document_id) {
      await supabase
        .from('processing_queue')
        .update({ 
          status: 'failed', 
          error_message: error.message || 'Unknown error occurred' 
        })
        .eq('document_id', document_id);
    }

    return new Response(
      JSON.stringify({ error: error.message }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 500,
      }
    );
  }
});
