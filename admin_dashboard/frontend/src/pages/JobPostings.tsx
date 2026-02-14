import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { jobPostingsAPI } from '@/lib/api';
import { Briefcase, Plus, Users, Calendar, X } from 'lucide-react';

interface JobPosting {
  _id: string;
  title: string;
  job_description: string;
  required_skills: string[];
  min_experience: number;
  location?: string;
  department?: string;
  candidates_count: number;
  is_active: boolean;
  created_at: string;
}

export default function JobPostings() {
  const [jobPostings, setJobPostings] = useState<JobPosting[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    job_description: '',
    required_skills: '',
    min_experience: 0,
    location: '',
    department: ''
  });
  const navigate = useNavigate();
  
  useEffect(() => {
    fetchJobPostings();
  }, []);
  
  const fetchJobPostings = async () => {
    try {
      const data = await jobPostingsAPI.getAll(true);
      setJobPostings(data);
    } catch (error) {
      console.error('Failed to fetch job postings:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateJob = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await jobPostingsAPI.create({
        ...formData,
        required_skills: formData.required_skills.split(',').map(s => s.trim()),
      });
      setShowCreateDialog(false);
      setFormData({
        title: '',
        job_description: '',
        required_skills: '',
        min_experience: 0,
        location: '',
        department: ''
      });
      await fetchJobPostings();
    } catch (error: any) {
      alert('Failed to create job posting: ' + (error.response?.data?.detail || error.message));
    }
  };
  
  if (loading) {
    return <div className="text-center py-12">Loading...</div>;
  }
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Job Postings</h2>
        <p className="text-muted-foreground">
            Manage job postings and view candidates
          </p>
        </div>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Plus className="mr-2 h-4 w-4" />
          New Job Posting
        </Button>
      </div>

      {/* Create Job Dialog */}
      {showCreateDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Create New Job Posting</CardTitle>
                <Button variant="ghost" size="sm" onClick={() => setShowCreateDialog(false)}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateJob} className="space-y-4">
                <div>
                  <Label htmlFor="title">Job Title</Label>
                  <Input
                    id="title"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="description">Job Description</Label>
                  <textarea
                    id="description"
                    className="w-full min-h-[100px] p-2 border rounded-md"
                    value={formData.job_description}
                    onChange={(e) => setFormData({ ...formData, job_description: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="skills">Required Skills (comma-separated)</Label>
                  <Input
                    id="skills"
                    placeholder="Python, React, SQL"
                    value={formData.required_skills}
                    onChange={(e) => setFormData({ ...formData, required_skills: e.target.value })}
                    required
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="experience">Min Experience (years)</Label>
                    <Input
                      id="experience"
                      type="number"
                      min="0"
                      value={formData.min_experience}
                      onChange={(e) => setFormData({ ...formData, min_experience: parseInt(e.target.value) })}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="location">Location</Label>
                    <Input
                      id="location"
                      value={formData.location}
                      onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                    />
                  </div>
                </div>
                <div>
                  <Label htmlFor="department">Department</Label>
                  <Input
                    id="department"
                    value={formData.department}
                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                  />
                </div>
                <div className="flex justify-end space-x-2">
                  <Button type="button" variant="outline" onClick={() => setShowCreateDialog(false)}>
                    Cancel
                  </Button>
                  <Button type="submit">
                    Create Job Posting
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      )}
      
      {jobPostings.length === 0 ? (
        <Card>
          <CardContent className="text-center py-12">
            <Briefcase className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-4 text-lg font-semibold">No job postings yet</h3>
            <p className="text-sm text-muted-foreground mt-2">
              Get started by creating your first job posting
            </p>
            <Button className="mt-4" onClick={() => setShowCreateDialog(true)}>
              Create Job Posting
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {jobPostings.map((job) => (
            <Card key={job._id} className="hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-xl">{job.title}</CardTitle>
                    <CardDescription className="mt-1">
                      {job.department || 'General'}
                    </CardDescription>
                  </div>
                  {job.is_active && (
                    <span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full">
                      Active
                    </span>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-sm text-gray-600 line-clamp-2">
                  {job.job_description}
                </p>
                
                <div className="flex items-center text-sm text-gray-500">
                  <Users className="h-4 w-4 mr-1" />
                  <span>{job.candidates_count} candidates</span>
                </div>
                
                <div className="flex items-center text-sm text-gray-500">
                  <Calendar className="h-4 w-4 mr-1" />
                  <span>{job.min_experience}+ years experience</span>
                </div>
                
                <div className="flex flex-wrap gap-1 mt-2">
                  {job.required_skills.slice(0, 3).map((skill, index) => (
                    <span 
                      key={index}
                      className="px-2 py-1 text-xs bg-purple-50 text-purple-700 rounded"
                    >
                      {skill}
                    </span>
                  ))}
                  {job.required_skills.length > 3 && (
                    <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                      +{job.required_skills.length - 3} more
                    </span>
                  )}
                </div>
                
                <Button 
                  className="w-full mt-4"
                  onClick={() => navigate(`/dashboard/job-postings/${job._id}`)}
                >
                  View Candidates
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
