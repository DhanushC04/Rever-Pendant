import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API functions
export const startProcess = async () => {
  try {
    const response = await api.post('/start');
    return response.data;
  } catch (error) {
    console.error('Start process error:', error);
    throw error;
  }
};

export const getStatus = async () => {
  try {
    const response = await api.get('/status');
    return response.data;
  } catch (error) {
    console.error('Get status error:', error);
    throw error;
  }
};

export const resetProcess = async () => {
  try {
    const response = await api.post('/reset');
    return response.data;
  } catch (error) {
    console.error('Reset process error:', error);
    throw error;
  }
};

export const downloadResults = async () => {
  try {
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
  } catch (error) {
    console.error('Download error:', error);
    throw error;
  }
};

export const checkHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw new Error('Backend is not responding');
  }
};

export default api;