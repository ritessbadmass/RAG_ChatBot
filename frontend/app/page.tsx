'use client';

import { useState, useRef, useEffect } from 'react';
import ChatMessage from '@/components/ChatMessage';
import ChatInput from '@/components/ChatInput';
import SuggestedQuestions from '@/components/SuggestedQuestions';
import KuveraHeader from '@/components/KuveraHeader';
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
    <div className="flex flex-col h-screen overflow-hidden bg-[var(--kuvera-bg)]">
      {/* Kuvera Global Navigation */}
      <KuveraHeader />

      {/* Main content */}
      <main className="flex-1 flex flex-col w-full max-w-5xl mx-auto relative overflow-hidden bg-white shadow-sm border-x border-[var(--kuvera-border)]">
        
        {/* App Context Sub-header */}
        <div className="w-full flex items-center justify-between py-4 px-6 border-b border-[var(--kuvera-border)] bg-[var(--kuvera-surface)] sticky top-0 z-20 shrink-0">
          <div>
            <h1 className="text-lg font-bold tracking-tight text-[var(--kuvera-navy)] flex items-center gap-2">
              <span className="w-6 h-6 rounded-md bg-[var(--kuvera-teal-light)] flex items-center justify-center">
                <svg className="w-3.5 h-3.5 text-[var(--kuvera-teal)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                   <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </span>
              AI Fact Assistant
            </h1>
            <p className="text-xs text-[var(--kuvera-text-muted)] mt-1">Official AMC data only. No investment advice.</p>
          </div>
          <button
            onClick={handleNewChat}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-[var(--kuvera-bg)] text-[var(--kuvera-navy)] text-xs font-semibold rounded-md hover:bg-gray-100 border border-[var(--kuvera-border)] transition-all active:scale-95"
          >
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Clear Chat
          </button>
        </div>

        {/* Chat Area Container */}
        <div className="flex-1 overflow-y-auto scroll-smooth px-4 sm:px-8 pt-6 pb-40 flex flex-col items-center w-full">
          <div className="w-full max-w-3xl">
            {messages.length === 0 ? (
              <div className="mt-4">
                <SuggestedQuestions onSelect={handleSendMessage} />
              </div>
            ) : (
              <div className="space-y-6">
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
        </div>

        {/* Input Area */}
        <div className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-white via-white to-transparent pt-12 pb-6 px-4 md:px-8 flex justify-center items-center z-30 pointer-events-none">
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
