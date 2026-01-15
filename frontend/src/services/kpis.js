// E:\MAWDSLEYS-AGENTE\frontend\src\services\kpis.js

import api from "./api";

export const getKpiOverview = () => api.get("/api/kpis/overview");

//export const getKpiOperational = () => api.get("/api/kpis/operational");