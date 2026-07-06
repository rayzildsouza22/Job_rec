import { NavLink, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";

import { getCurrentUser, getToken, logoutUser } from "../Services/AuthServices";
import type { User } from "../types/auth";

function NavBar() {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    if (!getToken()) return;
    getCurrentUser().then(setUser).catch(() => setUser(null));
  }, []);

  function handleLogout() {
    logoutUser();
    navigate("/login");
  }

  return (
    <header className="navbar">
      <strong className="brand">AI Job Assistant</strong>
      <nav className="nav-links">
        <NavLink to="/dashboard">Dashboard</NavLink>
        <NavLink to="/profile">Profile</NavLink>
        <NavLink to="/resume">Resume</NavLink>
        <NavLink to="/jobs">Jobs</NavLink>
        <NavLink to="/recommendations">Recommend</NavLink>
        <NavLink to="/saved">Saved</NavLink>
        <NavLink to="/history">History</NavLink>
        {user?.is_admin && <NavLink to="/admin">Admin</NavLink>}
      </nav>
      <div className="nav-right">
        {user && <span className="who">{user.name}</span>}
        <button className="secondary" onClick={handleLogout}>Log out</button>
      </div>
    </header>
  );
}

export default NavBar;
