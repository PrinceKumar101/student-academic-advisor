import type { MeResponse, TokenResponse } from "../api/auth";

export function studentMe(): MeResponse {
  return {
    id: 1,
    email: "rahul@demo.edu",
    role: "STUDENT",
    student_id: 12,
    teacher_id: null,
    full_name: "Rahul Venn",
  };
}

export function teacherMe(): MeResponse {
  return {
    id: 2,
    email: "teacher1@demo.edu",
    role: "TEACHER",
    student_id: null,
    teacher_id: 1,
    full_name: "Teacher One",
  };
}

export function tokenResponse(user: MeResponse): TokenResponse {
  return {
    access_token: "test-token",
    token_type: "bearer",
    expires_in: 3600,
    user: {
      id: user.id,
      role: user.role,
      student_id: user.student_id,
      teacher_id: user.teacher_id,
      full_name: user.full_name,
    },
  };
}

export function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}
