'use client';

import { useState, useEffect } from 'react';
import { Thread, listThreads, deleteThread } from '@/lib/api';

interface ThreadSidebarProps {
  currentThreadId: string | null;
  onThreadSelect: (threadId: string) => void;
  onNewChat: () => void;
  onThreadDelete: (threadId: string) => void;
}

export default function ThreadSidebar({
  currentThreadId,
  onThreadSelect,
  onNewChat,
  onThreadDelete,
}: ThreadSidebarProps) {
  const [threads, setThreads] = useState<Thread[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    loadThreads();
  }, []);

  const loadThreads = async () => {
    setIsLoading(true);
    try {
      const response = await listThreads(20);
      setThreads(response.threads);
    } catch (error) {
      console.error('Failed to load threads:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (e: React.MouseEvent, threadId: string) => {
    e.stopPropagation();
    if (confirm('Delete this conversation?')) {
      try {
        await deleteThread(threadId);
        onThreadDelete(threadId);
        loadThreads();
      } catch (error) {
        console.error('Failed to delete thread:', error);
      }
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  return (
    <>
      {/* Mobile hamburger */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-4 left-4 z-50 p-2 rounded-lg lg:hidden"
        style={{ background: 'var(--kuvera-teal)', color: '#fff', boxShadow: 'var(--shadow-md)' }}
        aria-label="Open menu"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      {/* Sidebar */}
      <div
        className={`fixed lg:static inset-y-0 left-0 z-40 w-64 flex flex-col transform transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
        style={{ background: 'var(--kuvera-surface)', borderRight: '1px solid var(--kuvera-border)' }}
      >
        {/* Kuvera-style logo/brand header */}
        <div className="flex items-center gap-3 px-5 py-4" style={{ borderBottom: '1px solid var(--kuvera-border)' }}>
          <div className="flex items-center justify-center w-8 h-8 rounded-lg" style={{ background: 'var(--kuvera-teal)' }}>
            <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div>
            <p className="text-sm font-600" style={{ color: 'var(--kuvera-text)', fontWeight: 600 }}>MF Assistant</p>
            <p className="text-xs" style={{ color: 'var(--kuvera-text-muted)' }}>by Kuvera</p>
          </div>
        </div>

        {/* New Chat button */}
        <div className="p-4">
          <button
            onClick={() => { onNewChat(); setIsOpen(false); }}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all hover:opacity-90 active:scale-[0.98]"
            style={{ background: 'var(--kuvera-teal)', color: '#fff' }}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Chat
          </button>
        </div>

        {/* Thread list */}
        <div className="flex-1 overflow-y-auto px-3 pb-3">
          {threads.length > 0 && (
            <p className="text-xs px-2 mb-2" style={{ color: 'var(--kuvera-text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Recent Chats
            </p>
          )}

          {isLoading ? (
            <div className="flex flex-col gap-2 mt-2">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-14 rounded-lg animate-pulse" style={{ background: 'var(--kuvera-bg)' }} />
              ))}
            </div>
          ) : threads.length === 0 ? (
            <div className="text-center py-8">
              <div className="w-10 h-10 rounded-full flex items-center justify-center mx-auto mb-3" style={{ background: 'var(--kuvera-teal-light)' }}>
                <svg className="w-5 h-5" style={{ color: 'var(--kuvera-teal)' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <p className="text-sm" style={{ color: 'var(--kuvera-text-muted)' }}>No chats yet</p>
              <p className="text-xs mt-1" style={{ color: 'var(--kuvera-text-light)' }}>Start asking questions</p>
            </div>
          ) : (
            <div className="space-y-1">
              {threads.map((thread) => (
                <div
                  key={thread.id}
                  onClick={() => { onThreadSelect(thread.id); setIsOpen(false); }}
                  className="group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all"
                  style={{
                    background: currentThreadId === thread.id ? 'var(--kuvera-teal-light)' : 'transparent',
                    borderLeft: currentThreadId === thread.id ? '3px solid var(--kuvera-teal)' : '3px solid transparent',
                  }}
                  onMouseEnter={e => {
                    if (currentThreadId !== thread.id) {
                      (e.currentTarget as HTMLElement).style.background = 'var(--kuvera-bg)';
                    }
                  }}
                  onMouseLeave={e => {
                    if (currentThreadId !== thread.id) {
                      (e.currentTarget as HTMLElement).style.background = 'transparent';
                    }
                  }}
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate" style={{ color: 'var(--kuvera-text)' }}>
                      Chat {thread.id.slice(0, 8)}...
                    </p>
                    <p className="text-xs mt-0.5" style={{ color: 'var(--kuvera-text-muted)' }}>
                      {formatDate(thread.updated_at)} · {thread.message_count} msgs
                    </p>
                  </div>
                  <button
                    onClick={(e) => handleDelete(e, thread.id)}
                    className="opacity-0 group-hover:opacity-100 p-1 rounded transition-all"
                    style={{ color: 'var(--kuvera-text-light)' }}
                    onMouseEnter={e => (e.currentTarget as HTMLElement).style.color = '#EF4444'}
                    onMouseLeave={e => (e.currentTarget as HTMLElement).style.color = 'var(--kuvera-text-light)'}
                  >
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Sidebar footer */}
        <div className="px-4 py-3" style={{ borderTop: '1px solid var(--kuvera-border)' }}>
          <p className="text-xs text-center" style={{ color: 'var(--kuvera-text-light)' }}>
            Facts-only · No investment advice
          </p>
        </div>
      </div>

      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 z-30 lg:hidden"
          style={{ background: 'rgba(26,43,74,0.4)', backdropFilter: 'blur(2px)' }}
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
}
