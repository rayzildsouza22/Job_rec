import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { getCurrentUser, logoutUser } from "../Services/AuthServices";
import type { User } from "../types/auth";

function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getCurrentUser()
      .then(setUser)
      .catch(() => {
        logoutUser();
        setError("Your session is invalid or expired.");
      });
  }, []);

  if (error) {
    return (
      <section className="card">
        <p className="error">{error}</p>
        <button onClick={() => navigate("/login")}>Return to login</button>
      </section>
    );
  }

  return (
    <section className="hero">
      <p className="eyebrow">DASHBOARD</p>
      <h1>{user ? `Hello, ${user.name}` : "Loading..."}</h1>
      <p>Complete the four steps below to get semantic job recommendations.</p>
      <div className="tile-grid">
        <Link className="tile" to="/profile">
          <h3>1. Profile</h3>
          <p>Add skills, education, preferred role.</p>
        </Link>
        <Link className="tile" to="/resume">
          <h3>2. Resume</h3>
          <p>Upload your PDF resume. Text is extracted automatically.</p>
        </Link>
        <Link className="tile" to="/jobs">
          <h3>3. Browse jobs</h3>
          <p>Search and filter jobs in the catalogue.</p>
        </Link>
        <Link className="tile" to="/recommendations">
          <h3>4. Recommendations</h3>
          <p>Ask the AI for personalised matches with explanations.</p>
        </Link>
      </div>
      {user && (
        <div className="user-detail">
          <span>Signed in as</span>
          <strong>{user.email}</strong>
          {user.is_admin && <em className="badge">admin</em>}
        </div>
      )}
    </section>
  );
}

export default Dashboard;
