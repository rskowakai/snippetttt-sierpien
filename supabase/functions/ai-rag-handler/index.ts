import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

interface RAGRequest {
  query: string;
  case_id?: string;
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

    const { query, case_id } = await req.json() as RAGRequest;

    // Select AI provider based on available API keys
    const openAIKey = Deno.env.get('OPENAI_API_KEY');
    const geminiKey = Deno.env.get('GEMINI_API_KEY');
    
    let aiProvider: 'openai' | 'gemini' = 'openai';
    let apiKey = openAIKey;
    
    if (!openAIKey && geminiKey) {
      aiProvider = 'gemini';
      apiKey = geminiKey;
    } else if (!openAIKey && !geminiKey) {
      throw new Error('No AI API key configured. Please set OPENAI_API_KEY or GEMINI_API_KEY environment variable.');
    }

    // Generate embedding for the query (simplified - in reality you'd use the same model as for indexing)
    let queryEmbedding: number[] = [];
    
    if (aiProvider === 'openai') {
      const embeddingResponse = await fetch('https://api.openai.com/v1/embeddings', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'text-embedding-ada-002',
          input: query,
        }),
      });

      if (!embeddingResponse.ok) {
        throw new Error('Failed to generate query embedding');
      }

      const embeddingData = await embeddingResponse.json();
      queryEmbedding = embeddingData.data[0].embedding;
    } else {
      // For Gemini, we'll simulate an embedding (in reality, you'd use their embedding API)
      // This is a simplified simulation
      queryEmbedding = Array.from({ length: 1536 }, () => Math.random() - 0.5);
    }

    // Search for similar documents using vector similarity
    // Note: This is a simplified version. In production, you'd use pgvector or similar
    let { data: relevantChunks, error: searchError } = await supabase
      .rpc('search_similar_documents', {
        query_embedding: queryEmbedding,
        similarity_threshold: 0.7,
        match_count: 5
      });

    if (searchError) {
      console.log('Vector search failed, using fallback text search');
      // Fallback to simple text search
      const { data: fallbackChunks } = await supabase
        .from('documents')
        .select('original_filename, id')
        .or(`original_filename.ilike.%${query}%`)
        .limit(5);
      
      relevantChunks = fallbackChunks?.map(doc => ({ 
        chunk_content: `Document: ${doc.original_filename}`,
        content: `Document: ${doc.original_filename}`
      })) || [];
    }

    // Construct context from relevant chunks
    const context = relevantChunks
      ?.map((chunk: any) => chunk.chunk_content || chunk.content)
      ?.join('\n\n') || '';

    // Generate response using the selected AI provider
    let aiResponse = '';
    
    if (aiProvider === 'openai') {
      const chatResponse = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'gpt-3.5-turbo',
          messages: [
            {
              role: 'system',
              content: `You are a legal AI assistant. Use the following context from legal documents to answer questions. If the context doesn't contain relevant information, say so clearly. 

Context:
${context}

Guidelines:
- Provide accurate legal analysis based on the context
- Identify potential risks or issues
- Be specific about document sections when possible
- If information is insufficient, clearly state limitations`
            },
            {
              role: 'user',
              content: query
            }
          ],
          max_tokens: 500,
          temperature: 0.3,
        }),
      });

      if (!chatResponse.ok) {
        throw new Error('Failed to get AI response');
      }

      const chatData = await chatResponse.json();
      aiResponse = chatData.choices[0].message.content;
    } else {
      // Gemini API integration
      const geminiResponse = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${apiKey}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          contents: [{
            parts: [{
              text: `You are a legal AI assistant. Use the following context from legal documents to answer questions. If the context doesn't contain relevant information, say so clearly.

Context:
${context}

Question: ${query}

Guidelines:
- Provide accurate legal analysis based on the context
- Identify potential risks or issues  
- Be specific about document sections when possible
- If information is insufficient, clearly state limitations`
            }]
          }],
          generationConfig: {
            temperature: 0.3,
            maxOutputTokens: 500,
          }
        }),
      });

      if (!geminiResponse.ok) {
        throw new Error('Failed to get Gemini response');
      }

      const geminiData = await geminiResponse.json();
      aiResponse = geminiData.candidates[0].content.parts[0].text;
    }

    // If no context was found, provide a helpful response
    if (!context || context.trim().length === 0) {
      aiResponse = "I don't have any relevant document context to answer your question. Please ensure you have uploaded and processed documents related to your query. I can help analyze contracts, identify risks, review legal documents, and provide insights once you have documents available in your library.";
    }

    return new Response(
      JSON.stringify({ 
        response: aiResponse,
        context_used: relevantChunks?.length || 0,
        ai_provider: aiProvider
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200,
      }
    );

  } catch (error) {
    console.error('Error in AI RAG handler:', error);

    return new Response(
      JSON.stringify({ error: error.message }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 500,
      }
    );
  }
});
