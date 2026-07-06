import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

import { getSkillGap } from "../Services/RecommendationService";
import type { SkillGap as SkillGapType } from "../types/domain";

function SkillGap() {
  const { jobId } = useParams();
  const [gap, setGap] = useState<SkillGapType | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!jobId) return;
    getSkillGap(Number(jobId))
      .then(setGap)
      .catch(() => setError("Could not compute skill gap."));
  }, [jobId]);

  if (error) return <p className="error">{error}</p>;
  if (!gap) return <p>Analysing...</p>;

  return (
    <section className="card wide">
      <p className="eyebrow">SKILL GAP</p>
      <h1>Skill gap for job #{gap.job_id}</h1>
      <h3>Matching skills</h3>
      <p>{gap.matching_skills.join(", ") || "None yet"}</p>
      <h3>Missing skills</h3>
      <p>{gap.missing_skills.join(", ") || "None — you cover all listed skills"}</p>
      <h3>AI suggestions</h3>
      <p style={{ whiteSpace: "pre-wrap" }}>{gap.suggestions}</p>
    </section>
  );
}

export default SkillGap;
