'use client';

import { ChatMessage as ChatMessageType } from '@/lib/api';

interface ChatMessageProps {
  message: ChatMessageType;
  source?: string;
  sourceUrl?: string;
}

export default function ChatMessage({ message, source, sourceUrl }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3 message-enter`}>
      {/* Bot avatar */}
      {!isUser && (
        <div
          className="flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center mr-2.5 mt-1"
          style={{ background: 'var(--kuvera-teal-light)' }}
        >
          <svg className="w-3.5 h-3.5" style={{ color: 'var(--kuvera-teal)' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
      )}

      <div
        className="max-w-[75%] px-4 py-3"
        style={{
          background: isUser ? 'var(--kuvera-teal)' : 'var(--kuvera-surface)',
          color: isUser ? '#FFFFFF' : 'var(--kuvera-text)',
          borderRadius: isUser ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
          boxShadow: isUser ? 'none' : 'var(--shadow-sm)',
          border: isUser ? 'none' : '1px solid var(--kuvera-border)',
        }}
      >
        <p className="text-sm leading-relaxed whitespace-pre-line">{message.content}</p>

        {!isUser && source && (
          <div className="mt-2.5 pt-2.5" style={{ borderTop: '1px solid var(--kuvera-border)' }}>
            <a
              href={sourceUrl || '#'}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs transition-opacity hover:opacity-80"
              style={{ color: 'var(--kuvera-teal)' }}
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
              </svg>
              <span>View Source</span>
            </a>
          </div>
        )}
      </div>

      {/* User avatar */}
      {isUser && (
        <div
          className="flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center ml-2.5 mt-1"
          style={{ background: 'var(--kuvera-navy)', color: '#fff' }}
        >
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
      )}
    </div>
  );
}
