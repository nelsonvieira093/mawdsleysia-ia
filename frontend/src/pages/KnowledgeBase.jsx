import React, { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import api from "../services/api";

export default function KnowledgeBase() {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    load();
  }, []);

  async function load() {
    try {
      setLoading(true);
      
      // 🎯 CORREÇÃO: Usa a rota CORRETA /knowledge/items
      const [itemsRes, statsRes] = await Promise.allSettled([
        api.get("/knowledge/items"),
        api.get("/knowledge/stats")
      ]);

      console.log("API Responses:", {
        items: itemsRes.status,
        stats: statsRes.status
      });

      // Carrega documentos (itens de conhecimento)
      if (itemsRes.status === "fulfilled" && Array.isArray(itemsRes.value?.data)) {
        console.log("Documentos carregados:", itemsRes.value.data.length);
        setDocs(itemsRes.value.data);
      } else {
        console.log("Usando fallback para documentos");
        setDocs([
          {
            id: "1",
            title: "Política de Segurança",
            excerpt: "Resumo da política interna de segurança da informação.",
            category: "Governança",
            tags: ["segurança", "política"]
          },
          {
            id: "2",
            title: "Manual do Produto X",
            excerpt: "Documentação completa do produto X para clientes e equipe.",
            category: "Produtos",
            tags: ["produto", "manual"]
          },
          {
            id: "3",
            title: "FAQ de Suporte Técnico",
            excerpt: "Perguntas frequentes e soluções para problemas comuns.",
            category: "Suporte",
            tags: ["faq", "suporte", "técnico"]
          },
          {
            id: "4",
            title: "Guia de Integração API",
            excerpt: "Como integrar sistemas externos via nossa API REST.",
            category: "Tecnologia",
            tags: ["api", "integração", "desenvolvimento"]
          },
          {
            id: "5",
            title: "Procedimentos Operacionais",
            excerpt: "Fluxos e procedimentos padrão para operações diárias.",
            category: "Operações",
            tags: ["procedimentos", "sop", "operações"]
          },
        ]);
      }

      // Carrega estatísticas
      if (statsRes.status === "fulfilled" && statsRes.value?.data) {
        setStats(statsRes.value.data);
      }

    } catch (e) {
      console.error("Erro ao carregar base de conhecimento:", e);
      
      // Fallback robusto
      setDocs([
        {
          id: "fallback_1",
          title: "Base de Conhecimento MAWDSLEYS",
          excerpt: "Documentação corporativa e processos internos.",
          category: "Geral",
          tags: ["documentação", "conhecimento"]
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  const handleOpenDoc = (doc) => {
    console.log("Abrindo documento:", doc.title);
    alert(`Abrindo: ${doc.title}\n\n${doc.excerpt || "Sem conteúdo disponível."}`);
    
    // Aqui você pode implementar navegação para detalhes
    // ou modal com conteúdo completo
  };

  const handleSearch = async (query) => {
    try {
      const response = await api.post("/knowledge/search", {
        query: query,
        limit: 10,
        threshold: 0.7
      });
      
      if (response.data?.results) {
        setDocs(response.data.results);
      }
    } catch (error) {
      console.error("Erro na busca:", error);
    }
  };

  const handleChat = async (question) => {
    try {
      const response = await api.post("/knowledge/chat", {
        question: question,
        max_results: 5
      });
      
      if (response.data?.answer) {
        alert(`Resposta do Assistente:\n\n${response.data.answer}`);
      }
    } catch (error) {
      console.error("Erro no chat:", error);
    }
  };

  return (
    <div style={styles.container}>
      <Sidebar />

      <div style={styles.main}>
        <div style={styles.header}>
          <div>
            <h1 style={styles.title}>Base de Conhecimento</h1>
            <p style={styles.subtitle}>
              Documentação corporativa, manuais e FAQs
              {stats && (
                <span style={styles.stats}>
                  • {stats.total_items || docs.length} documentos • {stats.total_bases || 2} bases
                </span>
              )}
            </p>
          </div>

          <div style={styles.headerActions}>
            <button 
              className="btn outline" 
              onClick={() => handleChat("Quais documentos estão disponíveis?")}
              style={{ marginRight: 10 }}
            >
              🤖 Perguntar ao Assistente
            </button>
            <button className="btn" onClick={load}>
              ⟳ Atualizar
            </button>
          </div>
        </div>

        {/* Barra de busca */}
        <div style={styles.searchContainer}>
          <input
            type="text"
            placeholder="Buscar na base de conhecimento (ex: 'como configurar', 'política')..."
            style={styles.searchInput}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && e.target.value.trim()) {
                handleSearch(e.target.value.trim());
              }
            }}
          />
          <button 
            className="btn small"
            onClick={() => {
              const input = document.querySelector('input[type="text"]');
              if (input?.value.trim()) {
                handleSearch(input.value.trim());
              }
            }}
          >
            🔍 Buscar
          </button>
        </div>

        {loading ? (
          <div style={styles.loadingContainer}>
            <div style={styles.spinner}></div>
            <p style={styles.loadingText}>Carregando base de conhecimento...</p>
          </div>
        ) : (
          <>
            {/* Categorias */}
            {stats?.items_by_category && (
              <div style={styles.categories}>
                <h3 style={styles.sectionTitle}>Categorias</h3>
                <div style={styles.categoryList}>
                  {Object.entries(stats.items_by_category).map(([cat, count]) => (
                    <div key={cat} style={styles.categoryBadge}>
                      {cat}: <strong>{count}</strong>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Lista de documentos */}
            <div style={styles.docsGrid}>
              {docs.map((doc) => (
                <div key={doc.id} style={styles.card} className="card">
                  <div style={styles.cardHeader}>
                    <div style={styles.cardCategory}>{doc.category || "Geral"}</div>
                    <div style={styles.cardPriority}>
                      {doc.priority === 1 ? "⭐ Alta" : 
                       doc.priority === 2 ? "📘 Média" : "📘 Baixa"}
                    </div>
                  </div>
                  
                  <div style={styles.cardContent}>
                    <div style={styles.cardTitle}>{doc.title}</div>
                    <div style={styles.cardExcerpt}>
                      {doc.content?.substring(0, 150) || doc.excerpt || "Documento interno..."}
                      {(doc.content?.length > 150 || doc.excerpt?.length > 150) && "..."}
                    </div>
                    
                    <div style={styles.cardTags}>
                      {doc.tags?.slice(0, 3).map(tag => (
                        <span key={tag} style={styles.tag}>{tag}</span>
                      ))}
                      {doc.tags?.length > 3 && (
                        <span style={styles.moreTags}>+{doc.tags.length - 3}</span>
                      )}
                    </div>
                    
                    <div style={styles.cardFooter}>
                      <div style={styles.cardMeta}>
                        {doc.language && <span>🌐 {doc.language}</span>}
                        {doc.source && <span>📚 {doc.source}</span>}
                      </div>
                      <button 
                        className="btn small" 
                        onClick={() => handleOpenDoc(doc)}
                        style={styles.button}
                      >
                        📄 Abrir
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {docs.length === 0 && (
              <div style={styles.emptyState}>
                <div style={styles.emptyIcon}>📚</div>
                <h3>Nenhum documento encontrado</h3>
                <p style={styles.emptyText}>
                  A base de conhecimento está vazia ou a conexão com o servidor falhou.
                </p>
                <button className="btn" onClick={load}>
                  Tentar novamente
                </button>
              </div>
            )}

            {/* Quick Actions */}
            <div style={styles.quickActions}>
              <h3 style={styles.sectionTitle}>Ações Rápidas</h3>
              <div style={styles.actionButtons}>
                <button 
                  className="btn outline"
                  onClick={() => handleChat("Como adicionar um novo documento?")}
                >
                  ➕ Novo Documento
                </button>
                <button 
                  className="btn outline"
                  onClick={() => handleSearch("FAQ")}
                >
                  ❓ Ver FAQs
                </button>
                <button 
                  className="btn outline"
                  onClick={() => {
                    api.get("/knowledge/bases")
                      .then(res => console.log("Bases:", res.data))
                      .catch(err => console.error("Erro:", err));
                  }}
                >
                  📁 Ver Bases
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    minHeight: "100vh",
    background: "var(--bg-primary, #0a0a0a)",
    color: "var(--text-primary, #fff)",
  },
  main: {
    marginLeft: 260,
    padding: "35px",
    width: "100%",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: "30px",
  },
  title: {
    fontSize: "32px",
    fontWeight: "bold",
    marginBottom: "8px",
    background: "linear-gradient(90deg, #4b7cff, #7bed8d)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
  },
  subtitle: {
    fontSize: "16px",
    color: "var(--text-secondary, #aaa)",
    margin: 0,
  },
  stats: {
    marginLeft: "15px",
    color: "#7bed8d",
    fontSize: "14px",
  },
  headerActions: {
    display: "flex",
    gap: "10px",
  },
  searchContainer: {
    display: "flex",
    gap: "10px",
    marginBottom: "30px",
  },
  searchInput: {
    flex: 1,
    padding: "12px 16px",
    borderRadius: "8px",
    border: "1px solid #333",
    background: "rgba(255, 255, 255, 0.05)",
    color: "#fff",
    fontSize: "14px",
  },
  loadingContainer: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    padding: "60px 20px",
  },
  spinner: {
    width: "40px",
    height: "40px",
    border: "3px solid rgba(255, 255, 255, 0.1)",
    borderTop: "3px solid #4b7cff",
    borderRadius: "50%",
    animation: "spin 1s linear infinite",
    marginBottom: "20px",
  },
  loadingText: {
    color: "#aaa",
    fontSize: "14px",
  },
  categories: {
    marginBottom: "30px",
    padding: "20px",
    background: "rgba(255, 255, 255, 0.02)",
    borderRadius: "12px",
    border: "1px solid #222",
  },
  sectionTitle: {
    fontSize: "18px",
    fontWeight: "600",
    marginBottom: "15px",
    color: "#fff",
  },
  categoryList: {
    display: "flex",
    flexWrap: "wrap",
    gap: "10px",
  },
  categoryBadge: {
    padding: "6px 12px",
    background: "rgba(75, 124, 255, 0.1)",
    borderRadius: "20px",
    fontSize: "13px",
    color: "#4b7cff",
    border: "1px solid rgba(75, 124, 255, 0.3)",
  },
  docsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
    gap: "20px",
    marginBottom: "40px",
  },
  card: {
    background: "var(--bg-card, #121212)",
    borderRadius: "12px",
    padding: "20px",
    border: "1px solid #222",
    transition: "all 0.3s ease",
    cursor: "pointer",
    display: "flex",
    flexDirection: "column",
  },
  cardHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: "15px",
  },
  cardCategory: {
    fontSize: "12px",
    color: "#4b7cff",
    fontWeight: "600",
    textTransform: "uppercase",
    letterSpacing: "0.5px",
  },
  cardPriority: {
    fontSize: "11px",
    color: "#ffd166",
    background: "rgba(255, 209, 102, 0.1)",
    padding: "2px 8px",
    borderRadius: "10px",
  },
  cardContent: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
  },
  cardTitle: {
    fontSize: "16px",
    fontWeight: "600",
    marginBottom: "10px",
    color: "#fff",
    lineHeight: "1.4",
  },
  cardExcerpt: {
    fontSize: "13px",
    color: "var(--text-secondary, #aaa)",
    marginBottom: "15px",
    lineHeight: "1.5",
    flex: 1,
  },
  cardTags: {
    display: "flex",
    flexWrap: "wrap",
    gap: "6px",
    marginBottom: "15px",
  },
  tag: {
    fontSize: "11px",
    color: "#7bed8d",
    background: "rgba(123, 237, 141, 0.1)",
    padding: "2px 8px",
    borderRadius: "10px",
  },
  moreTags: {
    fontSize: "11px",
    color: "#aaa",
  },
  cardFooter: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    marginTop: "auto",
  },
  cardMeta: {
    fontSize: "11px",
    color: "#666",
    display: "flex",
    gap: "10px",
  },
  button: {
    padding: "6px 12px",
    fontSize: "12px",
  },
  emptyState: {
    textAlign: "center",
    padding: "60px 20px",
  },
  emptyIcon: {
    fontSize: "48px",
    marginBottom: "20px",
  },
  emptyText: {
    color: "#aaa",
    fontSize: "14px",
    marginBottom: "20px",
    maxWidth: "400px",
    margin: "0 auto 20px",
  },
  quickActions: {
    padding: "25px",
    background: "rgba(255, 255, 255, 0.02)",
    borderRadius: "12px",
    border: "1px solid #222",
  },
  actionButtons: {
    display: "flex",
    gap: "15px",
  },
};

// Adiciona animação do spinner
const styleSheet = document.createElement("style");
styleSheet.textContent = `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;
document.head.appendChild(styleSheet);