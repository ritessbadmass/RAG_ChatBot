const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_URL = BASE_URL.replace(/\/$/, '');

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  sources?: string[];
}

export interface ChatResponse {
  answer: string;
  source?: string;
  source_url?: string;
  confidence?: number;
  thread_id: string;
  query_type?: string;
}

export interface Thread {
  id: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ThreadHistory {
  thread_id: string;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

export async function sendMessage(
  query: string, 
  threadId?: string,
  history: ChatMessage[] = []
): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      thread_id: threadId,
      history,
    }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to send message');
  }

  return response.json();
}

export async function createThread(): Promise<{ thread_id: string; created_at: string }> {
  const response = await fetch(`${API_URL}/chat/threads`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create thread');
  }

  return response.json();
}

export async function getThreadHistory(threadId: string): Promise<ThreadHistory> {
  const response = await fetch(`${API_URL}/chat/threads/${threadId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get thread history');
  }

  return response.json();
}

export async function listThreads(limit: number = 50): Promise<{ threads: Thread[]; total: number }> {
  const response = await fetch(`${API_URL}/chat/threads?limit=${limit}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to list threads');
  }

  return response.json();
}

export async function deleteThread(threadId: string): Promise<void> {
  const response = await fetch(`${API_URL}/chat/threads/${threadId}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete thread');
  }
}

export async function ingestData(): Promise<any> {
  const response = await fetch(`${API_URL}/admin/ingest`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to trigger ingestion');
  }

  return response.json();
}

export async function getIngestionStatus(): Promise<{ is_running: boolean; error: string | null; last_run: string | null }> {
  const response = await fetch(`${API_URL}/admin/ingest/status`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get ingestion status');
  }

  return response.json();
}
