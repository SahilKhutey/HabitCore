import ENV from '../config/env';

const API_URL = ENV.API_URL;

export type Method = "GET" | "POST" | "PUT" | "DELETE";

export const api = async (endpoint: string, method: Method = "GET", body: any = null, token: string | null = null) => {
  return fetch(`${API_URL}${endpoint}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token && { "Authorization": `Bearer ${token}` }),
    },
    body: body ? JSON.stringify(body) : null,
  }).then(async res => {
    const data = await res.json();
    if (!res.ok) {
        throw new Error(data.detail || "API Error");
    }
    return data;
  });
};

export const login = async (email: string, password: string) => {
  return api("/auth/login", "POST", { email, password });
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
