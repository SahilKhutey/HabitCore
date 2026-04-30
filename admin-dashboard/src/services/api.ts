import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000/admin",
});

export const getDAU = () => API.get("/analytics/dau");
export const getUserGrowth = () => API.get("/analytics/user-growth");
export const getEvents = () => API.get("/analytics/events");
export const getStats = () => API.get("/stats");
export const getRetention = () => API.get("/analytics/retention");
export const banUser = (id: string) => API.post(`/ban/${id}`);
export const grantPremium = (id: string) => API.post(`/grant-premium/${id}`);
