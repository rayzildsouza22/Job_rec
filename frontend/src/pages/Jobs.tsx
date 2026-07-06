import { FormEvent, useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { listJobs } from "../Services/JobService";
import { saveJob } from "../Services/SavedJobService";
import type { Job } from "../types/domain";

function Jobs() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [q, setQ] = useState("");
  const [location, setLocation] = useState("");
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState<Record<number, boolean>>({});

  async function load(search?: string, loc?: string) {
    setLoading(true);
    try {
      const data = await listJobs(search, loc);
      setJobs(data);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleSearch(event: FormEvent) {
    event.preventDefault();
    load(q || undefined, location || undefined);
  }

  async function handleSave(jobId: number) {
    await saveJob(jobId);
    setSaved((prev) => ({ ...prev, [jobId]: true }));
  }

  return (
    <section>
      <p className="eyebrow">JOBS</p>
      <h1>Job catalogue</h1>
      <form className="filter-bar" onSubmit={handleSearch}>
        <input
          placeholder="Keyword (title, company, skill, ...)"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />
        <input
          placeholder="Location"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
        />
        <button>Search</button>
      </form>
      {loading ? (
        <p>Loading...</p>
      ) : jobs.length === 0 ? (
        <p>No jobs found.</p>
      ) : (
        <ul className="cards">
          {jobs.map((job) => (
            <li key={job.id} className="card job-card">
              <h3>
                <Link to={`/jobs/${job.id}`}>{job.title}</Link>
              </h3>
              <p className="muted">
                {job.company} • {job.location || "—"} • {job.experience || "—"}
              </p>
              <p>{job.description.slice(0, 220)}...</p>
              <p><strong>Skills:</strong> {job.required_skills}</p>
              <div className="actions">
                <Link to={`/jobs/${job.id}`}>View</Link>
                <button
                  className="secondary"
                  onClick={() => handleSave(job.id)}
                  disabled={saved[job.id]}
                >
                  {saved[job.id] ? "Saved" : "Save"}
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export default Jobs;
