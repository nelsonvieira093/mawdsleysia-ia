// src/contexts/AIContext.jsx
import React, { createContext, useState, useContext, useEffect } from "react";
import { getAIContext, chatWithAI } from "../services/api";
import { useAuth } from "./AuthContext";

const AIContext = createContext();

export const AIProvider = ({ children }) => {
  // ✅ CORREÇÃO: evita optional chaining em chamada de função
  let user = null;
  try {
    const auth = useAuth();
    user = auth?.user || null;
  } catch {
    user = null;
  }

  const [aiState, setAiState] = useState({
    context: null,
    conversation: [],
    isLoading: false,
    lastUpdated: null,
  });

  // Atualiza contexto quando usuário muda
  useEffect(() => {
    if (user?.id) {
      refreshContext(user.id);
    }
  }, [user?.id]);

  const refreshContext = async (userId) => {
    setAiState((prev) => ({ ...prev, isLoading: true }));
    try {
      const context = await getAIContext(userId);
      setAiState((prev) => ({
        ...prev,
        context,
        isLoading: false,
        lastUpdated: new Date().toISOString(),
      }));
    } catch (error) {
      console.error("Erro ao atualizar contexto IA:", error);
      setAiState((prev) => ({ ...prev, isLoading: false }));
    }
  };

  const sendToAI = async (message) => {
    const userMessage = {
      role: "user",
      content: message,
      timestamp: new Date(),
    };

    setAiState((prev) => ({
      ...prev,
      conversation: [...prev.conversation, userMessage],
      isLoading: true,
    }));

    try {
      const response = await chatWithAI(message);

      const aiMessage = {
        role: "assistant",
        content: response.response || response.data?.response,
        data: response.relevant_data || response.data?.relevant_data,
        timestamp: new Date(),
      };

      setAiState((prev) => ({
        ...prev,
        conversation: [...prev.conversation, aiMessage],
        isLoading: false,
      }));

      return aiMessage;
    } catch (error) {
      console.error("Erro no chat:", error);

      const errorMessage = {
        role: "assistant",
        content: "Desculpe, ocorreu um erro. Tente novamente.",
        timestamp: new Date(),
      };

      setAiState((prev) => ({
        ...prev,
        conversation: [...prev.conversation, errorMessage],
        isLoading: false,
      }));

      return errorMessage;
    }
  };

  const clearConversation = () => {
    setAiState((prev) => ({ ...prev, conversation: [] }));
  };

  return (
    <AIContext.Provider
      value={{
        ...aiState,
        sendToAI,
        refreshContext,
        clearConversation,
      }}
    >
      {children}
    </AIContext.Provider>
  );
};

export const useAI = () => {
  const context = useContext(AIContext);
  if (!context) {
    throw new Error("useAI must be used within AIProvider");
  }
  return context;
};
