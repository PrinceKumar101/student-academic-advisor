import { Navigate, Outlet } from "react-router-dom";

import { Loading } from "../components/Loading";
import { useAuth } from "./AuthContext";

type RoleRouteProps = {
  role: "STUDENT" | "TEACHER";
};

export function RoleRoute({ role }: RoleRouteProps) {
  const { user, ready } = useAuth();

  if (!ready) {
    return <Loading />;
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if (user.role !== role) {
    return <Navigate to="/forbidden" replace />;
  }
  return <Outlet />;
}

export function HomeRedirect() {
  const { user, ready, token } = useAuth();

  if (!ready) {
    return <Loading />;
  }
  if (!token || !user) {
    return <Navigate to="/login" replace />;
  }
  return <Navigate to={user.role === "TEACHER" ? "/teacher" : "/student"} replace />;
}
