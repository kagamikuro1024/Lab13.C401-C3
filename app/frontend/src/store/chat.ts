import { create } from 'zustand';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  cost?: number;
  warning?: string;
  correlation_id?: string;
}

export interface ChatStore {
  messages: Message[];
  loading: boolean;
  error: string | null;
  userId: string;
  darkMode: boolean;
  
  setUserId: (id: string) => void;
  addMessage: (role: 'user' | 'assistant', content: string, cost?: number, warning?: string, correlation_id?: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearMessages: () => void;
  toggleDarkMode: () => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  loading: false,
  error: null,
  userId: '',
  darkMode: false,
  
  setUserId: (id) => set({ userId: id }),
  
  addMessage: (role, content, cost, warning, correlation_id) => set((state) => ({
    messages: [
      ...state.messages,
      {
        id: Date.now().toString(),
        role,
        content,
        timestamp: new Date(),
        cost,
        warning,
        correlation_id,
      },
    ],
  })),
  
  setLoading: (loading) => set({ loading }),
  
  setError: (error) => set({ error }),
  
  clearMessages: () => set({ messages: [] }),
  
  toggleDarkMode: () => set((state) => ({ darkMode: !state.darkMode })),
}));
