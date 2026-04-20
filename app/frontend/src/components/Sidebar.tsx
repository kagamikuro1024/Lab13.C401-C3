'use client';

import { useState, useEffect } from 'react';
import { Moon, Sun } from 'lucide-react';
import { useChatStore, type Message } from '@/store/chat';
import { metricsApi, type MetricsResponse, type HealthResponse } from '@/lib/api';

interface SidebarProps {
  apiKey: string;
  onApiKeyChange: (key: string) => void;
  costInfo: { spent: number; budget: number; warning: string };
  onClearChat: () => void;
}

export function Sidebar({ apiKey, onApiKeyChange, costInfo, onClearChat }: SidebarProps) {
  const { darkMode, toggleDarkMode, messages } = useChatStore();
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);

  useEffect(() => {
    const loadMetrics = async () => {
      try {
        const [metricsRes, healthRes] = await Promise.all([
          metricsApi.getMetrics(),
          metricsApi.getHealth(),
        ]);
        setMetrics(metricsRes.data);
        setHealth(healthRes.data);
      } catch (err) {
        console.error('Failed to load metrics:', err);
      }
    };

    loadMetrics();
    const interval = setInterval(loadMetrics, 10000);
    return () => clearInterval(interval);
  }, []);

  const bgColor = darkMode ? 'bg-dark-secondary border-dark-border' : 'bg-light-card border-light-border';
  const textColor = darkMode ? 'text-dark-text' : 'text-light-text';
  const textSecondary = darkMode ? 'text-dark-text-secondary' : 'text-light-text-secondary';

  const quickQuestions = [
    '🔧 Cách cài đặt gcc trên Windows?',
    '📝 Con trỏ trong C là gì?',
    '🐛 Segmentation fault là lỗi gì?',
    '📅 Lịch thi cuối kỳ khi nào?',
    '💻 Cho em xem code mẫu vòng lặp for',
  ];

  return (
    <div className={`w-64 ${darkMode ? 'bg-dark-bg border-dark-border' : 'bg-light-secondary border-light-border'} border-r h-screen overflow-y-auto flex flex-col`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-300 dark:border-gray-700">
        <h1 className={`text-2xl font-bold ${darkMode ? 'text-accent' : 'text-accent'}`}>🎓</h1>
        <p className={`text-sm ${textSecondary}`}>AI Trợ Giảng</p>
      </div>

      {/* Theme Toggle */}
      <div className="p-4">
        <button
          onClick={toggleDarkMode}
          className={`w-full flex items-center justify-center gap-2 py-2 px-3 rounded-lg border transition-colors ${
            darkMode 
              ? 'border-dark-border text-dark-text hover:border-accent' 
              : 'border-light-border text-light-text hover:border-accent'
          }`}
        >
          {darkMode ? (
            <>
              <Sun size={16} />
              <span className="text-sm">Chế độ sáng</span>
            </>
          ) : (
            <>
              <Moon size={16} />
              <span className="text-sm">Chế độ tối</span>
            </>
          )}
        </button>
      </div>

      {/* Security Section */}
      <div className="px-4 py-6 border-t border-gray-300 dark:border-gray-700">
        <h3 className={`text-sm font-semibold uppercase tracking-wide mb-4 ${textSecondary}`}>🔐 Kiểm soát truy cập</h3>
        
        <input
          type="password"
          value={apiKey}
          onChange={(e) => onApiKeyChange(e.target.value)}
          placeholder="Nhập API key..."
          className={`w-full px-3 py-2 rounded-lg border text-sm mb-4 ${
            darkMode
              ? 'bg-dark-bg border-dark-border text-dark-text'
              : 'bg-white border-light-border text-light-text'
          } focus:border-accent outline-none`}
        />

        {/* Rate Limit */}
        <div className="space-y-3 mb-4">
          <div className={`p-3 rounded-lg ${bgColor}`}>
            <p className={`text-xs ${textSecondary} mb-1`}>Requests còn lại</p>
            <p className={`text-lg font-bold ${textColor}`}>20/20</p>
          </div>
          <div className={`p-3 rounded-lg ${bgColor}`}>
            <p className={`text-xs ${textSecondary} mb-1`}>Sử dụng</p>
            <p className={`text-lg font-bold ${textColor}`}>0%</p>
          </div>
        </div>

        {/* Cost Guard */}
        <p className={`text-sm font-semibold mb-2 ${textColor}`}>💰 Budget hôm nay</p>
        <div className="space-y-2 mb-4">
          <div className={`p-3 rounded-lg ${bgColor} text-center`}>
            <p className={`text-xs ${textSecondary}`}>Cá nhân</p>
            <p className={`text-sm font-bold ${textColor}`}>${costInfo.spent.toFixed(4)}</p>
            <p className={`text-xs ${textSecondary}`}>/ ${costInfo.budget.toFixed(2)}</p>
          </div>
          <div className={`p-3 rounded-lg ${bgColor} text-center`}>
            <p className={`text-xs ${textSecondary}`}>Toàn bộ</p>
            <p className={`text-sm font-bold ${textColor}`}>$0.0000</p>
            <p className={`text-xs ${textSecondary}`}>/ $10.00</p>
          </div>
        </div>

        {/* Health Status */}
        {health && (
          <div className="space-y-2">
            <p className={`text-sm font-semibold ${textColor}`}>📊 Trạng thái</p>
            <div className={`p-3 rounded-lg ${bgColor} text-center`}>
              <p className={`text-sm font-bold ${health.status === 'healthy' ? 'text-green-600' : 'text-yellow-600'}`}>
                {health.status === 'healthy' ? '✅ Healthy' : '⚠️ Degraded'}
              </p>
              <p className={`text-xs ${textSecondary} mt-1`}>Uptime: {Math.floor(health.uptime_seconds)}s</p>
            </div>
          </div>
        )}
      </div>

      {/* Metrics */}
      {metrics && (
        <div className={`px-4 py-6 border-t border-gray-300 dark:border-gray-700`}>
          <h3 className={`text-sm font-semibold uppercase tracking-wide mb-4 ${textSecondary}`}>📊 Thống kê Agent</h3>
          <div className="grid grid-cols-3 gap-2">
            <div className={`p-3 rounded-lg ${bgColor} text-center`}>
              <p className="text-lg font-bold text-green-600">👍</p>
              <p className={`text-sm font-bold ${textColor}`}>{metrics.helpful}</p>
            </div>
            <div className={`p-3 rounded-lg ${bgColor} text-center`}>
              <p className="text-lg font-bold text-red-600">👎</p>
              <p className={`text-sm font-bold ${textColor}`}>{metrics.unhelpful}</p>
            </div>
            <div className={`p-3 rounded-lg ${bgColor} text-center`}>
              <p className="text-lg font-bold text-orange-600">⚠️</p>
              <p className={`text-sm font-bold ${textColor}`}>{metrics.escalated}</p>
            </div>
          </div>
          <p className={`text-center text-xs ${textSecondary} mt-3`}>
            Tổng: <span className={textColor}>{metrics.total}</span>
          </p>
        </div>
      )}

      {/* Course Info */}
      <div className={`px-4 py-6 border-t border-gray-300 dark:border-gray-700 space-y-3`}>
        <div className={`p-3 rounded-lg ${bgColor}`}>
          <h4 className={`text-sm font-semibold mb-2 ${textColor}`}>📚 Khóa học</h4>
          <p className={`text-xs ${textColor} font-semibold`}>Lập trình C/C++ cơ bản</p>
          <p className={`text-xs ${textSecondary}`}>Mã: CS101 | HK2 2025-2026</p>
          <p className={`text-xs ${textSecondary}`}>GV: ThS. Nguyễn Văn Minh</p>
        </div>

        <div className={`p-3 rounded-lg ${bgColor}`}>
          <h4 className={`text-sm font-semibold mb-2 ${textColor}`}>📅 Lịch học</h4>
          <p className={`text-xs ${textSecondary}`}>🏫 Lý thuyết: T3, 8:00-10:00</p>
          <p className={`text-xs ${textSecondary}`}>💻 Thực hành: T5, 13:00-16:00</p>
        </div>

        <div className={`p-3 rounded-lg ${bgColor}`}>
          <h4 className={`text-sm font-semibold mb-2 ${textColor}`}>👩‍💼 Trợ giảng</h4>
          <p className={`text-xs ${textColor} font-semibold`}>Trần Thị Hoa (chính)</p>
          <p className={`text-xs ${textSecondary}`}>T2-T6: 18:00-21:00</p>
          <p className={`text-xs ${textColor} font-semibold mt-2`}>Lê Minh Tuấn (phụ)</p>
          <p className={`text-xs ${textSecondary}`}>T7: 9:00-12:00</p>
        </div>
      </div>

      {/* Quick Questions */}
      <div className={`px-4 py-6 border-t border-gray-300 dark:border-gray-700`}>
        <h3 className={`text-sm font-semibold uppercase tracking-wide mb-3 ${textSecondary}`}>💡 Câu hỏi mẫu</h3>
        <div className="space-y-2">
          {quickQuestions.map((q) => (
            <button
              key={q}
              className={`w-full text-left text-xs p-2 rounded border transition-colors ${
                darkMode
                  ? 'border-dark-border text-dark-text hover:border-accent hover:text-accent'
                  : 'border-light-border text-light-text hover:border-accent hover:text-accent'
              }`}
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* New Chat Button */}
      <div className="px-4 py-4 border-t border-gray-300 dark:border-gray-700">
        <button
          onClick={onClearChat}
          className="w-full py-2 px-3 bg-accent text-white rounded-lg hover:bg-accent-hover transition font-medium text-sm"
        >
          ➕ Đoạn chat mới
        </button>
      </div>

      {/* Footer */}
      <div className={`px-4 py-4 border-t border-gray-300 dark:border-gray-700 text-center text-xs ${textSecondary} opacity-50`}>
        <p>Powered by GPT-4o-mini</p>
        <p>+ LangGraph</p>
        <p className="mt-1">© 2026 AI TA</p>
      </div>
    </div>
  );
}
