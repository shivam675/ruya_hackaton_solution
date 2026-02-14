import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { interviewsAPI } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, Calendar, Briefcase, Clock } from 'lucide-react';
import { format } from 'date-fns';

interface Interview {
  _id: string;
  candidate_id: string;
  candidate_name?: string;
  job_posting_id: string;
  job_title?: string;
  scheduled_at: string;
  status: string;
  interview_type: string;
  score?: number;
  feedback?: string;
  created_at: string;
}

export default function Interviews() {
  const [statusFilter, setStatusFilter] = useState<string | null>(null);

  const { data: interviews = [], isLoading } = useQuery({
    queryKey: ['interviews', statusFilter],
    queryFn: () => interviewsAPI.getAll(undefined, statusFilter ?? undefined),
  });

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      scheduled: 'bg-blue-100 text-blue-700',
      completed: 'bg-green-100 text-green-700',
      cancelled: 'bg-red-100 text-red-700',
      in_progress: 'bg-yellow-100 text-yellow-700',
    };
    return colors[status] || 'bg-gray-100 text-gray-700';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-purple-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Interviews</h2>
          <p className="text-gray-600 mt-1">Manage and track all interviews</p>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex space-x-2">
        <Badge
          variant={statusFilter === null ? 'default' : 'outline'}
          className="cursor-pointer"
          onClick={() => setStatusFilter(null)}
        >
          All
        </Badge>
        <Badge
          variant={statusFilter === 'scheduled' ? 'default' : 'outline'}
          className="cursor-pointer"
          onClick={() => setStatusFilter('scheduled')}
        >
          Scheduled
        </Badge>
        <Badge
          variant={statusFilter === 'in_progress' ? 'default' : 'outline'}
          className="cursor-pointer"
          onClick={() => setStatusFilter('in_progress')}
        >
          In Progress
        </Badge>
        <Badge
          variant={statusFilter === 'completed' ? 'default' : 'outline'}
          className="cursor-pointer"
          onClick={() => setStatusFilter('completed')}
        >
          Completed
        </Badge>
      </div>

      {/* Interviews List */}
      <div className="grid gap-4">
        {interviews.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <Calendar className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-600">No interviews found</p>
            </CardContent>
          </Card>
        ) : (
          interviews.map((interview: Interview) => (
            <Card key={interview._id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <CardTitle className="text-lg">
                      {interview.candidate_name || 'Candidate'}
                    </CardTitle>
                    <CardDescription className="flex items-center gap-4">
                      <span className="flex items-center">
                        <Briefcase className="h-4 w-4 mr-1" />
                        {interview.job_title || interview.job_posting_id}
                      </span>
                      <span className="flex items-center">
                        <Clock className="h-4 w-4 mr-1" />
                        {interview.interview_type}
                      </span>
                    </CardDescription>
                  </div>
                  <Badge className={getStatusColor(interview.status)}>
                    {interview.status.replace('_', ' ')}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center text-sm text-gray-600">
                    <Calendar className="h-4 w-4 mr-2" />
                    Scheduled: {format(new Date(interview.scheduled_at), 'PPp')}
                  </div>
                  
                  {interview.score !== undefined && (
                    <div className="flex items-center text-sm">
                      <span className="font-medium mr-2">Score:</span>
                      <Badge variant="outline">{interview.score}/100</Badge>
                    </div>
                  )}
                  
                  {interview.feedback && (
                    <div className="text-sm">
                      <span className="font-medium">Feedback:</span>
                      <p className="text-gray-600 mt-1">{interview.feedback}</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
