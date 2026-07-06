import { FormEvent, useEffect, useState } from "react";

import { getMyProfile, updateMyProfile } from "../Services/ProfileService";
import type { Profile as ProfileType } from "../types/domain";

function Profile() {
  const [profile, setProfile] = useState<ProfileType | null>(null);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    getMyProfile()
      .then(setProfile)
      .catch(() => setError("Could not load your profile."));
  }, []);

  function update<K extends keyof ProfileType>(key: K, value: string) {
    if (!profile) return;
    setProfile({ ...profile, [key]: value } as ProfileType);
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!profile) return;
    setSaving(true);
    setMessage("");
    setError("");
    try {
      const updated = await updateMyProfile({
        full_name: profile.full_name,
        education: profile.education,
        skills: profile.skills,
        experience_level: profile.experience_level,
        preferred_role: profile.preferred_role,
        preferred_location: profile.preferred_location,
      });
      setProfile(updated);
      setMessage("Profile saved.");
    } catch {
      setError("Save failed.");
    } finally {
      setSaving(false);
    }
  }

  if (!profile) return <p>Loading...</p>;

  return (
    <section className="card wide">
      <p className="eyebrow">PROFILE</p>
      <h1>Your profile</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Full name
          <input
            value={profile.full_name ?? ""}
            onChange={(e) => update("full_name", e.target.value)}
          />
        </label>
        <label>
          Education
          <input
            value={profile.education ?? ""}
            onChange={(e) => update("education", e.target.value)}
            placeholder="e.g. B.Tech Computer Science"
          />
        </label>
        <label>
          Skills (comma-separated)
          <textarea
            rows={3}
            value={profile.skills ?? ""}
            onChange={(e) => update("skills", e.target.value)}
            placeholder="Python, React, SQL, ..."
          />
        </label>
        <label>
          Experience level
          <input
            value={profile.experience_level ?? ""}
            onChange={(e) => update("experience_level", e.target.value)}
            placeholder="Fresher / 1-2 years / Senior"
          />
        </label>
        <label>
          Preferred role
          <input
            value={profile.preferred_role ?? ""}
            onChange={(e) => update("preferred_role", e.target.value)}
            placeholder="Backend Engineer"
          />
        </label>
        <label>
          Preferred location
          <input
            value={profile.preferred_location ?? ""}
            onChange={(e) => update("preferred_location", e.target.value)}
            placeholder="Bengaluru / Remote"
          />
        </label>
        {message && <p className="success">{message}</p>}
        {error && <p className="error">{error}</p>}
        <button disabled={saving}>{saving ? "Saving..." : "Save profile"}</button>
      </form>
    </section>
  );
}

export default Profile;
