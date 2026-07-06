import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getJob } from "../Services/JobService";
import { saveJob } from "../Services/SavedJobService";
import type { Job } from "../types/domain";

function JobDetails() {
  const { id } = useParams();
  const [job, setJob] = useState<Job | null>(null);
  const [savedFlag, setSavedFlag] = useState(false);

  useEffect(() => {
    if (!id) return;
    getJob(Number(id)).then(setJob).catch(() => setJob(null));
  }, [id]);

  async function handleSave() {
    if (!job) return;
    await saveJob(job.id);
    setSavedFlag(true);
  }

  if (!job) return <p>Loading...</p>;

  return (
    <section className="card wide">
      <p className="eyebrow">JOB</p>
      <h1>{job.title}</h1>
      <p className="muted">
        {job.company} • {job.location || "—"} • {job.experience || "—"} • {job.salary || "—"}
      </p>
      <h3>Description</h3>
      <p style={{ whiteSpace: "pre-wrap" }}>{job.description}</p>
      <h3>Required skills</h3>
      <p>{job.required_skills}</p>
      <div className="actions">
        <button onClick={handleSave} disabled={savedFlag}>
          {savedFlag ? "Saved" : "Save job"}
        </button>
        <Link className="button-link" to={`/skill-gap/${job.id}`}>
          Skill gap analysis
        </Link>
      </div>
    </section>
  );
}

export default JobDetails;
