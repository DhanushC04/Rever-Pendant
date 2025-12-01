import React, { useState, useEffect } from 'react';
import { Search, Calendar, User, Clock, Trash2, FileText } from 'lucide-react';
import { getConversations, searchConversations, deleteAudio } from '../services/api';
import { Link } from 'react-router-dom';

const History = () => {
  const [conversations, setConversations] = useState([]);
  const [filteredConversations, setFilteredConversations] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchConversations();
  }, []);

  const fetchConversations = async () => {
    setIsLoading(true);
    try {
      const data = await getConversations();
      setConversations(data);
      setFilteredConversations(data);
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    
    if (query.length > 2) {
      try {
        const results = await searchConversations(query);
        setFilteredConversations(results);
      } catch (error) {
        console.error('Search error:', error);
      }
    } else {
      setFilteredConversations(conversations);
    }
  };

  const handleDeleteAudio = async (convId) => {
    if (window.confirm('Delete audio file? Transcript will be preserved.')) {
      try {
        await deleteAudio(convId);
        alert('Audio file deleted successfully');
        fetchConversations();
      } catch (error) {
        console.error('Delete error:', error);
      }
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-4xl font-bold text-white">Conversation History</h1>
          <Link 
            to="/"
            className="bg-blue-900 hover:bg-blue-800 text-white px-6 py-3 rounded-xl font-semibold border border-white"
          >
            New Recording
          </Link>
        </div>

        {/* Search Bar */}
        <div className="mb-6 relative">
          <Search className="absolute left-4 top-4 text-white" />
          <input
            type="text"
            placeholder="Search conversations by content..."
            value={searchQuery}
            onChange={handleSearch}
            className="w-full pl-12 pr-4 py-4 rounded-xl bg-slate-800 border border-white text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white"
          />
        </div>

        {/* Conversations List */}
        {isLoading ? (
          <div className="text-center text-white py-12">Loading...</div>
        ) : filteredConversations.length === 0 ? (
          <div className="text-center text-white/50 py-12">
            <FileText className="w-16 h-16 mx-auto mb-4 opacity-30" />
            <p>No conversations found</p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredConversations.map((conv) => (
              <div 
                key={conv.id} 
                className="bg-slate-900 rounded-2xl p-6 border border-white hover:bg-slate-800 transition-all"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <Link 
                      to={`/conversation/${conv.id}`}
                      className="text-xl font-bold text-white hover:text-purple-300"
                    >
                      {conv.title || 'Untitled Conversation'}
                    </Link>
                    <div className="flex items-center gap-4 mt-2 text-sm text-white/70">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        {new Date(conv.timestamp).toLocaleString()}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {conv.duration?.toFixed(0)}s
                      </span>
                      <span className="flex items-center gap-1">
                        <User className="w-4 h-4" />
                        {conv.speaker_count} speaker(s)
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteAudio(conv.id)}
                    className="text-white hover:text-white/70 p-2 border border-white rounded"
                    title="Delete audio (keep transcript)"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>

                <p className="text-white/80 mb-3 line-clamp-2">{conv.summary}</p>

                <div className="flex gap-2 flex-wrap">
                  <span className="text-xs bg-blue-900 text-white px-3 py-1 rounded-full border border-white">
                    {conv.word_count} words
                  </span>
                  {conv.location && (
                    <span className="text-xs bg-blue-900 text-white px-3 py-1 rounded-full border border-white">
                      📍 {conv.location}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default History;