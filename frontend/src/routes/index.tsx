import { Navigate, Route, Routes } from "react-router-dom";

import { ProtectedRoute } from "../auth/ProtectedRoute";
import { HomeRedirect, RoleRoute } from "../auth/RoleRoute";
import { Layout } from "../components/Layout";
import { ForbiddenPage } from "../pages/ForbiddenPage";
import { LoginPage } from "../pages/LoginPage";
import { RegisterPage } from "../pages/RegisterPage";
import { AdvisorPage } from "../pages/student/AdvisorPage";
import { InterventionsPage } from "../pages/student/InterventionsPage";
import { PerformancePage } from "../pages/student/PerformancePage";
import { PlannerPage } from "../pages/student/PlannerPage";
import { ProfilePage } from "../pages/student/ProfilePage";
import { RiskPage } from "../pages/student/RiskPage";
import { StudentHomePage } from "../pages/student/StudentHomePage";
import { SubjectsPage } from "../pages/student/SubjectsPage";
import { WhatIfPage } from "../pages/student/WhatIfPage";
import { TeacherHomePage } from "../pages/teacher/TeacherHomePage";
import { TeacherInterventionsPage } from "../pages/teacher/TeacherInterventionsPage";
import { TeacherStudentDetailPage } from "../pages/teacher/TeacherStudentDetailPage";
import { TeacherStudentsPage } from "../pages/teacher/TeacherStudentsPage";
import { TeacherSubjectsPage } from "../pages/teacher/TeacherSubjectsPage";

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forbidden" element={<ForbiddenPage />} />
      <Route path="/" element={<HomeRedirect />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route element={<RoleRoute role="STUDENT" />}>
            <Route path="/student" element={<StudentHomePage />} />
            <Route path="/student/risk" element={<RiskPage />} />
            <Route path="/student/performance" element={<PerformancePage />} />
            <Route path="/student/subjects" element={<SubjectsPage />} />
            <Route path="/student/what-if" element={<WhatIfPage />} />
            <Route path="/student/advisor" element={<AdvisorPage />} />
            <Route path="/student/planner" element={<PlannerPage />} />
            <Route path="/student/interventions" element={<InterventionsPage />} />
            <Route path="/student/profile" element={<ProfilePage />} />
          </Route>
          <Route element={<RoleRoute role="TEACHER" />}>
            <Route path="/teacher" element={<TeacherHomePage />} />
            <Route path="/teacher/students" element={<TeacherStudentsPage />} />
            <Route path="/teacher/students/:studentId" element={<TeacherStudentDetailPage />} />
            <Route path="/teacher/interventions" element={<TeacherInterventionsPage />} />
            <Route path="/teacher/subjects" element={<TeacherSubjectsPage />} />
            <Route path="/teacher/subjects/:subjectId" element={<TeacherSubjectsPage />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
