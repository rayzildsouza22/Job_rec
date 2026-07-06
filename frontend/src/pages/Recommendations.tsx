import axios from "axios";
import { useState } from "react";
import { Link } from "react-router-dom";

import { generateRecommendations } from "../Services/RecommendationService";
import { saveJob } from "../Services/SavedJobService";
import type { RecommendationItem } from "../types/domain";

function Recommendations() {
  const [items, setItems] = useState<RecommendationItem[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function handleGenerate() {
    setBusy(true);
    setError("");
    try {
      const data = await generateRecommendations(5);
      setItems(data);
      if (data.length === 0) {
        setError("No matches yet. Ask an admin to add jobs to the catalogue.");
      }
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || "Could not generate recommendations.");
      } else {
        setError("Could not generate recommendations.");
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <section>
      <p className="eyebrow">AI RECOMMENDATIONS</p>
      <h1>Personalised job matches</h1>
      <p>
        Uses your resume + profile, embeds it with Sentence Transformers, retrieves
        the closest jobs from Qdrant, then asks Groq (via LangChain) to explain the
        match.
      </p>
      <button onClick={handleGenerate} disabled={busy}>
        {busy ? "Thinking..." : "Generate recommendations"}
      </button>
      {error && <p className="error">{error}</p>}
      <ul className="cards">
        {items.map((item) => (
          <li key={item.job.id} className="card job-card">
            <h3>
              <Link to={`/jobs/${item.job.id}`}>{item.job.title}</Link>
              <span className="score">{(item.similarity * 100).toFixed(1)}% match</span>
            </h3>
            <p className="muted">
              {item.job.company} • {item.job.location || "—"}
            </p>
            <p><strong>Why:</strong> {item.explanation}</p>
            <p><strong>Matching:</strong> {item.matching_skills.join(", ") || "—"}</p>
            <p><strong>Missing:</strong> {item.missing_skills.join(", ") || "—"}</p>
            <div className="actions">
              <button className="secondary" onClick={() => saveJob(item.job.id)}>
                Save
              </button>
              <Link className="button-link" to={`/skill-gap/${item.job.id}`}>
                Skill gap
              </Link>
            </div>
          </li>
        ))}
      </ul>
      <p className="muted">
        Note: the score is Qdrant cosine similarity, not a hiring probability.
      </p>
    </section>
  );
}

export default Recommendations;
