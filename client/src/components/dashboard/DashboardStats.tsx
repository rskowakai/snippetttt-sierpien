import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/lib/supabase";
import { FileText, Lock, Clock, Bot } from "lucide-react";

export function DashboardStats() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const { data: documents } = await supabase.from('documents').select('*');
      const { data: encrypted } = await supabase.from('documents').select('*').eq('is_encrypted', true);
      const { data: processing } = await supabase.from('processing_queue').select('*').eq('status', 'processing');
      const { data: aiMessages } = await supabase.from('ai_messages').select('*').gte('created_at', new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString());

      return {
        totalDocuments: documents?.length || 0,
        encryptedFiles: encrypted?.length || 0,
        processingQueue: processing?.length || 0,
        aiQueries: aiMessages?.length || 0,
      };
    },
  });

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 animate-pulse">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-gray-200 rounded-lg"></div>
              <div className="ml-4">
                <div className="w-20 h-4 bg-gray-200 rounded mb-2"></div>
                <div className="w-16 h-8 bg-gray-200 rounded"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  const statsCards = [
    {
      title: "Total Documents",
      value: stats?.totalDocuments || 0,
      icon: FileText,
      bgColor: "bg-blue-700 bg-opacity-10",
      iconColor: "text-blue-700",
      testId: "stat-total-documents",
    },
    {
      title: "Encrypted Files",
      value: stats?.encryptedFiles || 0,
      icon: Lock,
      bgColor: "bg-green-600 bg-opacity-10",
      iconColor: "text-green-600",
      testId: "stat-encrypted-files",
    },
    {
      title: "Processing Queue",
      value: stats?.processingQueue || 0,
      icon: Clock,
      bgColor: "bg-yellow-500 bg-opacity-10",
      iconColor: "text-yellow-600",
      testId: "stat-processing-queue",
    },
    {
      title: "AI Queries Today",
      value: stats?.aiQueries || 0,
      icon: Bot,
      bgColor: "bg-purple-500 bg-opacity-10",
      iconColor: "text-purple-600",
      testId: "stat-ai-queries",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {statsCards.map((card) => (
        <div key={card.title} className="bg-white p-6 rounded-lg shadow-sm border border-gray-200" data-testid={card.testId}>
          <div className="flex items-center">
            <div className={`p-2 ${card.bgColor} rounded-lg`}>
              <card.icon className={`${card.iconColor} text-xl`} />
            </div>
            <div className="ml-4">
              <p className="text-sm text-gray-600">{card.title}</p>
              <p className="text-2xl font-bold text-gray-900" data-testid={`value-${card.testId}`}>
                {card.value}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
