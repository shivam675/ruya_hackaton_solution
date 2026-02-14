import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { candidatesAPI, jobPostingsAPI } from '@/lib/api';
import { Download, Mail, CheckCircle, Loader2 } from 'lucide-react';

interface Candidate {
  _id: string;
  name: string;
  email: string;
  skills: string[];
  experience: number;
  confidence: number;
  status: string;
  cv_path?: string;
}

export default function Candidates() {
  const { jobId } = useParams<{ jobId: string }>();
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [jobTitle, setJobTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(false);
  const [selectedCandidates, setSelectedCandidates] = useState<Set<string>>(new Set());
  
  useEffect(() => {
    if (jobId && jobId !== 'undefined') {
      fetchJobDetails();
      fetchCandidates();
    }
  }, [jobId]);
  
  const fetchJobDetails = async () => {
    if (!jobId || jobId === 'undefined') return;
    try {
      const job = await jobPostingsAPI.getById(jobId);
      setJobTitle(job.title);
    } catch (error) {
      console.error('Failed to fetch job details:', error);
    }
  };
  
  const fetchCandidates = async () => {
    if (!jobId || jobId === 'undefined') return;
    setLoading(true);
    try {
      const data = await candidatesAPI.getByJob(jobId);
      setCandidates(data);
    } catch (error) {
      console.error('Failed to fetch candidates:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleFetchFromCVAgent = async () => {
    if (!jobId || jobId === 'undefined') {
      alert('Invalid job ID');
      return;
    }
    setFetching(true);
    try {
      await candidatesAPI.fetchFromCVAgent(jobId);
      await fetchCandidates();
      alert('Candidates fetched successfully!');
    } catch (error: any) {
      alert('Failed to fetch candidates: ' + (error.response?.data?.detail || error.message));
    } finally {
      setFetching(false);
    }
  };
  
  const handleToggleCandidate = (candidateId: string) => {
    const newSelected = new Set(selectedCandidates);
    if (newSelected.has(candidateId)) {
      newSelected.delete(candidateId);
    } else {
      newSelected.add(candidateId);
    }
    setSelectedCandidates(newSelected);
  };
  
  const handleApprove = async () => {
    if (selectedCandidates.size === 0) {
      alert('Please select at least one candidate');
      return;
    }
    
    try {
      await candidatesAPI.approve(Array.from(selectedCandidates), true);
      await fetchCandidates();
      setSelectedCandidates(new Set());
      alert('Candidates approved and emails sent!');
    } catch (error: any) {
      alert('Failed to approve candidates: ' + (error.response?.data?.detail || error.message));
    }
  };
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Candidates for {jobTitle}</h2>
          <p className="text-muted-foreground mt-1">
            Review and approve candidates for interview
          </p>
        </div>
        <div className="flex gap-2">
          <Button 
            onClick={handleFetchFromCVAgent}
            disabled={fetching}
            variant="outline"
          >
            {fetching ? (
              <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Fetching...</>
            ) : (
              <><Download className="mr-2 h-4 w-4" /> Fetch from CV Agent</>
            )}
          </Button>
          {selectedCandidates.size > 0 && (
            <Button onClick={handleApprove}>
              <Mail className="mr-2 h-4 w-4" />
              Approve & Send Email ({selectedCandidates.size})
            </Button>
          )}
        </div>
      </div>
      
      {loading ? (
        <div className="text-center py-12">Loading candidates...</div>
      ) : candidates.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <p className="text-muted-foreground">
              No candidates yet. Click "Fetch from CV Agent" to shortlist candidates.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {candidates.map((candidate) => (
            <Card 
              key={candidate._id}
              className={`cursor-pointer transition-all ${
                selectedCandidates.has(candidate._id) ? 'ring-2 ring-purple-500' : ''
              }`}
              onClick={() => handleToggleCandidate(candidate._id)}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      {candidate.name}
                      {selectedCandidates.has(candidate._id) ? (
                        <CheckCircle className="h-5 w-5 text-purple-600" />
                      ) : (
                        <div className="h-5 w-5 border-2 rounded-full" />
                      )}
                    </CardTitle>
                    <CardDescription>{candidate.email}</CardDescription>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold">
                      Confidence: {(candidate.confidence * 100).toFixed(0)}%
                    </div>
                    <div className="text-xs text-muted-foreground capitalize">
                      {candidate.status.replace('_', ' ')}
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <span className="text-sm font-medium">Experience:</span>
                  <span className="text-sm text-muted-foreground ml-2">
                    {candidate.experience} years
                  </span>
                </div>
                
                <div>
                  <span className="text-sm font-medium">Skills:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {candidate.skills.map((skill, index) => (
                      <span 
                        key={index}
                        className="px-2 py-1 text-xs bg-blue-50 text-blue-700 rounded"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
