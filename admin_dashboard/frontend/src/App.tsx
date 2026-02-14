import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Dashboard from '@/pages/Dashboard';
import JobPostings from '@/pages/JobPostings';
import Candidates from '@/pages/Candidates';
import CandidateInterview from '@/pages/CandidateInterview';
import Interviews from '@/pages/Interviews';
import AgentLearning from '@/pages/AgentLearning';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter
        future={{
          v7_startTransition: true,
          v7_relativeSplatPath: true,
        }}
      >
        <Routes>
          <Route path="/interview" element={<CandidateInterview />} />
          <Route path="/dashboard" element={<Dashboard />}>
            <Route index element={<JobPostings />} />
            <Route path="job-postings" element={<JobPostings />} />
            <Route path="job-postings/:jobId" element={<Candidates />} />
            <Route path="interviews" element={<Interviews />} />
            <Route path="learning" element={<AgentLearning />} />
          </Route>
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
