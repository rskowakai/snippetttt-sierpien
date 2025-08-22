import { useEffect, useRef } from 'react';
import { supabase } from '@/lib/supabase';
import { useToast } from '@/hooks/use-toast';

export function useRealtime(userId: string | null) {
  const { toast } = useToast();
  const subscriptionRef = useRef<any>(null);

  useEffect(() => {
    if (!userId) return;

    // Subscribe to processing queue changes for this user
    subscriptionRef.current = supabase
      .channel('processing_updates')
      .on(
        'postgres_changes',
        {
          event: 'UPDATE',
          schema: 'public',
          table: 'processing_queue',
          filter: `documents.uploaded_by=eq.${userId}`,
        },
        (payload) => {
          const { status, error_message } = payload.new;
          
          if (status === 'completed') {
            toast({
              title: "Document processed successfully",
              description: "Your document has been encrypted and is now secure.",
            });
          } else if (status === 'failed') {
            toast({
              title: "Document processing failed",
              description: error_message || "An error occurred during processing.",
              variant: "destructive",
            });
          }
        }
      )
      .subscribe();

    return () => {
      if (subscriptionRef.current) {
        subscriptionRef.current.unsubscribe();
      }
    };
  }, [userId, toast]);

  return null;
}
