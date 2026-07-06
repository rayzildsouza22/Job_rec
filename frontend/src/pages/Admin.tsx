import { FormEvent, useEffect, useState } from "react";

import { createJob, deleteJob, listJobs } from "../Services/JobService";
import type { Job } from "../types/domain";

const empty = {
  company: "",
  title: "",
  description: "",
  required_skills: "",
  location: "",
  experience: "",
  salary: "",
};

function Admin() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [form, setForm] = useState({ ...empty });
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");

  async function load() {
    setJobs(await listJobs());
  }

  useEffect(() => {
    load();
  }, []);

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      await createJob({ ...form, location: form.location || null, experience: form.experience || null, salary: form.salary || null } as any);
      setForm({ ...empty });
      setMessage("Job created (and embedded in Qdrant).");
      load();
    } catch {
      setMessage("Failed to create job. Are you sure you're an admin?");
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete(id: number) {
    if (!confirm("Delete this job?")) return;
    await deleteJob(id);
    load();
  }

  return (
    <section>
      <p className="eyebrow">ADMIN</p>
      <h1>Manage jobs</h1>
      <form onSubmit={handleCreate} className="card">
        <h3>Add a new job</h3>
        <label>Company <input value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} required /></label>
        <label>Title <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} required /></label>
        <label>Description <textarea rows={4} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} required /></label>
        <label>Required skills (comma-separated) <input value={form.required_skills} onChange={(e) => setForm({ ...form, required_skills: e.target.value })} required /></label>
        <label>Location <input value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} /></label>
        <label>Experience <input value={form.experience} onChange={(e) => setForm({ ...form, experience: e.target.value })} /></label>
        <label>Salary <input value={form.salary} onChange={(e) => setForm({ ...form, salary: e.target.value })} /></label>
        {message && <p>{message}</p>}
        <button disabled={busy}>{busy ? "Saving..." : "Create job"}</button>
      </form>

      <h3>Existing jobs</h3>
      <ul className="cards">
        {jobs.map((job) => (
          <li key={job.id} className="card job-card">
            <h4>{job.title} <span className="muted">#{job.id}</span></h4>
            <p className="muted">{job.company} • {job.location || "—"}</p>
            <p>{job.description.slice(0, 200)}...</p>
            <button className="secondary" onClick={() => handleDelete(job.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </section>
  );
}

export default Admin;
