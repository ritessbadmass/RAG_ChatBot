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
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[80%] rounded-2xl px-6 py-4 ${
          isUser
            ? 'bg-primary-600 text-white rounded-br-md'
            : 'bg-white text-gray-800 rounded-bl-md shadow-md'
        }`}
      >
        <p className="text-sm leading-relaxed">{message.content}</p>
        
        {!isUser && source && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            <a
              href={sourceUrl || '#'}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center text-xs text-primary-600 hover:text-primary-700 transition-colors"
            >
              <span className="mr-1">[DOC]</span>
              <span>{source}</span>
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
