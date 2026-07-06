import axios from "axios";
import { FormEvent, useEffect, useState } from "react";

import {
  deleteMyResume,
  getMyResume,
  uploadResume,
} from "../Services/ResumeService";
import type { Resume } from "../types/domain";

function ResumeUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [resume, setResume] = useState<Resume | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    getMyResume().then(setResume).catch(() => setResume(null));
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!file) {
      setError("Choose a PDF file first.");
      return;
    }
    setBusy(true);
    setMessage("");
    setError("");
    try {
      const uploaded = await uploadResume(file);
      setResume(uploaded);
      setFile(null);
      setMessage("Resume uploaded and text extracted.");
    } catch (err) {
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || "Upload failed.");
      } else {
        setError("Upload failed.");
      }
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete() {
    if (!confirm("Delete your current resume?")) return;
    await deleteMyResume();
    setResume(null);
    setMessage("Resume deleted.");
  }

  return (
    <section className="card wide">
      <p className="eyebrow">RESUME</p>
      <h1>Upload your resume</h1>
      <p>PDF only, up to 5 MB. Text is extracted server-side.</p>
      <form onSubmit={handleSubmit}>
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
        {error && <p className="error">{error}</p>}
        {message && <p className="success">{message}</p>}
        <button disabled={busy}>{busy ? "Uploading..." : "Upload"}</button>
      </form>

      {resume && (
        <div className="preview">
          <h3>Current resume</h3>
          <p><strong>{resume.filename}</strong> — uploaded {new Date(resume.uploaded_at).toLocaleString()}</p>
          <details>
            <summary>Extracted text preview</summary>
            <pre className="scroll-box">{resume.extracted_text.slice(0, 2000)}</pre>
          </details>
          <button className="secondary" onClick={handleDelete}>Delete resume</button>
        </div>
      )}
    </section>
  );
}

export default ResumeUpload;
