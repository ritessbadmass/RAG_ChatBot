'use client';

import { useState, FormEvent } from 'react';

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading: boolean;
}

export default function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [input, setInput] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSend(input.trim());
      setInput('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative w-full">
      <div className="relative flex items-center w-full shadow-sm rounded-xl" style={{ border: '1px solid var(--kuvera-border)', background: 'var(--kuvera-surface)' }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about mutual funds..."
          disabled={isLoading}
          className="w-full px-5 py-4 bg-transparent text-sm focus:outline-none disabled:opacity-50 transition-all"
          style={{ color: 'var(--kuvera-text)' }}
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="mr-3 p-2 rounded-lg transition-all"
          style={{ 
            background: input.trim() ? 'var(--kuvera-teal)' : 'var(--kuvera-bg)',
            color: input.trim() ? '#fff' : 'var(--kuvera-text-light)',
            cursor: isLoading || !input.trim() ? 'not-allowed' : 'pointer'
          }}
        >
          {isLoading ? (
            <div className="w-5 h-5 border-2 border-t-transparent rounded-full animate-spin" style={{ borderColor: 'var(--kuvera-teal) transparent transparent transparent' }} />
          ) : (
            <svg className="w-5 h-5 translate-x-[1px] translate-y-[1px]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19V5m0 0l-7 7m7-7l7 7" />
            </svg>
          )}
        </button>
      </div>
    </form>
  );
}
