'use client';

import { useState, useRef, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import ChatMessage from '@/components/ChatMessage';
import ChatInput from '@/components/ChatInput';
import SuggestedQuestions from '@/components/SuggestedQuestions';
import { sendMessage, ChatMessage as ChatMessageType } from '@/lib/api';

export default function Home() {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [threadId] = useState(() => uuidv4());
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    const userMessage: ChatMessageType = { role: 'user', content };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const history = messages.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const response = await sendMessage(content, history);

      const assistantMessage: ChatMessageType = {
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
      const errorMessage: ChatMessageType = {
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
    <main className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500">
      <div className="max-w-3xl mx-auto px-4 py-8 min-h-screen flex flex-col">
        {/* Header */}
        <header className="text-center mb-8">
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
  );
}
