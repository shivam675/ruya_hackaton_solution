import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { learningAPI, criticAPI } from '@/lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Brain, 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Target,
  Zap,
  BookOpen,
  BarChart3,
  Loader2,
  CheckCircle2,
  XCircle,
  FileEdit,
  ThumbsUp,
  ThumbsDown,
  Eye,
  Sparkles
} from 'lucide-react';

interface AgentMetrics {
  agent_type: string;
  version: string;
  total_actions: number;
  successful_actions: number;
  failed_actions: number;
  average_rating: number;
  improvement_rate: number;
  patterns_learned: number;
  last_improvement_at?: string;
}

export default function AgentLearning() {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [selectedImprovement, setSelectedImprovement] = useState<any | null>(null);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const queryClient = useQueryClient();

  const { data: allMetrics = [], isLoading: metricsLoading } = useQuery({
    queryKey: ['agent-metrics'],
    queryFn: () => learningAPI.getAllMetrics(),
  });

  const { data: insights, isLoading: insightsLoading } = useQuery({
    queryKey: ['agent-insights', selectedAgent],
    queryFn: () => learningAPI.getInsights(selectedAgent!),
    enabled: !!selectedAgent,
  });

  // Critic agent queries
  const { data: improvements = [], isLoading: improvementsLoading } = useQuery({
    queryKey: ['critic-improvements', selectedAgent],
    queryFn: () => criticAPI.listImprovements(selectedAgent || undefined),
    enabled: true,
  });

  // Mutations
  const evaluateMutation = useMutation({
    mutationFn: (agentType: string) => criticAPI.evaluateAgent(agentType, 10),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['critic-improvements'] });
      setIsEvaluating(false);
    },
    onError: () => {
      setIsEvaluating(false);
    },
  });

  const approveMutation = useMutation({
    mutationFn: (evaluationId: string) => criticAPI.approveImprovement(evaluationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['critic-improvements'] });
      setSelectedImprovement(null);
    },
  });

  const rejectMutation = useMutation({
    mutationFn: ({ evaluationId, reason }: { evaluationId: string; reason?: string }) =>
      criticAPI.rejectImprovement(evaluationId, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['critic-improvements'] });
      setSelectedImprovement(null);
    },
  });

  const handleEvaluateAgent = (agentType: string) => {
    setIsEvaluating(true);
    evaluateMutation.mutate(agentType);
  };

  const handleApprove = (evaluationId: string) => {
    if (confirm('Are you sure you want to approve and apply this improved prompt?')) {
      approveMutation.mutate(evaluationId);
    }
  };

  const handleReject = (evaluationId: string) => {
    const reason = prompt('Optional: Provide a reason for rejection');
    rejectMutation.mutate({ evaluationId, reason: reason || undefined });
  };

  const agentTypes = [
    { id: 'cv_shortlisting', name: 'CV Shortlisting Agent', icon: '📄', color: 'blue' },
    { id: 'interview', name: 'Interview Agent', icon: '🎤', color: 'purple' },
    { id: 'email_scheduling', name: 'Email Agent', icon: '📧', color: 'green' },
    { id: 'hr_chat', name: 'HR Chat Agent', icon: '💬', color: 'orange' },
  ];

  const getSuccessRate = (metrics: AgentMetrics) => {
    if (!metrics.total_actions) return 0;
    return ((metrics.successful_actions / metrics.total_actions) * 100).toFixed(1);
  };

  if (metricsLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-purple-600" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
            <Brain className="h-8 w-8 text-purple-600" />
            Agent Self-Learning Dashboard
          </h2>
          <p className="text-gray-600 mt-1">
            Real-time tracking of AI agents learning and improving autonomously
          </p>
        </div>
        <Badge variant="default" className="bg-gradient-to-r from-purple-500 to-blue-500">
          <Zap className="h-3 w-3 mr-1" />
          Auto-Learning Enabled
        </Badge>
      </div>

      {/* Overview Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {agentTypes.map((agentType) => {
          const metrics = allMetrics.find((m: AgentMetrics) => m.agent_type === agentType.id);
          const successRate = metrics ? getSuccessRate(metrics) : 0;
          const improvementRate = metrics?.improvement_rate || 0;

          return (
            <Card
              key={agentType.id}
              className={`cursor-pointer transition-all hover:shadow-lg ${
                selectedAgent === agentType.id ? 'ring-2 ring-purple-500' : ''
              }`}
              onClick={() => setSelectedAgent(agentType.id)}
            >
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <span className="text-2xl">{agentType.icon}</span>
                      {agentType.name}
                    </CardTitle>
                    <CardDescription className="mt-1">
                      v{metrics?.version || '1.0.0'}
                    </CardDescription>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Success Rate</span>
                  <Badge variant="outline" className="font-semibold">
                    {successRate}%
                  </Badge>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Improvement</span>
                  <div className="flex items-center gap-1">
                    {improvementRate > 0 ? (
                      <TrendingUp className="h-4 w-4 text-green-600" />
                    ) : improvementRate < 0 ? (
                      <TrendingDown className="h-4 w-4 text-red-600" />
                    ) : (
                      <Activity className="h-4 w-4 text-gray-400" />
                    )}
                    <span className={`text-sm font-semibold ${
                      improvementRate > 0 ? 'text-green-600' : 
                      improvementRate < 0 ? 'text-red-600' : 'text-gray-600'
                    }`}>
                      {improvementRate > 0 ? '+' : ''}{improvementRate.toFixed(1)}%
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Patterns Learned</span>
                  <Badge variant="secondary">
                    <BookOpen className="h-3 w-3 mr-1" />
                    {metrics?.patterns_learned || 0}
                  </Badge>
                </div>

                <div className="pt-2 border-t">
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>{metrics?.total_actions || 0} actions</span>
                    <span>★ {metrics?.average_rating?.toFixed(1) || '0.0'}/5</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Detailed Insights */}
      {selectedAgent && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Detailed Learning Insights: {agentTypes.find(a => a.id === selectedAgent)?.name}
            </CardTitle>
            <CardDescription>
              Deep dive into what this agent has learned and how it's improving
            </CardDescription>
          </CardHeader>
          <CardContent>
            {insightsLoading ? (
              <div className="flex items-center justify-center py-8">
                <Loader2 className="h-6 w-6 animate-spin text-purple-600" />
              </div>
            ) : insights ? (
              <div className="space-y-6">
                {/* Learning State */}
                <div>
                  <h3 className="font-semibold mb-3 flex items-center gap-2">
                    <Target className="h-4 w-4" />
                    Learning Configuration
                  </h3>
                  <div className="grid gap-3 md:grid-cols-3">
                    <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
                      {insights.learning_state.learning_enabled ? (
                        <CheckCircle2 className="h-5 w-5 text-green-600" />
                      ) : (
                        <XCircle className="h-5 w-5 text-red-600" />
                      )}
                      <div>
                        <div className="text-sm font-medium">Learning Enabled</div>
                        <div className="text-xs text-gray-600">
                          {insights.learning_state.learning_enabled ? 'Active' : 'Disabled'}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
                      {insights.learning_state.auto_adapt ? (
                        <Zap className="h-5 w-5 text-purple-600" />
                      ) : (
                        <XCircle className="h-5 w-5 text-gray-400" />
                      )}
                      <div>
                        <div className="text-sm font-medium">Auto-Adapt</div>
                        <div className="text-xs text-gray-600">
                          {insights.learning_state.auto_adapt ? 'Enabled' : 'Manual'}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
                      <Activity className="h-5 w-5 text-blue-600" />
                      <div>
                        <div className="text-sm font-medium">Exploration Rate</div>
                        <div className="text-xs text-gray-600">
                          {(insights.learning_state.exploration_rate * 100).toFixed(0)}% trying new approaches
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Performance Metrics */}
                <div>
                  <h3 className="font-semibold mb-3 flex items-center gap-2">
                    <BarChart3 className="h-4 w-4" />
                    Performance Metrics
                  </h3>
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                    <div className="p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
                      <div className="text-2xl font-bold text-blue-700">
                        {insights.metrics.total_actions}
                      </div>
                      <div className="text-sm text-blue-600">Total Actions</div>
                    </div>

                    <div className="p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-lg">
                      <div className="text-2xl font-bold text-green-700">
                        {insights.metrics.successful_actions}
                      </div>
                      <div className="text-sm text-green-600">Successful</div>
                    </div>

                    <div className="p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
                      <div className="text-2xl font-bold text-purple-700">
                        {insights.metrics.average_rating.toFixed(2)}
                      </div>
                      <div className="text-sm text-purple-600">Avg Rating</div>
                    </div>

                    <div className="p-4 bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg">
                      <div className="text-2xl font-bold text-orange-700">
                        {insights.metrics.patterns_learned}
                      </div>
                      <div className="text-sm text-orange-600">Patterns Learned</div>
                    </div>
                  </div>
                </div>

                {/* Top Learned Patterns */}
                <div>
                  <h3 className="font-semibold mb-3 flex items-center gap-2">
                    <BookOpen className="h-4 w-4" />
                    Top Learned Patterns ({insights.top_patterns.length})
                  </h3>
                  <div className="space-y-2">
                    {insights.top_patterns.slice(0, 5).map((pattern: any, index: number) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <Badge variant="outline">#{index + 1}</Badge>
                          <div>
                            <div className="font-medium text-sm">
                              {pattern.pattern_type.replace('_', ' ').toUpperCase()}
                            </div>
                            <div className="text-xs text-gray-600">
                              Used {pattern.usage_count} times
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge 
                            variant={pattern.success_rate > 0.7 ? 'default' : 'secondary'}
                            className={pattern.success_rate > 0.7 ? 'bg-green-600' : ''}
                          >
                            {(pattern.success_rate * 100).toFixed(0)}% success
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recent Activity */}
                <div className="flex items-center justify-between p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg">
                  <div>
                    <div className="font-semibold">Recent Feedback</div>
                    <div className="text-sm text-gray-600">
                      {insights.recent_feedback_count} feedback items in the last period
                    </div>
                  </div>
                  <Badge
                    variant="outline"
                    className={`${
                      insights.performance_trend === 'improving'
                        ? 'border-green-500 text-green-700 bg-green-50'
                        : 'border-orange-500 text-orange-700 bg-orange-50'
                    }`}
                  >
                    <TrendingUp className="h-3 w-3 mr-1" />
                    {insights.performance_trend}
                  </Badge>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-600">
                No insights available yet. The agent needs more data to learn.
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Critic Agent - Prompt Improvements */}
      <Card className="border-2 border-purple-200">
        <CardHeader className="bg-gradient-to-r from-purple-50 to-blue-50">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-purple-600" />
                Critic Agent - Prompt Improvements
              </CardTitle>
              <CardDescription>
                AI-powered system prompt optimization based on performance analysis
              </CardDescription>
            </div>
            {selectedAgent && (
              <Button
                onClick={() => handleEvaluateAgent(selectedAgent)}
                disabled={isEvaluating || evaluateMutation.isPending}
                className="bg-gradient-to-r from-purple-600 to-blue-600"
              >
                {isEvaluating || evaluateMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Evaluating...
                  </>
                ) : (
                  <>
                    <FileEdit className="h-4 w-4 mr-2" />
                    Evaluate {agentTypes.find(a => a.id === selectedAgent)?.name}
                  </>
                )}
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent className="pt-6">
          {improvementsLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-purple-600" />
            </div>
          ) : improvements.length === 0 ? (
            <div className="text-center py-8">
              <Sparkles className="h-12 w-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-600">
                No prompt improvements yet. Click "Evaluate Agent" to analyze performance and get suggestions.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Filter Tabs */}
              <div className="flex gap-2 border-b pb-2">
                <Button
                  variant={!selectedAgent ? 'default' : 'ghost'}
                  size="sm"
                  onClick={() => setSelectedAgent(null)}
                >
                  All Agents
                </Button>
                {agentTypes.map(agent => (
                  <Button
                    key={agent.id}
                    variant={selectedAgent === agent.id ? 'default' : 'ghost'}
                    size="sm"
                    onClick={() => setSelectedAgent(agent.id)}
                  >
                    {agent.icon} {agent.name.split(' ')[0]}
                  </Button>
                ))}
              </div>

              {/* Improvements List */}
              <div className="space-y-3">
                {improvements
                  .filter((imp: any) => !selectedAgent || imp.agent_type === selectedAgent)
                  .map((improvement: any) => (
                    <Card
                      key={improvement.evaluation_id}
                      className={`cursor-pointer transition-all ${
                        selectedImprovement?.evaluation_id === improvement.evaluation_id
                          ? 'ring-2 ring-purple-500'
                          : 'hover:shadow-md'
                      }`}
                      onClick={() =>
                        setSelectedImprovement(
                          selectedImprovement?.evaluation_id === improvement.evaluation_id
                            ? null
                            : improvement
                        )
                      }
                    >
                      <CardContent className="pt-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <span className="text-xl">
                                {agentTypes.find(a => a.id === improvement.agent_type)?.icon}
                              </span>
                              <h4 className="font-semibold">
                                {agentTypes.find(a => a.id === improvement.agent_type)?.name}
                              </h4>
                              <Badge
                                variant={
                                  improvement.status === 'approved'
                                    ? 'default'
                                    : improvement.status === 'rejected'
                                    ? 'destructive'
                                    : 'secondary'
                                }
                                className={
                                  improvement.status === 'approved'
                                    ? 'bg-green-600'
                                    : improvement.status === 'rejected'
                                    ? 'bg-red-600'
                                    : 'bg-yellow-600'
                                }
                              >
                                {improvement.status.replace('_', ' ')}
                              </Badge>
                              <Badge variant="outline">
                                Score: {improvement.evaluation_score}/10
                              </Badge>
                            </div>

                            <p className="text-sm text-gray-600 mb-2">
                              <strong>Improvement Reasoning:</strong> {improvement.improvement_reasoning}
                            </p>

                            <div className="flex flex-wrap gap-1 mb-2">
                              {improvement.issues_identified?.slice(0, 3).map((issue: string, idx: number) => (
                                <Badge key={idx} variant="outline" className="text-xs">
                                  ⚠️ {issue}
                                </Badge>
                              ))}
                            </div>

                            <div className="text-xs text-gray-500">
                              {new Date(improvement.timestamp).toLocaleString()} •{' '}
                              Avg Rating: {improvement.performance_metrics?.avg_feedback_rating?.toFixed(1) || 'N/A'}/5 •{' '}
                              Success Rate: {((improvement.performance_metrics?.success_rate || 0) * 100).toFixed(0)}%
                            </div>

                            {/* Expanded View */}
                            {selectedImprovement?.evaluation_id === improvement.evaluation_id && (
                              <div className="mt-4 space-y-4 border-t pt-4">
                                {/* Issues Identified */}
                                <div>
                                  <h5 className="font-semibold text-sm mb-2">Issues Identified:</h5>
                                  <ul className="list-disc list-inside space-y-1">
                                    {improvement.issues_identified?.map((issue: string, idx: number) => (
                                      <li key={idx} className="text-sm text-gray-700">
                                        {issue}
                                      </li>
                                    ))}
                                  </ul>
                                </div>

                                {/* Expected Improvements */}
                                <div>
                                  <h5 className="font-semibold text-sm mb-2">Expected Improvements:</h5>
                                  <ul className="list-disc list-inside space-y-1">
                                    {improvement.expected_improvements?.map((exp: string, idx: number) => (
                                      <li key={idx} className="text-sm text-green-700">
                                        {exp}
                                      </li>
                                    ))}
                                  </ul>
                                </div>

                                {/* Side-by-Side Prompt Comparison */}
                                <div>
                                  <h5 className="font-semibold text-sm mb-2">Prompt Comparison:</h5>
                                  <div className="grid md:grid-cols-2 gap-4">
                                    {/* Previous Prompt */}
                                    <div className="border rounded-lg p-3 bg-red-50">
                                      <div className="flex items-center gap-2 mb-2">
                                        <XCircle className="h-4 w-4 text-red-600" />
                                        <span className="font-semibold text-sm text-red-900">
                                          Previous Prompt
                                        </span>
                                      </div>
                                      <pre className="text-xs bg-white p-2 rounded border overflow-auto max-h-60 whitespace-pre-wrap">
                                        {improvement.current_prompt}
                                      </pre>
                                    </div>

                                    {/* Improved Prompt */}
                                    <div className="border rounded-lg p-3 bg-green-50">
                                      <div className="flex items-center gap-2 mb-2">
                                        <CheckCircle2 className="h-4 w-4 text-green-600" />
                                        <span className="font-semibold text-sm text-green-900">
                                          Improved Prompt
                                        </span>
                                      </div>
                                      <pre className="text-xs bg-white p-2 rounded border overflow-auto max-h-60 whitespace-pre-wrap">
                                        {improvement.improved_prompt}
                                      </pre>
                                    </div>
                                  </div>
                                </div>

                                {/* Action Buttons */}
                                {improvement.status === 'pending_review' && (
                                  <div className="flex gap-2 justify-end">
                                    <Button
                                      variant="outline"
                                      size="sm"
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        handleReject(improvement.evaluation_id);
                                      }}
                                      disabled={rejectMutation.isPending}
                                      className="border-red-300 text-red-700 hover:bg-red-50"
                                    >
                                      <ThumbsDown className="h-4 w-4 mr-1" />
                                      Reject
                                    </Button>
                                    <Button
                                      size="sm"
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        handleApprove(improvement.evaluation_id);
                                      }}
                                      disabled={approveMutation.isPending}
                                      className="bg-green-600 hover:bg-green-700"
                                    >
                                      <ThumbsUp className="h-4 w-4 mr-1" />
                                      Approve & Apply
                                    </Button>
                                  </div>
                                )}

                                {improvement.status === 'approved' && (
                                  <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                                    <div className="flex items-center gap-2 text-green-800 text-sm">
                                      <CheckCircle2 className="h-4 w-4" />
                                      <span>
                                        Approved and applied on {new Date(improvement.approved_at).toLocaleString()}
                                      </span>
                                    </div>
                                  </div>
                                )}

                                {improvement.status === 'rejected' && (
                                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                                    <div className="flex items-center gap-2 text-red-800 text-sm">
                                      <XCircle className="h-4 w-4" />
                                      <span>
                                        Rejected on {new Date(improvement.rejected_at).toLocaleString()}
                                        {improvement.rejection_reason && `: ${improvement.rejection_reason}`}
                                      </span>
                                    </div>
                                  </div>
                                )}
                              </div>
                            )}
                          </div>

                          <Eye className="h-4 w-4 text-gray-400 ml-2" />
                        </div>
                      </CardContent>
                    </Card>
                  ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* How It Works */}
      <Card className="bg-gradient-to-br from-purple-50 to-blue-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            How Self-Learning Works
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <div className="space-y-2">
              <div className="w-10 h-10 bg-purple-600 text-white rounded-lg flex items-center justify-center font-bold">
                1
              </div>
              <h4 className="font-semibold">Collect Feedback</h4>
              <p className="text-sm text-gray-600">
                System records outcomes of every agent action (hired candidates, interview quality, etc.)
              </p>
            </div>

            <div className="space-y-2">
              <div className="w-10 h-10 bg-blue-600 text-white rounded-lg flex items-center justify-center font-bold">
                2
              </div>
              <h4 className="font-semibold">Extract Patterns</h4>
              <p className="text-sm text-gray-600">
                AI analyzes successful vs failed actions to identify what works and what doesn't
              </p>
            </div>

            <div className="space-y-2">
              <div className="w-10 h-10 bg-green-600 text-white rounded-lg flex items-center justify-center font-bold">
                3
              </div>
              <h4 className="font-semibold">Auto-Adapt</h4>
              <p className="text-sm text-gray-600">
                Agents automatically apply learned patterns to improve future performance
              </p>
            </div>

            <div className="space-y-2">
              <div className="w-10 h-10 bg-orange-600 text-white rounded-lg flex items-center justify-center font-bold">
                4
              </div>
              <h4 className="font-semibold">Continuous Evolution</h4>
              <p className="text-sm text-gray-600">
                Prompts and behaviors evolve over time, getting better with each interaction
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
