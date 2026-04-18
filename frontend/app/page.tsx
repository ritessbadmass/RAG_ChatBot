'use client';

import { useState, useRef, useEffect } from 'react';
import ChatMessage from '@/components/ChatMessage';
import ChatInput from '@/components/ChatInput';
import SuggestedQuestions from '@/components/SuggestedQuestions';
import { sendMessage, createThread, ChatMessage as ChatMessageType } from '@/lib/api';

type UIChatMessage = ChatMessageType & { source?: string; sourceUrl?: string; };

export default function Home() {
  const [messages, setMessages] = useState<UIChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [threadId, setThreadId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    handleNewChat();
  }, []);

  const handleNewChat = async () => {
    try {
      const newThread = await createThread();
      setThreadId(newThread.thread_id);
      setMessages([]);
    } catch (error) {
      console.error('Failed to create thread:', error);
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!threadId) return;

    const userMessage: UIChatMessage = { role: 'user', content };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const history = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const response = await sendMessage(content, threadId, history);

      const assistantMessage: UIChatMessage = {
        role: 'assistant',
        content: response.answer,
      };

      setMessages((prev) => [
        ...prev,
        {
          ...assistantMessage,
          source: response.source,
          sourceUrl: response.source_url,
        },
      ]);
    } catch (error) {
      if (error instanceof Error && error.message.includes('not found')) {
        try {
          const newThread = await createThread();
          setThreadId(newThread.thread_id);
          const response = await sendMessage(content, newThread.thread_id, []);
          setMessages((prev) => [
            ...prev,
            {
              role: 'assistant',
              content: response.answer,
              source: response.source,
              sourceUrl: response.source_url,
            },
          ]);
          return;
        } catch (retryError) {
          console.error('Retry failed:', retryError);
        }
      }

      const errorMessage: UIChatMessage = {
        role: 'assistant',
        content: error instanceof Error ? error.message : 'Sorry, I encountered an error. Please try again.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex justify-center h-screen overflow-hidden bg-[var(--kuvera-bg)] relative">
      {/* Main content */}
      <main className="flex flex-col items-center justify-between w-full lg:px-8 px-4 relative max-h-screen">
        
        {/* Fresh Start Button */}
        <div className="absolute top-4 right-4 lg:top-8 lg:right-8 z-50">
          <button
            onClick={handleNewChat}
            className="flex items-center gap-2 px-4 py-2 bg-white text-[var(--kuvera-teal)] text-sm font-semibold rounded-full shadow-sm hover:shadow border border-[var(--kuvera-border)] transition-all active:scale-95"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Fresh Start
          </button>
        </div>
        
        {/* Top Header & Disclaimer */}
        <div className="w-full max-w-3xl pt-16 lg:pt-8 pb-4 bg-gradient-to-b from-[var(--kuvera-bg)] to-transparent sticky top-0 z-10 flex flex-col items-center">
          <div className="w-12 h-12 bg-[var(--kuvera-teal-light)] rounded-2xl flex items-center justify-center mb-4 shadow-sm">
            <svg className="w-6 h-6 text-[var(--kuvera-teal)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-[var(--kuvera-navy)] tracking-tight text-center">Mutual Fund Assistant</h1>
          <p className="text-[var(--kuvera-text-muted)] text-sm mb-6 text-center max-w-sm">Get instant, factual answers about expense ratios, NAVs, and fund details.</p>
          
          <div className="w-full bg-yellow-50 border border-yellow-200 rounded-lg p-3 mx-4">
            <p className="text-xs text-yellow-800 text-center flex items-center justify-center gap-2">
              <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <span><strong>Facts-only. No investment advice.</strong> Data sourced from official AMC documents.</span>
            </p>
          </div>
        </div>

        {/* Chat Area */}
        <div className="w-full max-w-3xl flex-1 overflow-y-auto pb-32 scroll-smooth px-2">
          {messages.length === 0 ? (
            <div className="mt-8">
              <SuggestedQuestions onSelect={handleSendMessage} />
            </div>
          ) : (
            <div className="space-y-6 pt-4">
              {messages.map((message, index) => (
                <ChatMessage
                  key={index}
                  message={message}
                  source={message.source}
                  sourceUrl={message.sourceUrl}
                />
              ))}
              <div ref={messagesEndRef} className="h-4" />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-[var(--kuvera-bg)] via-[var(--kuvera-bg)] to-transparent pt-10 pb-6 px-4 lg:px-8 flex justify-center items-center z-20 pointer-events-none">
          <div className="w-full max-w-3xl pointer-events-auto">
            <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
            <p className="text-[10px] text-[var(--kuvera-text-light)] text-center mt-3 tracking-wide uppercase">
              Powered by RAG • Data updated continuously
            </p>
          </div>
        </div>

      </main>
    </div>
  );
}
