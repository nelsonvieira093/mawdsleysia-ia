// frontend/src/services/followups.js

import api from "./api";

// ⚠️ baseURL = http://localhost:8000
// ⚠️ TODAS as rotas precisam começar com /api

export const listFollowups = () => api.get("/api/followups/");
export const getFollowup = (id) => api.get(`/api/followups/${id}`);
export const createFollowup = (data) => api.post("/api/followups/", data);

export const updateFollowup = (id, data) =>
  api.put(`/api/followups/${id}`, data);

export const closeFollowup = (id) => api.post(`/api/followups/${id}/close`);

export const deleteFollowup = (id) => api.delete(`/api/followups/${id}`);
