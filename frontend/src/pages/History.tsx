import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getHistory } from "../Services/RecommendationService";
import type { RecommendationHistoryItem } from "../types/domain";

function History() {
  const [items, setItems] = useState<RecommendationHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getHistory()
      .then(setItems)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading...</p>;

  return (
    <section>
      <p className="eyebrow">HISTORY</p>
      <h1>Recommendation history</h1>
      {items.length === 0 ? (
        <p>No recommendations generated yet.</p>
      ) : (
        <ul className="cards">
          {items.map((row) => (
            <li key={row.id} className="card">
              <p className="muted">{new Date(row.created_at).toLocaleString()}</p>
              <p>
                <Link to={`/jobs/${row.job_id}`}>Job #{row.job_id}</Link>
                <span className="score"> {(row.similarity * 100).toFixed(1)}% match</span>
              </p>
              <p>{row.explanation}</p>
              <p><strong>Matching:</strong> {row.matching_skills || "—"}</p>
              <p><strong>Missing:</strong> {row.missing_skills || "—"}</p>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default History;
