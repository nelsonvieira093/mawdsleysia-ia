import api from "./api";

// Lista conversas
export const listConversations = async () => {
  const res = await api.get("/whatsapp/conversations");
  return res.data;
};

// Busca mensagens de uma conversa
export const getMessages = async (conversationId) => {
  const res = await api.get(`/whatsapp/messages/${conversationId}`);
  return res.data;
};

// Enviar mensagem manual pelo dashboard
export const sendMessage = async (to, text) => {
  const res = await api.post(`/whatsapp/send`, { to, text });
  return res.data;
};

// Logs do webhook
export const getWebhookStatus = async () => {
  const res = await api.get("/whatsapp/status");
  return res.data;
};
