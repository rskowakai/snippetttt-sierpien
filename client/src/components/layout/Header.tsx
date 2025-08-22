import { Bell, Shield, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

interface HeaderProps {
  user: any;
  onSignOut: () => void;
}

export function Header({ user, onSignOut }: HeaderProps) {
  const getInitials = (firstName: string, lastName: string) => {
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 bg-blue-700 rounded-lg flex items-center justify-center">
              <Shield className="text-white text-lg" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">LegalTech Pro</h1>
              <p className="text-xs text-gray-500">Secure Document Platform</p>
            </div>
          </div>
          
          <nav className="hidden md:flex space-x-8">
            <a href="#" className="text-blue-700 border-b-2 border-blue-700 pb-1 px-1 text-sm font-medium" data-testid="nav-dashboard">
              Dashboard
            </a>
            <a href="#" className="text-gray-500 hover:text-gray-700 px-1 text-sm font-medium" data-testid="nav-documents">
              Documents
            </a>
            <a href="#" className="text-gray-500 hover:text-gray-700 px-1 text-sm font-medium" data-testid="nav-ai-assistant">
              AI Assistant
            </a>
            <a href="#" className="text-gray-500 hover:text-gray-700 px-1 text-sm font-medium" data-testid="nav-cases">
              Cases
            </a>
          </nav>

          <div className="flex items-center space-x-4">
            <div className="relative">
              <Button variant="ghost" size="sm" className="p-2 text-gray-400 hover:text-gray-600 relative" data-testid="button-notifications">
                <Bell className="h-5 w-5" />
                <span className="absolute -top-1 -right-1 h-5 w-5 bg-red-600 text-white text-xs rounded-full flex items-center justify-center">
                  3
                </span>
              </Button>
            </div>
            
            <div className="flex items-center space-x-3">
              <Avatar className="h-8 w-8" data-testid="avatar-user">
                <AvatarFallback className="bg-blue-700 text-white">
                  {user ? getInitials(user.first_name || 'U', user.last_name || 'U') : 'U'}
                </AvatarFallback>
              </Avatar>
              <span className="text-gray-700 font-medium text-sm" data-testid="text-username">
                {user ? `${user.first_name} ${user.last_name}` : 'User'}
              </span>
              <Button variant="ghost" onClick={onSignOut} className="text-sm" data-testid="button-signout">
                Sign Out
              </Button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
