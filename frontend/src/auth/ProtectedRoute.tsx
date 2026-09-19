import { Navigate, Outlet, useLocation } from "react-router-dom";

import { Loading } from "../components/Loading";
import { useAuth } from "./AuthContext";

export function ProtectedRoute() {
  const { user, token, ready } = useAuth();
  const location = useLocation();

  if (!ready) {
    return <Loading />;
  }
  if (!token || !user) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }
  return <Outlet />;
}
