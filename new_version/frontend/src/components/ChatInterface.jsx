import React, { useState } from 'react';
import { Send, MessageSquare, FileText } from 'lucide-react';
import { chatWithHistory } from '../services/api';
import { Link } from 'react-router-dom';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMessage = {
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await chatWithHistory(inputValue);
      
      const aiMessage = {
        type: 'ai',
        content: response.response,
        sources: response.sources || [],
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        type: 'error',
        content: 'Failed to get response. Please try again.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Chat with Your Memory</h1>
          <p className="text-white/70">Ask me anything about your past conversations</p>
        </div>

        {/* Chat Messages */}
        <div className="bg-slate-900 rounded-2xl p-6 border border-white mb-6 h-[500px] overflow-y-auto">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-white/50">
              <MessageSquare className="w-16 h-16 mb-4" />
              <p className="text-center">Start a conversation about your recorded meetings</p>
              <p className="text-sm text-center mt-2">Try asking: "What did we discuss about the project deadline?"</p>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message, idx) => (
                <div key={idx} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] rounded-xl p-4 ${
                    message.type === 'user' ? 'bg-blue-900 text-white border border-white' :
                    message.type === 'error' ? 'bg-slate-800 text-white border border-white' :
                    'bg-slate-800 text-white border border-white'
                  }`}>
                    <p className="whitespace-pre-wrap">{message.content}</p>
                    
                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-white">
                        <p className="text-xs text-white mb-2">Sources:</p>
                        {message.sources.map((source, sourceIdx) => (
                          <Link
                            key={sourceIdx}
                            to={`/conversation/${source.id}`}
                            className="block text-xs bg-slate-700 rounded px-2 py-1 mb-1 hover:bg-slate-600 border border-white"
                          >
                            <FileText className="w-3 h-3 inline mr-1" />
                            {source.title} ({source.date})
                            <span className="ml-2 text-white/70">
                              {(source.similarity * 100).toFixed(0)}% match
                            </span>
                          </Link>
                        ))}
                      </div>
                    )}
                    
                    <p className="text-xs text-white/60 mt-2">
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-slate-800 rounded-xl p-4 border border-white">
                    <div className="flex gap-2">
                      <div className="w-2 h-2 bg-white rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Input */}
        <div className="flex gap-3">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask about your conversations..."
            className="flex-1 px-4 py-4 rounded-xl bg-slate-800 border border-white text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white"
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !inputValue.trim()}
            className="bg-blue-900 hover:bg-blue-800 text-white px-6 py-4 rounded-xl font-semibold flex items-center gap-2 border border-white disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;