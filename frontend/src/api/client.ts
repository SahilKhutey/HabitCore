const API_URL = "http://localhost:8000";

export type Method = "GET" | "POST" | "PUT" | "DELETE";

export const api = async (endpoint: string, method: Method = "GET", body: any = null, token: string | null = null) => {
  return fetch(`${API_URL}${endpoint}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token && { "Authorization": token }),
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
