import { useAuth } from "../../auth/AuthContext";

/**
 * Landing call-to-action state. Reads the existing auth context only: the
 * landing page adds no authentication logic and issues no request of its own.
 */
export function useLandingCta(): { signedIn: boolean; dashboardPath: string } {
  const { user, ready } = useAuth();

  return {
    signedIn: ready && user !== null,
    dashboardPath: user?.role === "TEACHER" ? "/teacher" : "/student",
  };
}
