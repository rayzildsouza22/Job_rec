import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { listSavedJobs, unsaveJob } from "../Services/SavedJobService";
import type { SavedJob } from "../types/domain";

function SavedJobs() {
  const [items, setItems] = useState<SavedJob[]>([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      setItems(await listSavedJobs());
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleRemove(jobId: number) {
    await unsaveJob(jobId);
    setItems((prev) => prev.filter((row) => row.job.id !== jobId));
  }

  if (loading) return <p>Loading...</p>;

  return (
    <section>
      <p className="eyebrow">SAVED JOBS</p>
      <h1>Your bookmarks</h1>
      {items.length === 0 ? (
        <p>You haven't saved any jobs yet.</p>
      ) : (
        <ul className="cards">
          {items.map((row) => (
            <li key={row.id} className="card job-card">
              <h3>
                <Link to={`/jobs/${row.job.id}`}>{row.job.title}</Link>
              </h3>
              <p className="muted">{row.job.company} • {row.job.location || "—"}</p>
              <p><strong>Skills:</strong> {row.job.required_skills}</p>
              <button className="secondary" onClick={() => handleRemove(row.job.id)}>
                Remove
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default SavedJobs;
