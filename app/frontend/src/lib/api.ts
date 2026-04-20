import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  timeout: 30000,
});

export interface ChatMessage {
  content: string;
  user_id?: string;
}

export interface ChatResponse {
  content: string;
  cost: number;
  remaining_budget: number;
  correlation_id?: string;
  warning?: string;
}

export interface MetricsResponse {
  helpful: number;
  unhelpful: number;
  escalated: number;
  total: number;
}

export interface HealthResponse {
  status: string;
  uptime_seconds: number;
  total_requests: number;
  error_count: number;
  error_rate: number;
}

export const chatApi = {
  sendMessage: (data: ChatMessage) => api.post<ChatResponse>('/chat', data),
  recordFeedback: (data: { type: 'helpful' | 'unhelpful' | 'escalated', target_id?: string, answer_content?: string }) => 
    api.post('/feedback', data),
  escalate: (data: Record<string, any>) => api.post('/escalate', data),
};

export const metricsApi = {
  getMetrics: () => api.get<MetricsResponse>('/metrics'),
  getHealth: () => api.get<HealthResponse>('/health'),
};
