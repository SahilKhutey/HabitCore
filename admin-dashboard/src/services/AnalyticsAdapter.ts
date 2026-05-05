import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const getHeaders = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const API = axios.create({
  baseURL: `${BASE_URL}/admin`,
});

API.interceptors.request.use((config) => {
  config.headers = { ...config.headers, ...getHeaders() };
  return config;
});

export const AnalyticsAdapter = {
  getStats: async () => {
    try {
      const response = await API.get('/stats');
      return response.data;
    } catch (e) {
      console.error("Failed to fetch stats", e);
      return { total_users: 0, premium_rate: 0, system_treasury: 0, growth_velocity: "0%" };
    }
  },

  getDAU: async () => {
    try {
      const response = await API.get('/analytics/dau');
      return response.data.dau || 0;
    } catch (e) {
      console.error("Failed to fetch DAU", e);
      return 0;
    }
  },
  
  getUserGrowth: async () => {
    try {
      const response = await API.get('/analytics/user-growth');
      return response.data || [];
    } catch (e) {
      console.error("Failed to fetch user growth", e);
      return [];
    }
  },
  
  getRetention: async () => {
    try {
      const response = await API.get('/analytics/retention');
      return response.data || [];
    } catch (e) {
      console.error("Failed to fetch retention", e);
      return [];
    }
  },

  getArchetypeDistribution: async () => {
    try {
      const response = await API.get('/analytics/archetype-distribution');
      return response.data || [];
    } catch (e) {
      console.error("Failed to fetch archetype distribution", e);
      return [];
    }
  },

  getTopHabits: async () => {
    try {
      const response = await API.get('/analytics/top-habits');
      return response.data || [];
    } catch (e) {
      console.error("Failed to fetch top habits", e);
      return [];
    }
  },

  getRecentEvents: async () => {
    try {
      const response = await API.get('/analytics/events');
      return response.data || [];
    } catch (e) {
      console.error("Failed to fetch events", e);
      return [];
    }
  },

  banUser: async (id: string) => {
    return API.post(`/ban/${id}`);
  },

  grantPremium: async (id: string) => {
    return API.post(`/grant-premium/${id}`);
  }
};
