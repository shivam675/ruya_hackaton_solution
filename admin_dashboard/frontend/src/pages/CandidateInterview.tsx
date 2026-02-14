import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { interviewsAPI } from '@/lib/api';
import { Loader2 } from 'lucide-react';

export default function CandidateInterview() {
  const [name, setName] = useState('');
  const [authenticated, setAuthenticated] = useState(false);
  const [interviewData, setInterviewData] = useState<any>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [transcript, setTranscript] = useState<any[]>([]);
  const [currentResponse, setCurrentResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [interviewStarted, setInterviewStarted] = useState(false);
  
  const [userInput, setUserInput] = useState('');
  
  const handleAuthenticate = async () => {
    setLoading(true);
    try {
      const data = await interviewsAPI.authenticateCandidate(name);
      setInterviewData(data);
      setAuthenticated(true);
    } catch (error: any) {
      alert('Authentication failed: ' + (error.response?.data?.detail || 'Interview not found'));
    } finally {
      setLoading(false);
    }
  };
  
  const startInterview = async () => {
    if (!interviewData) return;
    
    // Start interview via API
    try {
      const response = await fetch('http://localhost:8004/start-interview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          interview_id: interviewData.interview._id,
          job_description: interviewData.job_description
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to start interview');
      }
      
      const data = await response.json();
      setCurrentResponse(data.greeting);
      setInterviewStarted(true);
      
      // Connect WebSocket
      const websocket = new WebSocket(`ws://localhost:8004/ws/interview/${interviewData.interview._id}`);
      
      websocket.onopen = () => {
        console.log('WebSocket connected');
      };
      
      websocket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        
        if (message.type === 'text') {
          setCurrentResponse(message.data);
        } else if (message.type === 'transcript') {
          setTranscript(prev => [...prev, message.data]);
        } else if (message.type === 'audio') {
          // Handle audio playback if needed
          console.log('Received audio chunk');
        }
      };
      
      websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      websocket.onclose = () => {
        console.log('WebSocket closed');
        setWs(null);
      };
      
      setWs(websocket);
    } catch (error: any) {
      console.error('Failed to start interview:', error);
      alert('Failed to start interview: ' + (error.message || 'Unknown error. Make sure the Interview Agent is running on port 8004.'));
    }
  };
  
  const handleSendText = () => {
    if (!userInput.trim() || !ws) return;
    
    // Send text to WebSocket
    ws.send(JSON.stringify({
      type: 'text',
      data: userInput
    }));
    
    setUserInput('');
    setCurrentResponse('Thinking...');
  };
  
  const endInterview = async () => {
    if (ws) {
      ws.send(JSON.stringify({ type: 'control', data: 'end' }));
      ws.close();
    }
    
    try {
      await fetch(`http://localhost:8004/end-interview/${interviewData.interview._id}`, {
        method: 'POST'
      });
      alert('Interview completed! Thank you.');
    } catch (error) {
      console.error('Failed to end interview:', error);
    }
  };
  
  if (!authenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-blue-50 p-4">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-2xl text-center">Interview Portal</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="name">Enter Your Name</Label>
              <Input
                id="name"
                placeholder="John Doe"
                value={name}
                onChange={(e) => setName(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAuthenticate()}
              />
            </div>
            <Button 
              onClick={handleAuthenticate}
              className="w-full"
              disabled={!name.trim() || loading}
            >
              {loading ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Authenticating...</> : 'Start Interview'}
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-4">
      <div className="max-w-4xl mx-auto space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Interview for {interviewData.candidate.name}</CardTitle>
            <p className="text-sm text-muted-foreground">
              Position: {interviewData.job_description.substring(0, 100)}...
            </p>
          </CardHeader>
          <CardContent>
            {!interviewStarted ? (
              <div className="text-center py-8">
                <p className="mb-4 text-lg">Ready to begin your interview?</p>
                <Button onClick={startInterview} size="lg">
                  Start Interview
                </Button>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Current Response */}
                <div className="p-4 bg-purple-50 rounded-lg">
                  <p className="font-semibold text-purple-900 mb-2">Interviewer:</p>
                  <p className="text-gray-700">{currentResponse}</p>
                </div>
                
                {/* User Input */}
                <div className="space-y-2">
                  <Label htmlFor="response">Your Response:</Label>
                  <div className="flex gap-2">
                    <Input
                      id="response"
                      placeholder="Type your answer and press send..."
                      value={userInput}
                      onChange={(e) => setUserInput(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSendText()}
                    />
                    <Button onClick={handleSendText} disabled={!userInput.trim()}>
                      Send
                    </Button>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Note: Real-time audio via STT/TTS will be integrated from your audio_jam scripts
                  </p>
                </div>
                
                {/* Transcript */}
                {transcript.length > 0 && (
                  <div className="border rounded-lg p-4 max-h-64 overflow-y-auto">
                    <h3 className="font-semibold mb-2">Transcript:</h3>
                    <div className="space-y-2">
                      {transcript.map((entry, index) => (
                        <div key={index} className="text-sm">
                          <span className={`font-medium ${entry.speaker === 'interviewer' ? 'text-purple-600' : 'text-blue-600'}`}>
                            {entry.speaker === 'interviewer' ? 'Interviewer' : 'You'}:
                          </span>
                          <span className="ml-2">{entry.text}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="flex justify-end">
                  <Button onClick={endInterview} variant="destructive">
                    End Interview
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
