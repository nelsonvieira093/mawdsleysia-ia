// frontend/src/pages/Chat.jsx - VERSÃO CORRIGIDA E ROBUSTA COM MELHORIAS
import React, { useState, useEffect, useRef } from "react";
import Sidebar from "../components/Sidebar";
import ChatInput from "../components/ChatInput";
import api from "../services/api";
import { useAuth } from "../contexts/AuthContext";
import { getAIContext } from "../services/api";
import ExecutiveBlock from "../components/ExecutiveBlock";

import "./Chat.css";

export default function Chat() {
  const { user } = useAuth();

  const [messages, setMessages] = useState([
    {
      id: 1,
      role: "assistant",
      type: "chat",
      content:
        "👋 Olá! Eu sou o **Agente MAWDSLEYS**.\n\nVocê pode conversar normalmente ou registrar pensamentos executivos (Bullet Journal).",
      timestamp: new Date().toISOString(),
    },
  ]);

  const [inputMessage, setInputMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [aiStatus, setAiStatus] = useState("checking");
  const [aiContext, setAiContext] = useState(null);
  const messagesEndRef = useRef(null);

  // 🔥 modo de operação
  const [mode, setMode] = useState("chat"); // chat | executive

  // =============================
  // FUNÇÕES AUXILIARES PARA PROCESSAMENTO EXECUTIVO
  // =============================

  const extractExecutiveDataFromText = (text) => {
    console.log("🔍 Extraindo dados executivos do texto...");

    const data = {
      hashtags: [],
      summary: "",
      structured_summary: "",
      followups: [],
      rituals: [],
      directors: [],
      actions: [],
      register_location: "DailyLog",
      raw_text: text,
    };

    // 1. Extrai hashtags (#tag)
    const hashtagMatches = text.match(/#([a-zA-ZÀ-ÿ0-9_]+)/g);
    if (hashtagMatches) {
      data.hashtags = hashtagMatches.map((tag) => tag.replace("#", "").trim());
    }

    // 🔥 MELHORIA 1: Extrair datas automaticamente (ADICIONADO)
    const datePatterns = [
      /\b(\d{1,2}\/\d{1,2}\/\d{4})\b/g, // DD/MM/YYYY
      /\b(\d{1,2}\s+de\s+\w+\s+\d{4})\b/gi, // "15 de Janeiro 2024"
      /\b(amanhã|hoje|segunda|terça|quarta|quinta|sexta|sábado|domingo)\b/gi,
      /\b(\d{1,2}\/\d{1,2})\b/g, // DD/MM (assume ano atual)
      /\b(até\s+\d{1,2}\/\d{1,2})\b/gi, // "até 15/01"
      /\b(para\s+\d{1,2}\/\d{1,2})\b/gi, // "para 15/01"
      /\b(prazo:\s+\d{1,2}\/\d{1,2})\b/gi, // "prazo: 15/01"
    ];

    const dates = [];
    datePatterns.forEach((pattern) => {
      const matches = text.match(pattern);
      if (matches) dates.push(...matches);
    });

    if (dates.length > 0) {
      data.deadline = dates[0];
      console.log("📅 Datas encontradas:", dates);
    }

    // 🔥 MELHORIA 2: Detectar prioridade automaticamente (ADICIONADO)
    const lowerText = text.toLowerCase();

    if (
      lowerText.includes("urgente") ||
      lowerText.includes("asap") ||
      lowerText.includes("hoje") ||
      lowerText.includes("imediat")
    ) {
      data.priority = "ALTA";
      data.urgency = 9;
    } else if (
      lowerText.includes("importante") ||
      lowerText.includes("prioritário") ||
      lowerText.includes("prioritario")
    ) {
      data.priority = "MÉDIA";
      data.urgency = 6;
    } else if (
      lowerText.includes("revisar") ||
      lowerText.includes("analisar") ||
      lowerText.includes("quando possível")
    ) {
      data.priority = "BAIXA";
      data.urgency = 3;
    }

    // 🔥 MELHORIA 3: Detectar impacto financeiro (ADICIONADO)
    const moneyPatterns = [
      /R\$\s*(\d+[.,]?\d*)/g,
      /US\$\s*(\d+[.,]?\d*)/g,
      /(\d+[.,]?\d*)\s*(mil|milhão|bilhão)/gi,
      /valor.*?(\d+[.,]?\d*)/gi,
      /custo.*?(\d+[.,]?\d*)/gi,
      /investimento.*?(\d+[.,]?\d*)/gi,
    ];

    moneyPatterns.forEach((pattern) => {
      const matches = text.match(pattern);
      if (matches && matches[1]) {
        data.budget_impact = `R$ ${matches[1]}`;
        console.log("💰 Impacto financeiro detectado:", matches[1]);
      } else if (matches) {
        data.budget_impact = matches[0];
        console.log("💰 Impacto financeiro detectado:", matches[0]);
      }
    });

    // 2. Extrai resumo estruturado (procura por padrões comuns)
    const summaryPatterns = [
      /🧠 Resumo Estruturado\s*\n([\s\S]*?)(?=\n📋|\nFollow-ups|$)/i,
      /Síntese da fala:\s*\n([\s\S]*?)(?=\n📋|\nFollow-ups|$)/i,
      /\*\*Resumo:\*\*\s*([\s\S]*?)(?=\n\*\*|$)/i,
    ];

    for (const pattern of summaryPatterns) {
      const match = text.match(pattern);
      if (match && match[1].trim()) {
        data.summary = match[1].trim();
        data.structured_summary = match[1].trim();
        break;
      }
    }

    // Se não encontrou resumo específico, usa as primeiras linhas
    if (!data.summary) {
      const lines = text
        .split("\n")
        .filter((line) => line.trim() && !line.match(/^[#\*\-]/));
      data.summary = lines.slice(0, 3).join("\n").substring(0, 300);
      data.structured_summary = data.summary;
    }

    // 3. Extrai follow-ups (procura lista numerada com **texto**)
    const followupLines = [];
    const lines = text.split("\n");

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();

      // Procura por: 1. **Título do follow-up**
      if (line.match(/^\d+\.\s+\*\*[^*]+\*\*/)) {
        const titleMatch = line.match(/\*\*([^*]+)\*\*/);
        if (titleMatch) {
          let followupText = titleMatch[1].trim();

          // Tenta pegar descrição nas próximas linhas
          for (let j = i + 1; j < Math.min(i + 3, lines.length); j++) {
            const nextLine = lines[j].trim();
            if (
              nextLine &&
              !nextLine.match(/^\d+\./) &&
              !nextLine.includes("**Status:**")
            ) {
              followupText += " - " + nextLine.replace(/^[\s\-\*]+/, "");
            }
          }

          followupLines.push(followupText);
        }
      }
      // Ou procura por lista de follow-ups após título
      else if (line.toLowerCase().includes("follow-ups identificados:")) {
        for (let j = i + 1; j < Math.min(i + 10, lines.length); j++) {
          const nextLine = lines[j].trim();
          if (nextLine && !nextLine.match(/^[A-Z]/) && nextLine.length > 10) {
            followupLines.push(nextLine.replace(/^[\s\-\*•]+/, ""));
          }
        }
      }
    }

    data.followups = followupLines.slice(0, 10);

    // 4. Extrai ações (procura por ✅ ou • ou - no início da linha)
    const actionLines = [];
    for (const line of lines) {
      const trimmedLine = line.trim();
      if (
        trimmedLine.match(/^[✅•\-]\s/) ||
        trimmedLine.toLowerCase().includes("ação") ||
        trimmedLine.toLowerCase().includes("action:") ||
        trimmedLine.toLowerCase().includes("tarefa:") ||
        trimmedLine.toLowerCase().includes("task:")
      ) {
        const cleanAction = trimmedLine.replace(/^[✅•\-\s]+/, "").trim();
        if (cleanAction && cleanAction.length > 5) {
          actionLines.push(cleanAction);
        }
      }
    }

    data.actions = actionLines.slice(0, 8);

    // 5. Tenta identificar diretorias (com base em palavras-chave)
    const directorKeywords = {
      Comercial: [
        "comercial",
        "vendas",
        "cliente",
        "contrato",
        "proposta",
        "comercialização",
      ],
      Tecnologia: [
        "tecnologia",
        "ti",
        "desenvolvimento",
        "software",
        "sistema",
        "api",
        "frontend",
        "backend",
        "dev",
        "programação",
        "infraestrutura",
      ],
      Financeiro: [
        "financeiro",
        "orçamento",
        "custo",
        "investimento",
        "receita",
        "despesa",
        "contabilidade",
        "fluxo de caixa",
        "relatório financeiro",
      ],
      RH: [
        "rh",
        "recursos humanos",
        "equipe",
        "colaborador",
        "treinamento",
        "funcionário",
        "talentos",
      ],
      Marketing: [
        "marketing",
        "divulgação",
        "campanha",
        "branding",
        "publicidade",
        "mídia",
        "redes sociais",
      ],
      Operações: [
        "operações",
        "processo",
        "logística",
        "produção",
        "suprimentos",
        "cadeia de suprimentos",
      ],
      Jurídico: [
        "jurídico",
        "legal",
        "contrato",
        "conformidade",
        "regulatório",
      ],
      Produto: [
        "produto",
        "product",
        "features",
        "funcionalidades",
        "lançamento",
      ],
    };

    const foundDirectors = [];
    const lowerTextForDirectors = text.toLowerCase();

    for (const [director, keywords] of Object.entries(directorKeywords)) {
      if (keywords.some((keyword) => lowerTextForDirectors.includes(keyword))) {
        foundDirectors.push(director);
      }
    }

    data.directors = foundDirectors;

    // 6. Tenta identificar ritos
    const ritualKeywords = [
      "daily",
      "weekly",
      "sprint",
      "review",
      "retrospective",
      "planning",
      "standup",
      "reunião",
      "meeting",
      "workshop",
      "alinhamento",
      "checkpoint",
      "sync",
    ];
    const foundRituals = [];

    for (const keyword of ritualKeywords) {
      if (lowerText.includes(keyword)) {
        const formattedRitual =
          keyword.charAt(0).toUpperCase() + keyword.slice(1);
        if (!foundRituals.includes(formattedRitual)) {
          foundRituals.push(formattedRitual);
        }
      }
    }

    data.rituals = foundRituals;

    // 🔥 MELHORIA 4: Detectar complexidade baseada no texto (ADICIONADO)
    const wordCount = text.split(/\s+/).length;
    const hasMultipleTopics = (text.match(/\d+\./g) || []).length > 2;
    const hasMultiplePeople =
      (text.match(/(equipe|time|colaborador|funcionário)/gi) || []).length > 1;

    if (wordCount > 200 || hasMultipleTopics || hasMultiplePeople) {
      data.complexity = 7;
      data.impact = 8;
    } else if (wordCount > 100) {
      data.complexity = 5;
      data.impact = 6;
    } else {
      data.complexity = 3;
      data.impact = 4;
    }

    console.log("✅ Dados extraídos com melhorias:", {
      hashtags: data.hashtags.length,
      summaryLength: data.summary?.length,
      followups: data.followups.length,
      actions: data.actions.length,
      directors: data.directors,
      rituals: data.rituals,
      priority: data.priority,
      deadline: data.deadline,
      budgetImpact: data.budget_impact,
      complexity: data.complexity,
      impact: data.impact,
    });

    return data;
  };

  // 🔥 CORREÇÃO: normalizeExecutiveData mais robusta
  const normalizeExecutiveData = (data, originalText) => {
    console.log("🔧 Normalizando dados executivos:", {
      inputType: typeof data,
      isObject: typeof data === "object",
      keys: typeof data === "object" ? Object.keys(data) : "n/a",
    });

    // Caso 1: data é string (texto ou JSON string)
    if (typeof data === "string") {
      console.log("📝 Data é string, tentando processar...");

      // Tenta parsear como JSON primeiro
      try {
        const parsed = JSON.parse(data);
        console.log("✅ String é JSON válido");

        // Se for JSON, usa mas garante estrutura
        return {
          hashtags: Array.isArray(parsed.hashtags)
            ? parsed.hashtags
            : parsed.tags
              ? parsed.tags
              : [],
          summary:
            parsed.summary ||
            parsed.structured_summary ||
            parsed.content ||
            "Análise executiva processada",
          structured_summary: parsed.structured_summary || parsed.summary || "",
          followups: Array.isArray(parsed.followups) ? parsed.followups : [],
          rituals: Array.isArray(parsed.rituals)
            ? parsed.rituals
            : parsed.ritual
              ? Array.isArray(parsed.ritual)
                ? parsed.ritual
                : [parsed.ritual]
              : [],
          directors: Array.isArray(parsed.directors)
            ? parsed.directors
            : parsed.departments || [],
          actions: Array.isArray(parsed.actions)
            ? parsed.actions
            : parsed.actions_required || parsed.tasks || [],
          register_location:
            parsed.register_location || parsed.where_to_register || "DailyLog",
          // 🔥 MELHORIA: Incluir dados extras se existirem
          deadline: parsed.deadline,
          priority: parsed.priority,
          urgency: parsed.urgency,
          impact: parsed.impact,
          complexity: parsed.complexity,
          budget_impact: parsed.budget_impact,
          raw_text: originalText,
        };
      } catch (e) {
        console.log("📝 String não é JSON, extraindo do texto");
        return extractExecutiveDataFromText(data);
      }
    }

    // Caso 2: data é objeto
    if (data && typeof data === "object") {
      console.log("📦 Data é objeto, verificando estrutura...");

      // Verifica se tem campos mínimos
      const hasExecutiveFields =
        data.hashtags ||
        data.summary ||
        data.followups ||
        data.actions ||
        data.content;

      if (!hasExecutiveFields) {
        console.log(
          "⚠️ Objeto sem campos executivos, extraindo do texto original",
        );
        return extractExecutiveDataFromText(originalText);
      }

      // Garante estrutura mínima com fallbacks
      return {
        hashtags: Array.isArray(data.hashtags)
          ? data.hashtags
          : data.tags
            ? data.tags
            : ["Executivo"],
        summary:
          data.summary ||
          data.structured_summary ||
          data.content ||
          "Análise executiva processada",
        structured_summary: data.structured_summary || data.summary || "",
        followups: Array.isArray(data.followups) ? data.followups : [],
        rituals: Array.isArray(data.rituals)
          ? data.rituals
          : data.ritual
            ? Array.isArray(data.ritual)
              ? data.ritual
              : [data.ritual]
            : [],
        directors: Array.isArray(data.directors)
          ? data.directors
          : data.departments || [],
        actions: Array.isArray(data.actions)
          ? data.actions
          : data.actions_required || data.tasks || [],
        register_location:
          data.register_location || data.where_to_register || "DailyLog",
        // 🔥 MELHORIA: Incluir dados extras
        deadline: data.deadline,
        priority: data.priority,
        urgency: data.urgency,
        impact: data.impact,
        complexity: data.complexity,
        budget_impact: data.budget_impact,
        // 🔥 CORREÇÃO: raw_text não contém JSON
        raw_text:
          originalText && originalText.length > 500
            ? originalText.substring(0, 500) + "..."
            : originalText,
      };
    }

    // Caso 3: data é null/undefined ou outro tipo
    console.log("❌ Data é inválido, usando fallback");
    return {
      hashtags: ["Sistema"],
      summary: "Análise executiva processada automaticamente",
      structured_summary: "",
      followups: [],
      rituals: [],
      directors: [],
      actions: [],
      register_location: "DailyLog",
      raw_text: originalText || "Sem dados disponíveis",
    };
  };

  // =============================
  // STATUS + CONTEXTO DA IA
  // =============================
  useEffect(() => {
    checkAIStatus();
  }, []);

  useEffect(() => {
    if (user?.id) {
      loadAIContext(user.id);
    }
  }, [user?.id]);

  const checkAIStatus = async () => {
    try {
      await api.get("/health");
      setAiStatus("online");
    } catch {
      setAiStatus("offline");
    }
  };

  const loadAIContext = async (userId) => {
    try {
      const context = await getAIContext(userId);
      setAiContext(context);
    } catch (err) {
      console.error("Erro ao carregar contexto IA:", err);
      setAiContext(null);
    }
  };

  // =============================
  // AUTO SCROLL
  // =============================
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const formatTime = (dateString) =>
    new Date(dateString).toLocaleTimeString("pt-BR", {
      hour: "2-digit",
      minute: "2-digit",
    });

  // =============================
  // ENVIO DE MENSAGEM
  // =============================
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isTyping || !user?.id) {
      console.log("⏸️ [CHAT] Envio bloqueado - sem input ou usuário");
      return;
    }

    const userMessage = {
      id: Date.now(),
      role: "user",
      type: mode,
      content: inputMessage,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const messageToSend = inputMessage;
    setInputMessage("");
    setIsTyping(true);

    const safeContext = aiContext || {};

    try {
      const token = localStorage.getItem("token") || "";
      const backendURL = "http://localhost:8080";

      console.log(`🚀 Enviando mensagem (modo: ${mode})...`);

      const fetchResponse = await fetch(`${backendURL}/api/v1/chat`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          message: messageToSend,
          context: safeContext,
          mode: mode === "executive" ? "bullet_journal_ceo" : undefined,
        }),
      });

      console.log("📡 Status da resposta:", fetchResponse.status);

      if (!fetchResponse.ok) {
        let errorText = "Erro desconhecido";
        try {
          errorText = await fetchResponse.text();
        } catch {}
        throw new Error(
          `HTTP ${fetchResponse.status}: ${errorText.substring(0, 100)}`,
        );
      }

      const responseData = await fetchResponse.json();
      console.log("✅ Resposta recebida, processando...");

      const replyText =
        responseData.reply ||
        responseData.response ||
        responseData.message ||
        "";

      // =============================
      // 📘 BULLET JOURNAL (CEO) - PROCESSAMENTO CORRIGIDO
      // =============================
      if (mode === "executive") {
        console.log("📊 Processando resposta executiva...");

        let parsedData;
        let isJSON = false;
        let rawResponse = replyText;

        // 🔥 CORREÇÃO: Tenta detectar se a resposta tem JSON embutido
        // Primeiro tenta parsear direto
        try {
          parsedData = JSON.parse(replyText);
          isJSON = true;
          console.log("✅ Resposta é JSON válido");
        } catch (jsonError) {
          console.log(
            "📝 Resposta não é JSON puro, verificando se tem JSON dentro",
          );

          // Tenta encontrar JSON dentro do texto
          const jsonMatch = replyText.match(/\{[\s\S]*\}/);
          if (jsonMatch) {
            try {
              parsedData = JSON.parse(jsonMatch[0]);
              isJSON = true;
              console.log("✅ Encontrou JSON dentro do texto");
              rawResponse = replyText.replace(jsonMatch[0], "").trim();
            } catch (e) {
              console.log("❌ JSON dentro do texto é inválido");
              parsedData = replyText;
            }
          } else {
            parsedData = replyText;
          }
        }

        // Normaliza os dados
        const normalizedData = normalizeExecutiveData(parsedData, rawResponse);

        // 🔥 CORREÇÃO: Adiciona hashtags inteligentes se necessário
        if (normalizedData.hashtags.length === 0) {
          // Detecta automaticamente hashtags baseadas no conteúdo
          const textForDetection = rawResponse.toLowerCase();

          if (
            textForDetection.includes("follow-up") ||
            textForDetection.includes("followup")
          ) {
            normalizedData.hashtags = ["Followups"];
          } else if (
            textForDetection.includes("reunião") ||
            textForDetection.includes("meeting")
          ) {
            normalizedData.hashtags = ["Reuniões"];
          } else if (
            textForDetection.includes("estratégia") ||
            textForDetection.includes("estratégico")
          ) {
            normalizedData.hashtags = ["Estratégia"];
          } else if (
            textForDetection.includes("tarefa") ||
            textForDetection.includes("task")
          ) {
            normalizedData.hashtags = ["Tarefas"];
          } else if (
            textForDetection.includes("decisão") ||
            textForDetection.includes("decision")
          ) {
            normalizedData.hashtags = ["Decisões"];
          } else if (
            textForDetection.includes("financeiro") ||
            textForDetection.includes("orçamento")
          ) {
            normalizedData.hashtags = ["Financeiro"];
          } else if (
            textForDetection.includes("projeto") ||
            textForDetection.includes("project")
          ) {
            normalizedData.hashtags = ["Projetos"];
          } else {
            normalizedData.hashtags = ["Executivo"];
          }
        }

        console.log("🎯 Dados normalizados para ExecutiveBlock:", {
          hashtags: normalizedData.hashtags,
          summaryLength: normalizedData.summary?.length,
          followupsCount: normalizedData.followups?.length,
          actionsCount: normalizedData.actions?.length,
          priority: normalizedData.priority,
          deadline: normalizedData.deadline,
          hasRawText: !!normalizedData.raw_text,
          rawTextLength: normalizedData.raw_text?.length,
        });

        // 🔥 CORREÇÃO: Garante que os dados sejam passados corretamente
        const executiveMessage = {
          id: Date.now() + 1,
          role: "assistant",
          type: "executive",
          data: normalizedData,
          timestamp: new Date().toISOString(),
          // 🔥 Adiciona fallback de conteúdo para compatibilidade
          content: normalizedData.summary || "Análise executiva processada",
        };

        console.log("💾 Salvando mensagem executiva:", {
          hasData: !!executiveMessage.data,
          dataKeys: Object.keys(executiveMessage.data || {}),
        });

        setMessages((prev) => [...prev, executiveMessage]);
      }

      // =============================
      // 💬 CHAT NORMAL
      // =============================
      else {
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now() + 1,
            role: "assistant",
            type: "chat",
            content: replyText,
            timestamp: new Date().toISOString(),
          },
        ]);
      }
    } catch (err) {
      console.error("❌ Erro no chat:", err);

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: "assistant",
          type: "error",
          content: `⚠️ **Erro técnico**\n\n${err.message}`,
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: 1,
        role: "assistant",
        type: "chat",
        content:
          "👋 Nova sessão iniciada.\n\nSelecione Chat ou Bullet Journal Executivo.",
        timestamp: new Date().toISOString(),
      },
    ]);
  };

  // =============================
  // RENDER
  // =============================
  return (
    <div className="chat-page-container">
      <Sidebar />

      <div className="chat-main-area">
        {/* Cabeçalho com estilos do CSS */}
        <div className="chat-header">
          <div className="header-left">
            <h1>MAWDSLEYS</h1>
            <div className={`ai-status ${aiStatus}`}>
              <span className="status-dot"></span>
              {aiStatus === "online"
                ? "IA Online"
                : aiStatus === "offline"
                  ? "IA Offline"
                  : "Verificando..."}
            </div>
          </div>

          <div className="header-right">
            <div className="chat-metrics">
              <div className="metric">
                <div className="metric-value">{messages.length}</div>
                <div className="metric-label">Mensagens</div>
              </div>
              <div className="metric">
                <div
                  className="metric-value"
                  style={{
                    color:
                      aiStatus === "online"
                        ? "#22c55e"
                        : aiStatus === "offline"
                          ? "#ef4444"
                          : "#fbbf24",
                  }}
                >
                  {aiStatus === "online"
                    ? "✓"
                    : aiStatus === "offline"
                      ? "✗"
                      : "?"}
                </div>
                <div className="metric-label">Status</div>
              </div>
            </div>

            <div className="action-buttons">
              <select
                value={mode}
                onChange={(e) => setMode(e.target.value)}
                className="action-btn"
                style={{
                  background: "rgba(59, 130, 246, 0.15)",
                  color: "#60a5fa",
                  border: "1px solid rgba(59, 130, 246, 0.3)",
                  padding: "10px 16px",
                  borderRadius: "10px",
                  fontWeight: "600",
                  fontSize: "13px",
                  cursor: "pointer",
                  minWidth: "200px",
                }}
              >
                <option value="chat">💬 Chat Normal</option>
                <option value="executive">📘 Bullet Journal (CEO)</option>
              </select>

              <button
                className="clear-btn"
                onClick={clearChat}
                disabled={isTyping}
              >
                🗑️ Nova Sessão
              </button>

              <button
                className="action-btn"
                onClick={() => {
                  console.log("🔧 Debug completo:");
                  console.log("- User:", user);
                  console.log(
                    "- Token:",
                    localStorage.getItem("token")?.substring(0, 20) + "...",
                  );
                  console.log("- Backend URL:", "http://localhost:8080");
                  console.log("- AI Status:", aiStatus);
                  console.log("- Modo atual:", mode);
                  console.log("- Contexto AI:", aiContext);
                  console.log(
                    "- Última mensagem executiva:",
                    messages.find((m) => m.type === "executive"),
                  );

                  // Teste rápido do backend
                  fetch("http://localhost:8080/health")
                    .then((r) => r.json())
                    .then((data) => console.log("✅ Backend health:", data))
                    .catch((e) => console.error("❌ Backend error:", e));
                }}
              >
                🔧 Debug
              </button>
            </div>
          </div>
        </div>

        {/* 🔥 Indicador de Modo */}
        <div
          className="mode-indicator"
          style={{
            background:
              mode === "executive"
                ? "linear-gradient(90deg, #0f766e, #0e7490)"
                : "linear-gradient(90deg, #1e40af, #3730a3)",
            padding: "10px 20px",
            borderRadius: "10px",
            marginBottom: "20px",
            display: "flex",
            alignItems: "center",
            gap: "12px",
            borderLeft: `4px solid ${mode === "executive" ? "#14b8a6" : "#3b82f6"}`,
          }}
        >
          <span style={{ fontSize: "22px" }}>
            {mode === "executive" ? "📘" : "💬"}
          </span>
          <div style={{ flex: 1 }}>
            <strong style={{ color: "white", fontSize: "14px" }}>
              {mode === "executive"
                ? "Modo Executivo (Bullet Journal)"
                : "Modo Chat Normal"}
            </strong>
            <div style={{ fontSize: "12px", opacity: 0.8, color: "#e2e8f0" }}>
              {mode === "executive"
                ? "Reflexões são transformadas em ações estruturadas"
                : "Conversa natural com o assistente"}
            </div>
          </div>
          <div
            style={{
              background:
                mode === "executive"
                  ? "rgba(20, 184, 166, 0.2)"
                  : "rgba(59, 130, 246, 0.2)",
              padding: "4px 10px",
              borderRadius: "6px",
              fontSize: "11px",
              fontWeight: "bold",
              color: mode === "executive" ? "#14b8a6" : "#60a5fa",
            }}
          >
            {mode === "executive" ? "EXECUTIVO" : "NORMAL"}
          </div>
        </div>

        {/* Sugestões Inteligentes */}
        {messages.length <= 2 && (
          <div className="suggestions-section">
            <p className="section-description">
              Comece uma conversa com sugestões inteligentes:
            </p>
            <div className="suggestions-grid">
              <button
                className="suggestion-card"
                onClick={() => {
                  setInputMessage("Quais são meus follow-ups pendentes?");
                  setTimeout(() => handleSendMessage(), 100);
                }}
                disabled={isTyping}
              >
                <div className="suggestion-icon">📋</div>
                <div className="suggestion-content">
                  <div className="suggestion-title">Follow-ups Pendentes</div>
                  <div className="suggestion-prompt">
                    Verifique suas tarefas pendentes e prazos
                  </div>
                </div>
              </button>

              <button
                className="suggestion-card"
                onClick={() => {
                  setInputMessage("Resuma minhas reuniões da semana");
                  setTimeout(() => handleSendMessage(), 100);
                }}
                disabled={isTyping}
              >
                <div className="suggestion-icon">📅</div>
                <div className="suggestion-content">
                  <div className="suggestion-title">Resumo Semanal</div>
                  <div className="suggestion-prompt">
                    Análise das reuniões e decisões importantes
                  </div>
                </div>
              </button>

              <button
                className="suggestion-card"
                onClick={() => {
                  setInputMessage(
                    "Registre um pensamento executivo sobre estratégia",
                  );
                  setMode("executive");
                  setTimeout(() => handleSendMessage(), 100);
                }}
                disabled={isTyping}
              >
                <div className="suggestion-icon">💡</div>
                <div className="suggestion-content">
                  <div className="suggestion-title">Bullet Journal</div>
                  <div className="suggestion-prompt">
                    Registre reflexões e transforme em ações
                  </div>
                </div>
              </button>
            </div>
          </div>
        )}

        {/* Área de mensagens */}
        <div className="messages-container">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`message-wrapper ${
                message.role === "user"
                  ? "user-message"
                  : message.type === "error"
                    ? "error-message"
                    : "bot-message"
              }`}
            >
              <div className="message-avatar">
                {message.role === "user"
                  ? "👤"
                  : message.type === "error"
                    ? "❌"
                    : "🤖"}
              </div>

              <div className="message-content">
                <div className="message-header">
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                    }}
                  >
                    <strong
                      style={{
                        color:
                          message.role === "user"
                            ? "#60a5fa"
                            : message.type === "error"
                              ? "#f87171"
                              : "#ffffff",
                      }}
                    >
                      {message.role === "user"
                        ? "Você"
                        : message.type === "error"
                          ? "Erro"
                          : "MAWDSLEYS"}
                    </strong>
                    {message.type === "executive" && (
                      <span
                        style={{
                          background: "rgba(20, 184, 166, 0.2)",
                          color: "#14b8a6",
                          padding: "2px 8px",
                          borderRadius: "4px",
                          fontSize: "10px",
                          fontWeight: "bold",
                          border: "1px solid rgba(20, 184, 166, 0.3)",
                        }}
                      >
                        📘 Executivo
                      </span>
                    )}
                  </div>
                  <span className="message-time">
                    {formatTime(message.timestamp)}
                  </span>
                </div>

                {message.type === "executive" && (
                  <div className="message-context">
                    📊 Análise executiva gerada
                  </div>
                )}

                <div
                  className="message-text"
                  style={{
                    color:
                      message.type === "error"
                        ? "#f87171"
                        : message.role === "user"
                          ? "#dbeafe"
                          : "#e2e8f0",
                  }}
                >
                  {message.type === "executive" ? (
                    // 🔥 CORREÇÃO: Passa data corretamente e adiciona fallback
                    <ExecutiveBlock
                      data={message.data || { summary: message.content }}
                    />
                  ) : (
                    <div style={{ whiteSpace: "pre-wrap" }}>
                      {message.content}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="typing-indicator">
              <div className="typing-header">
                <span className="typing-sender">MAWDSLEYS</span>
                <span className="typing-model">
                  {mode === "executive"
                    ? "📘 Processando Executivo"
                    : "💬 Processando"}
                </span>
              </div>
              <div className="typing-animation">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <span className="typing-text">
                  {mode === "executive"
                    ? "📊 Analisando reflexão executiva..."
                    : "💬 Processando sua mensagem..."}
                </span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input area - usando componente ChatInput */}
        <ChatInput
          value={inputMessage}
          onChange={setInputMessage}
          onSend={handleSendMessage}
          onKeyPress={handleKeyPress}
          isTyping={isTyping}
          aiStatus={aiStatus}
          mode={mode}
        />

        {/* Informações técnicas */}
        <div className="tech-info">
          <div className="tech-card">
            <h4>⚙️ Informações do Sistema</h4>
            <ul>
              <li>
                <span>Backend:</span>
                <strong>localhost:8080</strong>
              </li>
              <li>
                <span>Status:</span>
                <strong className={`status-${aiStatus}`}>
                  {aiStatus === "online"
                    ? "✅ Online"
                    : aiStatus === "offline"
                      ? "❌ Offline"
                      : "⏳ Verificando"}
                </strong>
              </li>
              <li>
                <span>Modo Atual:</span>
                <strong>
                  {mode === "executive" ? "📘 Executivo" : "💬 Normal"}
                </strong>
              </li>
              <li>
                <span>Mensagens:</span>
                <strong>{messages.length}</strong>
              </li>
            </ul>
          </div>

          <div className="tech-card">
            <h4>🔗 Conexões</h4>
            <ul>
              <li>
                <span>Usuário:</span>
                <strong>{user?.name || "Não logado"}</strong>
              </li>
              <li>
                <span>ID:</span>
                <strong>{user?.id || "-"}</strong>
              </li>
              <li>
                <span>Token:</span>
                <strong>
                  {localStorage.getItem("token") ? "✅ Presente" : "❌ Ausente"}
                </strong>
              </li>
              <li>
                <span>Conexão:</span>
                <strong>
                  {aiStatus === "online"
                    ? "🟢 Estável"
                    : aiStatus === "offline"
                      ? "🔴 Interrompida"
                      : "🟡 Testando"}
                </strong>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
