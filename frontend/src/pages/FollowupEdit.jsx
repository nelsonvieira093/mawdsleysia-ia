//E:\MAWDSLEYS-AGENTE\frontend\src\pages\FollowupEdit.jsx

import { useParams, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { getFollowup, updateFollowup } from "@/services/followups";
import "./FollowupEdit.css";

export default function FollowupEdit() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    title: "",
    description: "",
    due_date: "",
    priority: "",
    status: "",
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  // 🔹 Carregar follow-up
  useEffect(() => {
    async function load() {
      try {
        const res = await getFollowup(id);
        const data = res.data?.data || {};

        setForm({
          title: data.title || "",
          description: data.description || "",
          due_date: data.due_date || "",
          priority: data.priority || "",
          status: data.status || "",
        });
      } catch (err) {
        console.error(err);
        setError("Erro ao carregar follow-up");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [id]);

  // 🔹 Salvar edição
  const save = async () => {
    if (saving) return; // 🔒 evita clique duplo / travamento

    setSaving(true);
    setError(null);

    try {
      await updateFollowup(id, {
        title: form.title,
        description: form.description,
        due_date: form.due_date,
        priority: form.priority,
        status: form.status,
      });

      navigate(`/followups/${id}`);
    } catch (err) {
      console.error(err);
      setError("Erro ao salvar follow-up");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <p className="followup-loading">Carregando…</p>;
  }

  return (
    <div className="followup-edit-container">
      <div className="followup-edit-card">
        <h2>Editar Follow-up</h2>

        {error && <p className="error">{error}</p>}

        <label>
          Título
          <input
            placeholder="Título"
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
          />
        </label>

        <label>
          Descrição
          <textarea
            placeholder="Descrição"
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
          />
        </label>

        <div className="actions">
          <button type="button" onClick={save} disabled={saving}>
            {saving ? "Salvando..." : "Salvar"}
          </button>

          <button
            type="button"
            className="cancel"
            onClick={() => navigate(`/followups/${id}`)}
            disabled={saving}
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
}
