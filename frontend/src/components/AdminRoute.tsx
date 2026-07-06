import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

import { getCurrentUser, getToken } from "../Services/AuthServices";

type Status = "loading" | "allowed" | "denied";

function AdminRoute({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<Status>("loading");

  useEffect(() => {
    if (!getToken()) {
      setStatus("denied");
      return;
    }
    getCurrentUser()
      .then((user) => setStatus(user.is_admin ? "allowed" : "denied"))
      .catch(() => setStatus("denied"));
  }, []);

  if (status === "loading") return <p className="page">Checking access...</p>;
  if (status === "denied") return <Navigate to="/dashboard" replace />;
  return children;
}

export default AdminRoute;
