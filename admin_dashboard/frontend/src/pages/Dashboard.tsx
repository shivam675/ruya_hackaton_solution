
import { Link, Outlet } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Briefcase, FileText, Home, Brain } from 'lucide-react';
import HRChatBubble from '@/components/HRChatBubble';

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Briefcase className="h-8 w-8 text-purple-600" />
              <h1 className="ml-3 text-xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                HR Recruitment System
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Public Access
                <span className="ml-2 px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full">
                  No Login Required
                </span>
              </span>
            </div>
          </div>
        </div>
      </header>
      
      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Navigation */}
        <nav className="mb-8">
          <div className="flex space-x-4">
            <Link to="/dashboard">
              <Button variant="ghost" className="flex items-center">
                <Home className="h-4 w-4 mr-2" />
                Home
              </Button>
            </Link>
            <Link to="/dashboard/job-postings">
              <Button variant="ghost" className="flex items-center">
                <Briefcase className="h-4 w-4 mr-2" />
                Job Postings
              </Button>
            </Link>
            <Link to="/dashboard/interviews">
              <Button variant="ghost" className="flex items-center">
                <FileText className="h-4 w-4 mr-2" />
                Interviews
              </Button>
            </Link>
            <Link to="/dashboard/learning">
              <Button variant="ghost" className="flex items-center">
                <Brain className="h-4 w-4 mr-2" />
                AI Learning
              </Button>
            </Link>
          </div>
        </nav>
        
        {/* Page Content */}
        <Outlet />
      </div>

      {/* HR Chat Bubble */}
      <HRChatBubble />
    </div>
  );
}
