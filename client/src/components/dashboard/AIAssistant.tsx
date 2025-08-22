import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/lib/supabase";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Bot, User, Send } from "lucide-react";

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export function AIAssistant() {
  const [message, setMessage] = useState("");
  const { toast } = useToast();
  const queryClient = useQueryClient();

  const { data: messages = [], isLoading } = useQuery({
    queryKey: ['ai-messages'],
    queryFn: async () => {
      // Get the most recent conversation
      const { data: conversations } = await supabase
        .from('ai_conversations')
        .select('*')
        .order('updated_at', { ascending: false })
        .limit(1);

      if (!conversations || conversations.length === 0) {
        return [];
      }

      const { data: messages, error } = await supabase
        .from('ai_messages')
        .select('*')
        .eq('conversation_id', conversations[0].id)
        .order('created_at', { ascending: true });

      if (error) throw error;
      return messages as Message[];
    },
  });

  const sendMessageMutation = useMutation({
    mutationFn: async (query: string) => {
      // First, ensure we have a conversation
      let conversationId;
      
      const { data: existingConversations } = await supabase
        .from('ai_conversations')
        .select('*')
        .order('updated_at', { ascending: false })
        .limit(1);

      if (existingConversations && existingConversations.length > 0) {
        conversationId = existingConversations[0].id;
      } else {
        const { data: newConversation, error: convError } = await supabase
          .from('ai_conversations')
          .insert({
            title: 'Legal Analysis Chat',
          })
          .select()
          .single();

        if (convError) throw convError;
        conversationId = newConversation.id;
      }

      // Save user message
      const { error: userMessageError } = await supabase
        .from('ai_messages')
        .insert({
          conversation_id: conversationId,
          role: 'user',
          content: query,
        });

      if (userMessageError) throw userMessageError;

      // Call AI RAG handler Edge Function
      const { data, error } = await supabase.functions.invoke('ai-rag-handler', {
        body: { query, case_id: null },
      });

      if (error) throw error;

      // Save AI response
      const { error: aiMessageError } = await supabase
        .from('ai_messages')
        .insert({
          conversation_id: conversationId,
          role: 'assistant',
          content: data.response,
        });

      if (aiMessageError) throw aiMessageError;

      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai-messages'] });
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
      setMessage("");
    },
    onError: (error: any) => {
      toast({
        title: "AI query failed",
        description: error.message || "Failed to process your query",
        variant: "destructive",
      });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !sendMessageMutation.isPending) {
      sendMessageMutation.mutate(message.trim());
    }
  };

  return (
    <div className="lg:col-span-1">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 h-fit">
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-10 h-10 bg-purple-500 bg-opacity-10 rounded-lg flex items-center justify-center">
            <Bot className="text-purple-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">AI Legal Assistant</h2>
            <p className="text-sm text-gray-600">RAG-powered document analysis</p>
          </div>
        </div>

        {/* Chat Interface */}
        <ScrollArea className="h-96 mb-6" data-testid="chat-messages">
          {isLoading ? (
            <div className="space-y-4">
              {Array.from({ length: 2 }).map((_, i) => (
                <div key={i} className="flex space-x-3 animate-pulse">
                  <div className="w-8 h-8 bg-gray-200 rounded-full"></div>
                  <div className="flex-1">
                    <div className="w-full h-20 bg-gray-200 rounded-lg"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : messages.length === 0 ? (
            <div className="text-center py-8 text-gray-500" data-testid="empty-chat">
              <Bot className="mx-auto h-12 w-12 text-gray-300 mb-4" />
              <p>Ask me anything about your legal documents!</p>
              <p className="text-sm mt-2">I can analyze contracts, identify risks, and provide insights.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((msg) => (
                <div key={msg.id} className="flex space-x-3" data-testid={`message-${msg.id}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                    msg.role === 'user' ? 'bg-gray-300' : 'bg-purple-500'
                  }`}>
                    {msg.role === 'user' ? (
                      <User className="text-gray-600 text-sm" />
                    ) : (
                      <Bot className="text-white text-sm" />
                    )}
                  </div>
                  <div className={`rounded-lg p-3 flex-1 ${
                    msg.role === 'user' ? 'bg-gray-100' : 'bg-purple-50'
                  }`}>
                    <p className="text-sm text-gray-900" data-testid={`message-content-${msg.id}`}>
                      {msg.content}
                    </p>
                  </div>
                </div>
              ))}
              {sendMessageMutation.isPending && (
                <div className="flex space-x-3">
                  <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center flex-shrink-0">
                    <Bot className="text-white text-sm" />
                  </div>
                  <div className="bg-purple-50 rounded-lg p-3 flex-1">
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse"></div>
                      <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                      <div className="w-2 h-2 bg-purple-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </ScrollArea>

        {/* Input Area */}
        <div className="border-t pt-4">
          <form onSubmit={handleSubmit} className="flex space-x-2">
            <Input
              type="text"
              placeholder="Ask about your documents..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              className="flex-1"
              disabled={sendMessageMutation.isPending}
              data-testid="input-ai-message"
            />
            <Button
              type="submit"
              className="bg-purple-600 text-white hover:bg-purple-700"
              disabled={!message.trim() || sendMessageMutation.isPending}
              data-testid="button-send-message"
            >
              <Send className="h-4 w-4" />
            </Button>
          </form>
          <p className="text-xs text-gray-500 mt-2">AI responses are generated from your encrypted document library</p>
        </div>
      </div>
    </div>
  );
}
