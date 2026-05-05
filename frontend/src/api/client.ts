import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import ENV from '../config/env';
import { useUserStore } from '../store/useUserStore';

const apiClient = axios.create({
  baseURL: ENV.API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: Inject JWT Token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = useUserStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Unified Error Handling
apiClient.interceptors.response.use(
  (response) => response.data,
  (error: AxiosError) => {
    const message = (error.response?.data as any)?.detail || error.message || 'Network error';
    
    if (error.response?.status === 401) {
      // Auto-logout on unauthorized
      useUserStore.getState().resetUser();
    }
    
    console.error(`[API Error] ${error.config?.url}:`, message);
    return Promise.reject({ message, status: error.response?.status });
  }
);

/**
 * Legacy wrapper for compatibility with existing code
 */
export async function api(endpoint: string, method: string = 'GET', body: any = null, token?: string) {
  const url = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  
  try {
    const config: any = {
      url,
      method,
    };
    
    if (body) {
      config.data = body;
    }
    
    // If token is explicitly passed (legacy), override interceptor
    if (token) {
      config.headers = { Authorization: `Bearer ${token}` };
    }
    
    const response = await apiClient(config);
    return response as any;
  } catch (error: any) {
    // Re-throw for specific component handling
    throw error;
  }
}

export default apiClient;

export type Method = "GET" | "POST" | "PUT" | "DELETE";

export const login = async (email: string, password: string) => {
  return api("/auth/login", "POST", { email, password });
};

export const register = async (email: string, password: string) => {
  return api("/auth/register", "POST", { email, password });
};

export const createHabit = async (name: string, time: string | null, token: string) => {
  return api("/habits/create", "POST", { name, time }, token);
};

export const completeHabit = async (habitId: string, token: string) => {
  return api("/habits/complete", "POST", { habit_id: habitId }, token);
};

export const updateHabit = async (habitId: string, name: string, time: string | null, token: string) => {
  return api(`/habits/${habitId}`, "PUT", { name, time }, token);
};

export const deleteHabit = async (habitId: string, token: string) => {
  return api(`/habits/${habitId}`, "DELETE", null, token);
};

export const getTodayStatus = async (token: string) => {
  return api("/habits/today/status", "GET", null, token);
};

export const getHabitHistory = async (habitId: string, token: string) => {
  return api(`/habits/${habitId}/history`, "GET", null, token);
};

export const getWeeklyReport = async (token: string) => {
  return api("/analytics/weekly", "GET", null, token);
};

export const getLeaderboard = async (token: string) => {
  return api("/analytics/leaderboard", "GET", null, token);
};

export const getRecommendations = async (token: string) => {
  return api("/analytics/recommendations", "GET", null, token);
};

export const getIdentityPulse = async (token: string) => {
  return api("/analytics/pulse", "GET", null, token);
};


export const getSmartTime = async (habitId: string, token: string) => {
  return api(`/habits/${habitId}/smart-time`, "GET", null, token);
};

export const adjustDifficulty = async (habitId: string, token: string) => {
  return api(`/habits/${habitId}/adjust`, "POST", null, token);
};

export const setDifficulty = async (habitId: string, level: string, token: string) => {
  return api(`/habits/${habitId}/difficulty`, "PUT", { level }, token);
};

export const getShopItems = async () => {
  return api("/shop/items", "GET");
};

export const buyShopItem = async (itemId: string, token: string) => {
  return api(`/shop/buy/${itemId}`, "POST", null, token);
};

export const useFreeze = async (habitId: string, token: string) => {
  return api(`/habits/${habitId}/freeze`, "POST", null, token);
};

export const getBurnout = async (token: string) => {
  return api("/users/burnout", "GET", null, token);
};

export const getMyBadges = async (token: string) => {
  return api("/users/badges", "GET", null, token);
};

export const getInventory = async (token: string) => {
  return api("/users/inventory", "GET", null, token);
};

export const updatePreferences = async (data: any, token: string) => {
  return api("/users/preferences", "PUT", data, token);
};
export const equipItem = async (inventoryId: string, token: string) => {
  return api(`/shop/equip/${inventoryId}`, "POST", null, token);
};

export const dailyCheckin = async (data: any, token: string) => {
  return api("/psychological/checkin", "POST", data, token);
};

export const getDailyChallenge = async () => {
  return api("/psychological/daily-challenge", "GET");
};

export const getUserProgress = async (token: string) => {
  return api("/psychological/user-progress", "GET", null, token);
};

export const getHabitState = async (token: string) => {
  return api("/habits/state", "GET", null, token);
};

export const resetBurnout = async (token: string) => {
  return api("/habits/reset-burnout", "POST", null, token);
};
