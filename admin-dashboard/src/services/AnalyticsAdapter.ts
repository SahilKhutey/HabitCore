import axios from 'axios';

const BASE_URL = 'http://localhost:8000';

// In a real app, you would inject this token via Context/Zustand or interceptors
const getHeaders = () => {
  const token = localStorage.getItem('token'); // Simplification for admin
  return token ? { Authorization: `Bearer ${token}` } : {};
};

export const AnalyticsAdapter = {
  getDAU: async () => {
    try {
      const response = await axios.get(`${BASE_URL}/admin/analytics/dau`, { headers: getHeaders() });
      return response.data.dau || 0;
    } catch (e) {
      console.error("Failed to fetch DAU", e);
      return 0;
    }
  },
  
  getUserGrowth: async () => {
    try {
      const response = await axios.get(`${BASE_URL}/admin/analytics/user-growth`, { headers: getHeaders() });
      return response.data || [];
    } catch (e) {
      console.error("Failed to fetch user growth", e);
      return [];
    }
  },
  
  getRetention: async () => {
    try {
      const response = await axios.get(`${BASE_URL}/admin/analytics/retention`, { headers: getHeaders() });
      return response.data || [];
    } catch (e) {
      console.error("Failed to fetch retention", e);
      return [];
    }
  }
};
