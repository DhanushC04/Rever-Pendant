// src/services/api.js - COMPLETE VERSION

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============================================================================
// ORIGINAL API FUNCTIONS (Your existing project - unchanged)
// ============================================================================

export const startProcess = async (userId = 1) => {
  const response = await api.post('/start', { user_id: userId });
  return response.data;
};

export const getStatus = async () => {
  const response = await api.get('/status');
  return response.data;
};

export const resetProcess = async () => {
  const response = await api.post('/reset');
  return response.data;
};

export const downloadResults = async () => {
  const response = await api.get('/download', {
    responseType: 'blob',
  });
  
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', 'final_output.txt');
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const checkHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

// ============================================================================
// NEW ADD-ON: Conversation Management
// ============================================================================

export const getConversations = async () => {
  const response = await api.get('/conversations');
  return response.data;
};

export const getConversationDetail = async (convId) => {
  const response = await api.get(`/conversations/${convId}`);
  return response.data;
};

// ============================================================================
// NEW ADD-ON: Keynote Management
// ============================================================================

export const markKeynoteComplete = async (keynoteId) => {
  const response = await api.post(`/keynotes/${keynoteId}/complete`);
  return response.data;
};

// ============================================================================
// NEW ADD-ON: Email Reminder System
// ============================================================================

/**
 * Create a reminder for a keynote
 * @param {number} keynoteId - ID of the keynote
 * @param {string} reminderTime - ISO format datetime (e.g., "2024-11-15T10:00:00")
 * @param {number} userId - User ID (default: 1)
 * @returns {Promise} Response with reminder_id and scheduled time
 */
export const createReminder = async (keynoteId, reminderTime, userId = 1) => {
  try {
    const response = await api.post('/reminders', {
      keynote_id: keynoteId,
      reminder_time: reminderTime,
      user_id: userId
    });
    return response.data;
  } catch (error) {
    console.error('Error creating reminder:', error);
    throw error;
  }
};

/**
 * Get all reminders for a user
 * @param {number} userId - User ID
 * @returns {Promise} Array of reminders
 */
export const getUserReminders = async (userId) => {
  try {
    const response = await api.get(`/reminders/user/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching reminders:', error);
    throw error;
  }
};

/**
 * Cancel a scheduled reminder
 * @param {number} reminderId - ID of the reminder to cancel
 * @returns {Promise} Confirmation response
 */
export const cancelReminder = async (reminderId) => {
  try {
    const response = await api.delete(`/reminders/${reminderId}`);
    return response.data;
  } catch (error) {
    console.error('Error cancelling reminder:', error);
    throw error;
  }
};

// ============================================================================
// NEW ADD-ON: Search and Chat
// ============================================================================

export const searchConversations = async (query) => {
  const response = await api.get('/search', { params: { q: query } });
  return response.data;
};

export const chatWithHistory = async (query) => {
  const response = await api.post('/chat', { query });
  return response.data;
};

// ============================================================================
// NEW ADD-ON: Audio Management
// ============================================================================

export const deleteAudio = async (convId) => {
  const response = await api.delete(`/audio/${convId}/delete`);
  return response.data;
};

// ============================================================================
// Error Handling Wrapper (Recommended)
// ============================================================================

/**
 * Generic error handler for API calls
 */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error
      console.error('API Error:', error.response.data);
      
      // You can add custom error handling here
      if (error.response.status === 404) {
        console.log('Resource not found');
      } else if (error.response.status === 500) {
        console.log('Server error');
      }
    } else if (error.request) {
      // Request made but no response
      console.error('No response from server');
    } else {
      // Something else happened
      console.error('Error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export default api;