//📄 frontend/src/pages/ActivityDetail.jsx
import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { getActivityLog } from "@/services/activityLog";

export default function ActivityDetail() {
  const { id } = useParams();
  const [log, setLog] = useState(null);

  useEffect(() => {
    getActivityLog(id).then((res) => setLog(res.data));
  }, [id]);

  if (!log) return <p>Carregando…</p>;

  return (
    <div>
      <h2>Evento</h2>
      <pre>{JSON.stringify(log, null, 2)}</pre>
    </div>
  );
}
