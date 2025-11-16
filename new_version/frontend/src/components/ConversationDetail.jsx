// src/components/ConversationDetail.jsx - ENHANCED VERSION

import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, User, Clock, Calendar, MapPin, CheckCircle, Bell, BellOff, Trash2 } from 'lucide-react';
import { getConversationDetail, markKeynoteComplete, createReminder, getUserReminders, cancelReminder } from '../services/api';

const ConversationDetail = () => {
  const { id } = useParams();
  const [conversation, setConversation] = useState(null);
  const [activeTab, setActiveTab] = useState('transcript');
  const [isLoading, setIsLoading] = useState(true);
  const [reminders, setReminders] = useState([]);
  const [showReminderModal, setShowReminderModal] = useState(false);
  const [selectedKeynote, setSelectedKeynote] = useState(null);

  useEffect(() => {
    fetchConversation();
    fetchReminders();
  }, [id]);

  const fetchConversation = async () => {
    setIsLoading(true);
    try {
      const data = await getConversationDetail(id);
      setConversation(data);
    } catch (error) {
      console.error('Failed to fetch conversation:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchReminders = async () => {
    try {
      const data = await getUserReminders(1); // user_id = 1
      setReminders(data);
    } catch (error) {
      console.error('Failed to fetch reminders:', error);
    }
  };

  const handleCompleteKeynote = async (keynoteId) => {
    try {
      await markKeynoteComplete(keynoteId);
      fetchConversation(); // Refresh to show updated status
    } catch (error) {
      console.error('Error marking complete:', error);
    }
  };

  const openReminderModal = (keynote) => {
    setSelectedKeynote(keynote);
    setShowReminderModal(true);
  };

  const handleSetReminder = async (hours) => {
    if (!selectedKeynote) return;

    const reminderTime = new Date();
    reminderTime.setHours(reminderTime.getHours() + parseInt(hours));

    try {
      await createReminder(selectedKeynote.id, reminderTime.toISOString(), 1);
      alert(`✅ Reminder set for ${reminderTime.toLocaleString()}`);
      setShowReminderModal(false);
      fetchReminders();
    } catch (error) {
      console.error('Error setting reminder:', error);
      alert('❌ Failed to set reminder');
    }
  };

  const handleCancelReminder = async (reminderId) => {
    if (!window.confirm('Cancel this reminder?')) return;

    try {
      await cancelReminder(reminderId);
      alert('✅ Reminder cancelled');
      fetchReminders();
    } catch (error) {
      console.error('Error cancelling reminder:', error);
    }
  };

  const isReminderSet = (keynoteId) => {
    return reminders.some(r => r.keynote_id === keynoteId && !r.is_sent);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
      </div>
    );
  }

  if (!conversation) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Conversation not found</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link 
            to="/history" 
            className="inline-flex items-center gap-2 text-purple-300 hover:text-purple-200 mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to History
          </Link>
          
          <h1 className="text-4xl font-bold text-white mb-4">{conversation.title}</h1>
          
          <div className="flex items-center gap-6 text-gray-300">
            <span className="flex items-center gap-2">
              <Calendar className="w-5 h-5" />
              {new Date(conversation.timestamp).toLocaleString()}
            </span>
            <span className="flex items-center gap-2">
              <Clock className="w-5 h-5" />
              {conversation.duration?.toFixed(0)}s
            </span>
            {conversation.location && (
              <span className="flex items-center gap-2">
                <MapPin className="w-5 h-5" />
                {conversation.location}
              </span>
            )}
            {conversation.speakers && (
              <span className="flex items-center gap-2">
                <User className="w-5 h-5" />
                {conversation.speakers.length} speaker(s)
              </span>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          {['transcript', 'speakers', 'keynotes', 'summary'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-3 rounded-xl font-semibold transition-all ${
                activeTab === tab
                  ? 'bg-purple-500 text-white'
                  : 'bg-white/10 text-gray-300 hover:bg-white/15'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
          {activeTab === 'keynotes' && (
            <div>
              <h2 className="text-2xl font-bold text-white mb-4">Key Takeaways</h2>
              {conversation.keynotes && conversation.keynotes.length > 0 ? (
                <div className="space-y-3">
                  {conversation.keynotes.map((keynote) => {
                    const hasReminder = isReminderSet(keynote.id);
                    
                    return (
                      <div 
                        key={keynote.id} 
                        className={`bg-white/5 rounded-xl p-4 border-l-4 ${
                          keynote.category === 'action_item' ? 'border-red-500' :
                          keynote.category === 'decision' ? 'border-green-500' :
                          keynote.category === 'question' ? 'border-yellow-500' :
                          keynote.category === 'deadline' ? 'border-red-600' :
                          'border-blue-500'
                        }`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <span className={`inline-block text-xs px-2 py-1 rounded mb-2 ${
                              keynote.category === 'action_item' ? 'bg-red-500/20 text-red-300' :
                              keynote.category === 'decision' ? 'bg-green-500/20 text-green-300' :
                              keynote.category === 'question' ? 'bg-yellow-500/20 text-yellow-300' :
                              keynote.category === 'deadline' ? 'bg-red-600/20 text-red-300' :
                              'bg-blue-500/20 text-blue-300'
                            }`}>
                              {keynote.category.replace('_', ' ').toUpperCase()}
                            </span>
                            <p className={`text-white/90 ${keynote.is_completed ? 'line-through opacity-50' : ''}`}>
                              {keynote.content}
                            </p>
                            <div className="flex items-center gap-4 mt-2">
                              <span className="text-xs text-gray-400">
                                Importance: {(keynote.importance_score * 100).toFixed(0)}%
                              </span>
                              {hasReminder && (
                                <span className="text-xs bg-yellow-500/20 text-yellow-300 px-2 py-1 rounded flex items-center gap-1">
                                  <Bell className="w-3 h-3" />
                                  Reminder Set
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="flex gap-2 ml-4">
                            <button
                              onClick={() => handleCompleteKeynote(keynote.id)}
                              className={`p-2 transition-colors ${
                                keynote.is_completed 
                                  ? 'text-gray-400' 
                                  : 'text-green-400 hover:text-green-300'
                              }`}
                              title={keynote.is_completed ? 'Mark as incomplete' : 'Mark as complete'}
                            >
                              <CheckCircle className="w-5 h-5" />
                            </button>
                            <button
                              onClick={() => openReminderModal(keynote)}
                              className="p-2 text-yellow-400 hover:text-yellow-300"
                              title="Set reminder"
                            >
                              {hasReminder ? <BellOff className="w-5 h-5" /> : <Bell className="w-5 h-5" />}
                            </button>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="text-gray-400">No keynotes extracted</p>
              )}
            </div>
          )}

          {/* Other tabs content... */}
          {activeTab === 'transcript' && (
            <div>
              <h2 className="text-2xl font-bold text-white mb-4">Full Transcript</h2>
              <p className="text-white/90 leading-relaxed whitespace-pre-wrap">
                {conversation.transcript}
              </p>
            </div>
          )}

          {activeTab === 'summary' && (
            <div>
              <h2 className="text-2xl font-bold text-white mb-4">AI Summary</h2>
              <p className="text-white/90 leading-relaxed">
                {conversation.summary}
              </p>
            </div>
          )}

          {activeTab === 'speakers' && (
            <div>
              <h2 className="text-2xl font-bold text-white mb-4">Speaker Analysis</h2>
              {conversation.speakers && conversation.speakers.length > 0 ? (
                <div className="space-y-6">
                  {conversation.speakers.map((speaker, idx) => (
                    <div key={idx} className="bg-white/5 rounded-xl p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-xl font-bold text-white">
                          {speaker.name || speaker.label}
                        </h3>
                        <span className="text-sm text-gray-400">
                          {speaker.total_duration?.toFixed(1)}s speaking time
                        </span>
                      </div>
                      
                      <div className="space-y-3">
                        {speaker.segments && speaker.segments.map((segment, segIdx) => (
                          <div key={segIdx} className="bg-black/20 rounded-lg p-4">
                            <div className="text-xs text-gray-400 mb-2">
                              {segment.start?.toFixed(1)}s - {segment.end?.toFixed(1)}s
                            </div>
                            <p className="text-white/90">{segment.text}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-400">No speaker data available</p>
              )}
            </div>
          )}
        </div>

        {/* Active Reminders Section */}
        {reminders.filter(r => !r.is_sent).length > 0 && (
          <div className="mt-6 bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
            <h3 className="text-xl font-bold text-white mb-4">⏰ Active Reminders</h3>
            <div className="space-y-2">
              {reminders.filter(r => !r.is_sent).map((reminder) => (
                <div key={reminder.id} className="bg-white/5 rounded-lg p-4 flex items-center justify-between">
                  <div>
                    <p className="text-white">Reminder for Keynote #{reminder.keynote_id}</p>
                    <p className="text-sm text-gray-400">
                      Scheduled: {new Date(reminder.reminder_time).toLocaleString()}
                    </p>
                  </div>
                  <button
                    onClick={() => handleCancelReminder(reminder.id)}
                    className="text-red-400 hover:text-red-300 p-2"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Reminder Modal */}
      {showReminderModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setShowReminderModal(false)}>
          <div className="bg-slate-800 rounded-2xl p-8 max-w-md w-full mx-4" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-2xl font-bold text-white mb-4">Set Reminder</h3>
            <p className="text-gray-300 mb-6">
              {selectedKeynote?.content}
            </p>
            <div className="space-y-3">
              <button
                onClick={() => handleSetReminder(1)}
                className="w-full bg-purple-500 hover:bg-purple-600 text-white py-3 rounded-xl font-semibold"
              >
                Remind me in 1 hour
              </button>
              <button
                onClick={() => handleSetReminder(24)}
                className="w-full bg-purple-500 hover:bg-purple-600 text-white py-3 rounded-xl font-semibold"
              >
                Remind me in 24 hours
              </button>
              <button
                onClick={() => handleSetReminder(72)}
                className="w-full bg-purple-500 hover:bg-purple-600 text-white py-3 rounded-xl font-semibold"
              >
                Remind me in 3 days
              </button>
              <button
                onClick={() => handleSetReminder(168)}
                className="w-full bg-purple-500 hover:bg-purple-600 text-white py-3 rounded-xl font-semibold"
              >
                Remind me in 1 week
              </button>
              <button
                onClick={() => setShowReminderModal(false)}
                className="w-full bg-gray-600 hover:bg-gray-700 text-white py-3 rounded-xl font-semibold"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ConversationDetail;