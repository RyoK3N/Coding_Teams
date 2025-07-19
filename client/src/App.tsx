import { Switch, Route, useLocation } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider, useTheme } from "@/components/theme-provider";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Button } from "@/components/ui/button";
import { Bell, Moon, Sun, Bot, LogOut } from "lucide-react";
import { useEffect, useState } from "react";
import { auth } from "@/lib/auth";
import Login from "@/pages/login";
import NotFound from "@/pages/not-found";

// Simplified Home component for testing
function Home() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-4">Coding-Team Dashboard</h1>
      <p className="text-gray-600">Welcome to your AI-powered development platform!</p>
    </div>
  );
}

// Simplified Session component
function SessionPage() {
  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-4">Session Page</h1>
      <p className="text-gray-600">Session management coming soon...</p>
    </div>
  );
}

function Header() {
  const { theme, toggleTheme } = useTheme();
  const user = auth.getUser();

  const handleLogout = () => {
    auth.logout();
  };

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <Bot className="h-8 w-8 text-blue-600 animate-pulse" />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-ping"></div>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  Coding-Team
                </h1>
                <span className="text-xs text-blue-600 font-medium">powered by Synexian</span>
              </div>
            </div>
            <span className="text-sm text-gray-500">
              AI-Powered Multi-Agent Development Platform
            </span>
          </div>
          <div className="flex items-center space-x-4">
            {user && (
              <span className="text-sm text-gray-600">
                {user.username}
              </span>
            )}
            <Button
              variant="ghost"
              size="sm"
              className="text-gray-500 hover:text-gray-700"
            >
              <Bell className="h-5 w-5" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={toggleTheme}
              className="text-gray-500 hover:text-gray-700"
            >
              <Moon className="h-5 w-5" />
            </Button>
            {user && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleLogout}
                className="text-gray-500 hover:text-gray-700"
              >
                <LogOut className="h-5 w-5" />
              </Button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

function ProtectedRoute({ component: Component }: { component: React.ComponentType }) {
  const [, setLocation] = useLocation();
  const isAuthenticated = auth.isAuthenticated();

  useEffect(() => {
    if (!isAuthenticated) {
      setLocation('/login');
    }
  }, [isAuthenticated, setLocation]);

  if (!isAuthenticated) {
    return null;
  }

  return <Component />;
}

function Router() {
  return (
    <Switch>
      <Route path="/login" component={Login} />
      <Route path="/" component={() => <ProtectedRoute component={Home} />} />
      <Route path="/session/:id" component={() => <ProtectedRoute component={SessionPage} />} />
      <Route component={NotFound} />
    </Switch>
  );
}

function AppContent() {
  const [location] = useLocation();
  const showHeader = location !== '/login';

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      {showHeader && <Header />}
      <main className={showHeader ? "max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6" : ""}>
        <Router />
      </main>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <TooltipProvider>
          <AppContent />
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
