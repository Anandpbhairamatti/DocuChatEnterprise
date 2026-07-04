import { useState, useEffect, useRef } from 'react';
import { Send, Bot, User as UserIcon, Loader2, Trash2 } from 'lucide-react';
import { api } from '../api/axios';

interface Citation {
  chunk_id: string;
  document_id: string;
  filename: string;
  text: string;
  similarity: number;
}

interface Message {
  id: string;
  role: 'user' | 'ai';
  content: string;
  citations?: Citation[];
  created_at: string;
}

interface ChatSession {
  id: string;
  title: string;
  updated_at: string;
}

export default function Chat() {
  const [query, setQuery] = useState('');
  const [chats, setChats] = useState<ChatSession[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchChats();
  }, []);

  useEffect(() => {
    if (activeChatId) {
      fetchMessages(activeChatId);
    } else {
      setMessages([]);
    }
  }, [activeChatId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const fetchChats = async () => {
    try {
      const response = await api.get('/chat/');
      setChats(response.data);
    } catch (error) {
      console.error('Failed to fetch chats:', error);
    }
  };

  const fetchMessages = async (chatId: string) => {
    try {
      const response = await api.get(`/chat/${chatId}/messages`);
      setMessages(response.data);
    } catch (error) {
      console.error('Failed to fetch messages:', error);
    }
  };

  const handleDeleteChat = async (chatId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this chat?')) return;
    
    try {
      await api.delete(`/chat/${chatId}`);
      if (activeChatId === chatId) {
        setActiveChatId(null);
      }
      fetchChats();
    } catch (error) {
      console.error('Failed to delete chat:', error);
      alert('Failed to delete chat. Please try again.');
    }
  };

  const handleSend = async () => {
    if (!query.trim()) return;

    const currentQuery = query;
    setQuery('');
    setLoading(true);

    // Optimistically add user message
    const tempUserMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: currentQuery,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMsg]);

    try {
      const response = await api.post('/chat/message', {
        query: currentQuery,
        chat_id: activeChatId
      });
      
      const newAiMessage = response.data;
      setMessages(prev => [...prev, newAiMessage]);
      
      // If this was a new chat, refresh the chat list and set active
      if (!activeChatId && newAiMessage.chat_id) {
        setActiveChatId(newAiMessage.chat_id);
        fetchChats();
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      // Remove optimistic message on failure
      setMessages(prev => prev.filter(m => m.id !== tempUserMsg.id));
      alert('Failed to send message. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex h-full bg-background overflow-hidden">
      {/* Sidebar history */}
      <div className="w-64 border-r border-border bg-muted/10 p-4 flex flex-col h-full overflow-y-auto">
        <button 
          onClick={() => setActiveChatId(null)}
          className="w-full py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium mb-4 flex-shrink-0"
        >
          + New Chat
        </button>
        <div className="space-y-2 flex-1">
          {chats.map(chat => (
            <div 
              key={chat.id}
              onClick={() => setActiveChatId(chat.id)}
              className={`p-2 rounded cursor-pointer text-sm font-medium transition-colors flex items-center justify-between group ${activeChatId === chat.id ? 'bg-primary/20 text-primary' : 'hover:bg-muted text-foreground'}`}
            >
              <span className="truncate pr-2">{chat.title}</span>
              <button 
                onClick={(e) => handleDeleteChat(chat.id, e)}
                className="opacity-0 group-hover:opacity-100 hover:text-destructive transition-opacity p-1"
                title="Delete Chat"
              >
                <Trash2 size={14} />
              </button>
            </div>
          ))}
          {chats.length === 0 && (
            <div className="text-sm text-muted-foreground text-center mt-4">No previous chats</div>
          )}
        </div>
      </div>
      
      {/* Main chat */}
      <div className="flex-1 flex flex-col relative h-full">
        <div className="flex-1 overflow-auto p-6 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-muted-foreground">
              <Bot size={48} className="mb-4 text-muted-foreground/50" />
              <h2 className="text-xl font-medium mb-2">How can I help you today?</h2>
              <p className="text-sm">Ask a question about your uploaded documents.</p>
            </div>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.role === 'ai' && (
                  <div className="w-8 h-8 rounded bg-primary/20 flex items-center justify-center shrink-0">
                    <Bot size={20} className="text-primary" />
                  </div>
                )}
                <div className={`space-y-2 max-w-[80%] ${msg.role === 'user' ? 'bg-primary text-primary-foreground p-3 rounded-2xl rounded-tr-sm' : ''}`}>
                  <div className="prose dark:prose-invert max-w-none">
                    <p className="whitespace-pre-wrap">{msg.content}</p>
                  </div>
                  {msg.role === 'ai' && msg.citations && msg.citations.length > 0 && (
                    <div className="flex items-center gap-2 mt-4 flex-wrap">
                      {msg.citations.map((cit, idx) => (
                        <span key={idx} className="text-xs text-blue-500 hover:underline cursor-pointer border border-blue-200 bg-blue-50 px-2 py-1 rounded dark:border-blue-900 dark:bg-blue-950 dark:text-blue-400">
                          [{idx + 1}] {cit.filename}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded bg-muted flex items-center justify-center shrink-0">
                    <UserIcon size={20} className="text-foreground" />
                  </div>
                )}
              </div>
            ))
          )}
          {loading && (
            <div className="flex gap-4 justify-start">
              <div className="w-8 h-8 rounded bg-primary/20 flex items-center justify-center shrink-0">
                <Bot size={20} className="text-primary" />
              </div>
              <div className="flex items-center gap-2 text-muted-foreground text-sm">
                <Loader2 size={16} className="animate-spin" />
                Thinking...
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        
        {/* Input */}
        <div className="p-4 border-t border-border bg-card shrink-0">
          <div className="max-w-3xl mx-auto relative flex items-center">
            <input 
              type="text" 
              placeholder="Ask a question about your documents..." 
              className="w-full pl-4 pr-12 py-3 bg-background border border-input rounded-xl focus:outline-none focus:ring-2 focus:ring-primary shadow-sm disabled:opacity-50"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />
            <button 
              onClick={handleSend}
              disabled={loading || !query.trim()}
              className="absolute right-2 p-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
            >
              <Send size={18} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
