// auth.js
// Small helper functions for reading/writing auth state in localStorage.

export function isLoggedIn() {
  return !!localStorage.getItem("token"); // !! converts to a true/false boolean
}

export function getToken() {
  return localStorage.getItem("token");
}

export function getUserName() {
  return localStorage.getItem("userName");
}

export function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("userName");
}