const localApiHost = window.location.hostname === "localhost" ? "localhost" : "127.0.0.1";
const API_URL = (import.meta.env.VITE_API_URL || `http://${localApiHost}:8000`).replace(/\/$/, "");

async function responseError(response) {
  let message = `Request failed (${response.status}).`;
  try {
    const body = await response.json();
    if (typeof body.detail === "string") message = body.detail;
    else if (body && typeof body === "object") {
      const messages = Object.values(body).flatMap((value) =>
        Array.isArray(value) ? value : [value]
      );
      if (messages.length) message = messages.join(" ");
    }
  } catch {
    if (response.status === 0) message = "Could not reach the Studyverse server.";
  }
  const error = new Error(message);
  error.status = response.status;
  return error;
}

async function request(path, options = {}) {
  const method = options.method || "GET";
  const headers = { ...(options.headers || {}) };
  if (options.body !== undefined) headers["Content-Type"] = "application/json";

  if (method !== "GET" && method !== "HEAD") {
    const csrfResponse = await fetch(`${API_URL}/api/accounts/csrf/`, {
      credentials: "include",
    });
    if (!csrfResponse.ok) throw await responseError(csrfResponse);
    const { csrfToken } = await csrfResponse.json();
    headers["X-CSRFToken"] = csrfToken;
  }

  let response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      ...options,
      method,
      headers,
      credentials: "include",
    });
  } catch {
    throw new Error("Could not connect to Studyverse. Check that Django is running.");
  }

  if (!response.ok) throw await responseError(response);
  if (response.status === 204) return null;
  return response.json();
}

function get(path) {
  return request(path);
}

function post(path, data) {
  return request(path, { method: "POST", body: JSON.stringify(data) });
}

export function getSession() {
  return get("/api/accounts/session/");
}

export function login(data) {
  return post("/api/accounts/login/", data);
}

export function register(data) {
  return post("/api/accounts/register/", data);
}

export function logout() {
  return post("/api/accounts/logout/", {});
}

export function getSemesters() {
  return get("/api/academics/semesters/");
}

export function getSubjects() {
  return get("/api/academics/subjects/");
}

export function getSemester3() {
  return get("/api/academics/semesters/current/");
}

export function getStudyPlan({ minutes = 180, days = 5, ai = true } = {}) {
  return get(`/api/ai/study-plan/?minutes=${minutes}&days=${days}&ai=${ai ? 1 : 0}`);
}

export function getSubjectDetail(subjectId) {
  return get(`/api/academics/subjects/${subjectId}/syllabus/`);
}

export function getModules() {
  return get("/api/academics/modules/");
}

export function getTopics() {
  return get("/api/academics/topics/");
}

export function completeTopic(topicId, completed) {
  return post(`/api/academics/topics/${topicId}/complete/`, { completed });
}

export function getStudySessions() {
  return get("/api/study/sessions/");
}

export function createStudySession(data) {
  return post("/api/study/sessions/", data);
}

export function getAssessments() {
  return get("/api/assessments/assessments/");
}

export function getMarks() {
  return get("/api/assessments/marks/");
}

export function getAnalytics() {
  return get("/api/analytics/overview/");
}

export function createMark(data) {
  return post("/api/assessments/marks/", data);
}

export function getAIOverview() {
  return get("/api/ai/overview/");
}

export function getAIMastery() {
  return get("/api/ai/mastery/");
}

export function getAIRisk() {
  return get("/api/ai/risk/");
}

export function getAIStudyPlan() {
  return get("/api/ai/study-plan/");
}

export function askAI(message, history = []) {
  return post("/api/ai/chat/", { message, history });
}

export function classifyQuestion(data) {
  return post("/api/ai/classify-question/", data);
}