import { Header } from "@/components/layout/Header";
import { DashboardStats } from "@/components/dashboard/DashboardStats";
import { DocumentUploader } from "@/components/dashboard/DocumentUploader";
import { AIAssistant } from "@/components/dashboard/AIAssistant";
import { SecurityStatus } from "@/components/dashboard/SecurityStatus";
import { DocumentsTable } from "@/components/dashboard/DocumentsTable";
import { useAuth } from "@/hooks/useAuth";
import { useRealtime } from "@/hooks/useRealtime";

export default function Dashboard() {
  const { user, profile, signOut } = useAuth();
  
  // Set up real-time notifications
  useRealtime(user?.id || null);

  return (
    <div className="min-h-screen bg-gray-50" data-testid="dashboard-page">
      <Header user={profile} onSignOut={signOut} />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <DashboardStats />
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <DocumentUploader />
          
          <div>
            <AIAssistant />
            <SecurityStatus />
          </div>
        </div>

        <DocumentsTable />
      </div>
    </div>
  );
}
