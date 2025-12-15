import React, { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import api from "../services/api";


export default function KnowledgeBase() {
  const [docs, setDocs] = useState([]);

  useEffect(() => {
    load();
  }, []);

  async function load() {
    try {
      const res = await api.get("/documents/");
      setDocs(res.data || []);
    } catch (e) {
      console.error("Erro ao carregar documentos:", e);

      // fallback caso API falhe
      setDocs([
        {
          id: 1,
          title: "Política de Segurança",
          excerpt: "Resumo da política interna...",
        },
      ]);
    }
  }

  return (
    <div style={styles.container}>
      <Sidebar />

      <div style={styles.main}>
        <h1 style={styles.title}>Base de Conhecimento</h1>

        <div style={{ marginTop: 20 }}>
          {docs.map((d) => (
            <div key={d.id} style={styles.card} className="card">
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <div>
                  <div style={styles.cardTitle}>{d.title}</div>
                  <div style={styles.cardExcerpt}>
                    {d.excerpt || "Documento interno"}
                  </div>
                </div>

                <button className="btn" style={styles.button}>
                  Abrir
                </button>
              </div>
            </div>
          ))}

          {docs.length === 0 && (
            <p style={styles.empty}>Nenhum documento cadastrado.</p>
          )}
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    minHeight: "100vh",
    background: "var(--bg-primary)",
  },
  main: {
    marginLeft: 260,
    padding: 35,
    width: "100%",
  },
  title: {
    fontSize: "28px",
    fontWeight: "bold",
  },
  card: {
    marginBottom: "15px",
    padding: "20px",
    borderRadius: "var(--radius)",
    background: "var(--bg-card)",
    boxShadow: "var(--shadow)",
  },
  cardTitle: {
    fontWeight: 700,
    fontSize: "18px",
  },
  cardExcerpt: {
    fontSize: "13px",
    color: "var(--text-secondary)",
    marginTop: 4,
  },
  button: {
    height: "36px",
    alignSelf: "center",
  },
  empty: {
    marginTop: 20,
    fontSize: "14px",
    color: "var(--text-secondary)",
  },
};
