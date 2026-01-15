// E:\MAWDSLEYS-AGENTE\frontend\src\services\activityLog.js

import api from "./api";

export const listActivityLogs = () => api.get("/activity-log");

export const getActivityLog = (id) => api.get(`/activity-log/${id}`);
