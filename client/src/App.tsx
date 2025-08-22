import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthModal } from "@/components/auth/AuthModal";
import { useAuth } from "@/hooks/useAuth";
import { supabase } from "@/lib/supabase";
import Dashboard from "@/pages/Dashboard";
import NotFound from "@/pages/not-found";

function Router() {
  const { user, signIn, signUp, loading } = useAuth();

  console.log('Auth state:', { user: !!user, loading });

  // Create anonymous user if no auth yet (for testing uploads)
  const createAnonymousUser = async () => {
    try {
      const { data, error } = await supabase.auth.signInAnonymously();
      if (error) {
        console.error('Anonymous auth failed:', error);
      } else {
        console.log('Anonymous user created:', data.user?.id);
      }
    } catch (error) {
      console.error('Failed to create anonymous user:', error);
    }
  };

  // Auto-create anonymous user if not authenticated
  if (!user && !loading) {
    createAnonymousUser();
  }

  // Show interface once we have any user (anonymous or real)
  if (user) {
    return (
      <Switch>
        <Route path="/" component={Dashboard} />
        <Route component={NotFound} />
      </Switch>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-700"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <AuthModal
        onLogin={signIn}
        onSignup={signUp}
        isLoading={loading}
      />
    );
  }

  return (
    <Switch>
      <Route path="/" component={Dashboard} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Router />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
