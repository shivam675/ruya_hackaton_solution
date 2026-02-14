import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { User, Calendar, Briefcase, Link as LinkIcon } from 'lucide-react';

export default function SampleDataInfo() {
  return (
    <Card className="border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-blue-50">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <User className="h-5 w-5 text-purple-600" />
          Sample Interview Data Available
        </CardTitle>
        <CardDescription>
          Use this test data to explore the interview features
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <User className="h-4 w-4 text-gray-500" />
              <span className="font-semibold">Candidate Name:</span>
            </div>
            <Badge variant="outline" className="text-base px-3 py-1">
              John Smith
            </Badge>
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Briefcase className="h-4 w-4 text-gray-500" />
              <span className="font-semibold">Position:</span>
            </div>
            <Badge variant="outline" className="text-base px-3 py-1">
              Senior Python Developer
            </Badge>
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4 text-gray-500" />
              <span className="font-semibold">Status:</span>
            </div>
            <Badge className="bg-blue-600 text-white">
              Scheduled
            </Badge>
          </div>
          
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <LinkIcon className="h-4 w-4 text-gray-500" />
              <span className="font-semibold">Interview Portal:</span>
            </div>
            <a
              href="/interview"
              target="_blank"
              rel="noopener noreferrer"
              className="text-purple-600 hover:text-purple-800 underline text-sm"
            >
              http://localhost:5173/interview
            </a>
          </div>
        </div>
        
        <div className="pt-4 border-t border-purple-200">
          <h4 className="font-semibold mb-2 text-sm text-gray-700">How to Access:</h4>
          <ol className="list-decimal list-inside space-y-1 text-sm text-gray-600">
            <li>Navigate to the Interview Portal link above</li>
            <li>Enter candidate name: <code className="bg-gray-100 px-2 py-0.5 rounded">John Smith</code></li>
            <li>Click "Start Interview" to begin the AI interview</li>
          </ol>
        </div>
        
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
          <p className="text-sm text-yellow-800">
            💡 <strong>Tip:</strong> This sample data is created automatically on backend startup. Check the Interviews page to see the scheduled interview.
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
