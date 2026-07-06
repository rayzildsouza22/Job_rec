import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";

import { getToken } from "../Services/AuthServices";

interface ProtectedRouteProps {
  children: ReactNode;
}

function ProtectedRoute({ children }: ProtectedRouteProps) {
  if (!getToken()) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

export default ProtectedRoute;

