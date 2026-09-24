// api.js
// Centralized Axios instance — automatically attaches the JWT token
// to every outgoing request if one exists.

import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

// This runs before EVERY request made with this 'api' instance
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;