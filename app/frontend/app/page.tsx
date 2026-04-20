'use client';

import { useState, useEffect, useRef } from 'react';
import { Sidebar } from '@/components/Sidebar';
import { useChatStore } from '@/store/chat';
import { chatApi, metricsApi } from '@/lib/api';

export default function Home() {
  const [apiKey, setApiKey] = useState('');
  const [costInfo, setCostInfo] = useState({ spent: 0, budget: 1.0, warning: '' });
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const { messages, loading, addMessage, setLoading, setError, clearMessages, darkMode } = useChatStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    if (!content.trim() || loading) return;

    const userId = apiKey || 'anonymous';
    
    // Add user message
    addMessage('user', content);
    setLoading(true);
    setError(null);

    try {
      const response = await chatApi.sendMessage({
        content,
        user_id: userId,
      });

      // Add assistant message with correlation_id
      addMessage(
        'assistant', 
        response.data.content, 
        response.data.cost, 
        response.data.warning, 
        response.data.correlation_id
      );

      // Update cost info
      setCostInfo({
        spent: response.data.cost,
        budget: 1.0,
        warning: response.data.warning || '',
      });
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Có lỗi xảy ra';
      setError(errorMsg);
      addMessage('assistant', `❌ Lỗi: ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (messageIndex: number, type: 'helpful' | 'unhelpful' | 'escalated') => {
    const msg = messages[messageIndex];
    if (!msg || msg.role !== 'assistant') return;

    try {
      await chatApi.recordFeedback({ 
        type, 
        target_id: msg.correlation_id,
        answer_content: msg.content // Gửi kèm nội dung để Admin thấy trên Dashboard
      });
      // Reload metrics would happen automatically via polling
    } catch (err) {
      console.error('Failed to record feedback:', err);
    }
  };

  const bgColor = darkMode ? 'bg-dark-bg' : 'bg-light-bg';
  const textColor = darkMode ? 'text-dark-text' : 'text-light-text';
  const cardBg = darkMode ? 'bg-dark-secondary border-dark-border' : 'bg-light-card border-light-border';

  return (
    <div className={`flex h-screen ${bgColor}`}>
      {/* Sidebar */}
      <Sidebar 
        apiKey={apiKey}
        onApiKeyChange={setApiKey}
        costInfo={costInfo}
        onClearChat={clearMessages}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <div className={`${cardBg} border-b p-6 text-center`}>
          <h1 className={`text-3xl font-bold font-serif ${textColor}`}>AI Trợ Giảng</h1>
          <p className={`text-sm ${darkMode ? 'text-dark-text-secondary' : 'text-light-text-secondary'}`}>
            Hỗ trợ học tập Lập trình C/C++ với GPT-4
          </p>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center max-w-md">
                <p className={`text-2xl font-bold mb-3 ${darkMode ? 'text-dark-text-secondary' : 'text-light-text-secondary'}`}>
                  Xin chào! 👋
                </p>
                <p className={`text-sm ${darkMode ? 'text-dark-text-secondary' : 'text-light-text-secondary'} leading-relaxed`}>
                  Mình là AI Trợ Giảng cho khóa học <strong>Lập trình C/C++ cơ bản</strong>. 
                  <br /><br />
                  Mình có thể giúp bạn:
                  <br />📖 Giải thích kiến thức
                  <br />🐛 Debug code
                  <br />📋 Thông tin khóa học
                  <br />💡 Gợi ý bài tập
                  <br /><br />
                  Hãy gõ câu hỏi bên dưới! ✨
                </p>
              </div>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-lg px-4 py-3 rounded-lg ${
                    msg.role === 'user'
                      ? `${darkMode ? 'bg-accent' : 'bg-accent'} text-white`
                      : `${cardBg} ${textColor} border`
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                  {msg.cost !== undefined && (
                    <p className={`text-xs mt-2 ${msg.role === 'user' ? 'opacity-75' : darkMode ? 'text-dark-text-secondary' : 'text-light-text-secondary'}`}>
                      💰 ${msg.cost.toFixed(4)}
                    </p>
                  )}
                  {msg.warning && (
                    <p className={`text-xs mt-2 ${msg.role === 'user' ? '' : 'text-red-600'}`}>
                      {msg.warning}
                    </p>
                  )}
                  <p className={`text-xs mt-1 ${msg.role === 'user' ? 'opacity-75' : darkMode ? 'text-dark-text-secondary' : 'text-light-text-secondary'}`}>
                    {msg.timestamp.toLocaleTimeString('vi-VN')}
                  </p>
                </div>

                {/* Feedback Buttons */}
                {msg.role === 'assistant' && idx === messages.length - 1 && (
                  <div className="flex gap-2 ml-2 items-end">
                    <button
                      onClick={() => handleFeedback(idx, 'helpful')}
                      className={`px-2 py-1 rounded text-xs transition-colors ${
                        darkMode
                          ? 'bg-green-900 text-green-200 hover:bg-green-800'
                          : 'bg-green-100 text-green-700 hover:bg-green-200'
                      }`}
                    >
                      👍
                    </button>
                    <button
                      onClick={() => handleFeedback(idx, 'unhelpful')}
                      className={`px-2 py-1 rounded text-xs transition-colors ${
                        darkMode
                          ? 'bg-red-900 text-red-200 hover:bg-red-800'
                          : 'bg-red-100 text-red-700 hover:bg-red-200'
                      }`}
                    >
                      👎
                    </button>
                    <button
                      onClick={() => handleFeedback(idx, 'escalated')}
                      className={`px-2 py-1 rounded text-xs transition-colors ${
                        darkMode
                          ? 'bg-orange-900 text-orange-200 hover:bg-orange-800'
                          : 'bg-orange-100 text-orange-700 hover:bg-orange-200'
                      }`}
                    >
                      ⚠️
                    </button>
                  </div>
                )}
              </div>
            ))
          )}

          {loading && (
            <div className="flex justify-start">
              <div className={`${cardBg} px-4 py-3 rounded-lg border ${textColor}`}>
                <p className="text-sm animate-pulse">🤔 Đang suy nghĩ...</p>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <ChatInput onSendMessage={handleSendMessage} disabled={loading} darkMode={darkMode} />
      </div>
    </div>
  );
}

function ChatInput({ 
  onSendMessage, 
  disabled,
  darkMode,
}: { 
  onSendMessage: (msg: string) => void;
  disabled: boolean;
  darkMode: boolean;
}) {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onSendMessage(input);
      setInput('');
    }
  };

  const cardBg = darkMode ? 'bg-dark-secondary border-dark-border' : 'bg-light-card border-light-border';
  const textColor = darkMode ? 'text-dark-text' : 'text-light-text';

  return (
    <form onSubmit={handleSubmit} className={`${cardBg} border-t p-6 space-y-3`}>
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Hỏi mình bất cứ gì về C/C++..."
          disabled={disabled}
          className={`flex-1 px-4 py-2 rounded-lg border transition-colors ${
            darkMode
              ? 'bg-dark-bg border-dark-border text-dark-text placeholder-dark-text-secondary focus:border-accent'
              : 'bg-light-bg border-light-border text-light-text placeholder-light-text-secondary focus:border-accent'
          } focus:outline-none disabled:opacity-50`}
        />
        <button
          type="submit"
          disabled={disabled || !input.trim()}
          className="px-6 py-2 bg-accent text-white rounded-lg hover:bg-accent-hover disabled:bg-gray-400 transition font-medium"
        >
          Gửi
        </button>
      </div>
    </form>
  );
}
