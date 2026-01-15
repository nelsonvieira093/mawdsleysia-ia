// E:\MAWDSLEYS-AGENTE\frontend\src\services\meetings.js

import api from "./api";

export const sendMeetingInvite = (meetingId) =>
  api.post(`/meetings/${meetingId}/invite`);
