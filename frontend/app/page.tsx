'use client';

import { useState, useRef, useEffect } from 'react';
import ChatMessage from '@/components/ChatMessage';
import ChatInput from '@/components/ChatInput';
import SuggestedQuestions from '@/components/SuggestedQuestions';
import ThreadSidebar from '@/components/ThreadSidebar';
import { sendMessage, createThread, getThreadHistory, ChatMessage as ChatMessageType } from '@/lib/api';

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

  // Create new thread on first load
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

  const handleThreadSelect = async (selectedThreadId: string) => {
    try {
      const threadHistory = await getThreadHistory(selectedThreadId);
      setThreadId(selectedThreadId);
      setMessages(threadHistory.messages.map((msg) => ({
        role: msg.role,
        content: msg.content,
        source: msg.sources?.[0],
        sourceUrl: msg.sources?.[0],
      })));
    } catch (error) {
      console.error('Failed to load thread:', error);
    }
  };

  const handleThreadDelete = (deletedThreadId: string) => {
    if (threadId === deletedThreadId) {
      handleNewChat();
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
      const errorMessage: UIChatMessage = {
        role: 'assistant',
        content: error instanceof Error ? error.message : 'Sorry, I encountered an error. Please try again.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestedQuestion = (question: string) => {
    handleSendMessage(question);
  };

  return (
    <div className="flex min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500">
      {/* Sidebar */}
      <ThreadSidebar
        currentThreadId={threadId}
        onThreadSelect={handleThreadSelect}
        onNewChat={handleNewChat}
        onThreadDelete={handleThreadDelete}
      />

      {/* Main content */}
      <main className="flex-1 lg:ml-0">
        <div className="max-w-3xl mx-auto px-4 py-8 min-h-screen flex flex-col">
          {/* Header */}
          <header className="text-center mb-8 lg:pl-0 pl-12">
            <h1 className="text-3xl font-bold text-white mb-2">MF FAQ Assistant</h1>
            <p className="text-white/80">Your trusted mutual fund information companion</p>
          </header>

          {/* Disclaimer */}
          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6 rounded-r-lg">
            <p className="text-sm text-yellow-800">
              <span className="font-semibold">[!]</span>{' '}
              <strong>Facts-only. No investment advice.</strong> This chatbot provides factual information 
              from official AMC documents only. Always consult a financial advisor before making investment decisions.
            </p>
          </div>

          {/* Suggested Questions */}
          {messages.length === 0 && (
            <SuggestedQuestions onSelect={handleSuggestedQuestion} />
          )}

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto mb-6 space-y-4">
            {messages.map((message, index) => (
              <ChatMessage
                key={index}
                message={message}
                source={message.source}
                sourceUrl={message.sourceUrl}
              />
            ))}
            <div ref={messagesEndRef} />
          </div>

          {/* Chat Input */}
          <div className="sticky bottom-0 bg-white/10 backdrop-blur-md rounded-2xl p-4">
            <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
          </div>

          {/* Footer */}
          <footer className="text-center mt-6 text-white/60 text-sm">
            Powered by Groq LLM | Data from official AMC sources | Updated daily at 9:15 AM IST
          </footer>
        </div>
      </main>
    </div>
  );
}
