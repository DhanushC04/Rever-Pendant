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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-4xl font-bold text-white">Conversation History</h1>
          <Link 
            to="/"
            className="bg-purple-500 hover:bg-purple-600 text-white px-6 py-3 rounded-xl font-semibold"
          >
            New Recording
          </Link>
        </div>

        {/* Search Bar */}
        <div className="mb-6 relative">
          <Search className="absolute left-4 top-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search conversations by content..."
            value={searchQuery}
            onChange={handleSearch}
            className="w-full pl-12 pr-4 py-4 rounded-xl bg-white/10 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
        </div>

        {/* Conversations List */}
        {isLoading ? (
          <div className="text-center text-white py-12">Loading...</div>
        ) : filteredConversations.length === 0 ? (
          <div className="text-center text-gray-400 py-12">
            <FileText className="w-16 h-16 mx-auto mb-4 opacity-30" />
            <p>No conversations found</p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredConversations.map((conv) => (
              <div 
                key={conv.id} 
                className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20 hover:bg-white/15 transition-all"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <Link 
                      to={`/conversation/${conv.id}`}
                      className="text-xl font-bold text-white hover:text-purple-300"
                    >
                      {conv.title || 'Untitled Conversation'}
                    </Link>
                    <div className="flex items-center gap-4 mt-2 text-sm text-gray-400">
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
                    className="text-red-400 hover:text-red-300 p-2"
                    title="Delete audio (keep transcript)"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>

                <p className="text-white/80 mb-3 line-clamp-2">{conv.summary}</p>

                <div className="flex gap-2 flex-wrap">
                  <span className="text-xs bg-blue-500/20 text-blue-300 px-3 py-1 rounded-full">
                    {conv.word_count} words
                  </span>
                  {conv.location && (
                    <span className="text-xs bg-green-500/20 text-green-300 px-3 py-1 rounded-full">
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