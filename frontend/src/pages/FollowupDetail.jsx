import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { getFollowup } from "@/services/followups";

export default function FollowupDetail() {
  const { id } = useParams();
  const [followup, setFollowup] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await getFollowup(id);
        const data = res.data?.data; // ✅ ponto correto
        setFollowup(data || null);
      } catch (err) {
        console.error("Erro ao carregar follow-up:", err);
        setFollowup(null);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [id]);

  if (loading) return <p>Carregando...</p>;
  if (!followup) return <p>Follow-up não encontrado.</p>;

  return (
    <div>
      <h2>{followup.title || "Sem título"}</h2>
      <p>{followup.description || "—"}</p>

      <p>Status: {followup.status || "—"}</p>
      <p>Prioridade: {followup.priority || "—"}</p>
      <p>Prazo: {followup.due_date || "—"}</p>
    </div>
  );
}
