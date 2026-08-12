// Thin wrapper around fetch that talks to the FastAPI backend
// and attaches the current Firebase ID token as a Bearer token.
import { auth } from "../firebase/firebaseConfig";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function getAuthHeader() {
  const user = auth.currentUser;
  if (!user) return {};
  const token = await user.getIdToken();
  return { Authorization: `Bearer ${token}` };
}

async function request(path, options = {}) {
  const authHeader = await getAuthHeader();

  const response = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...authHeader,
      ...options.headers,
    },
  });

  if (!response.ok) {
    let detail = "Request failed";
    try {
      const data = await response.json();
      detail = data.detail || detail;
    } catch (_) {
      // response wasn't JSON
    }
    throw new Error(detail);
  }

  // /health-style endpoints may return no body
  const contentType = response.headers.get("content-type") || "";
  return contentType.includes("application/json") ? response.json() : null;
}

export const apiClient = {
  get: (path) => request(path, { method: "GET" }),
  post: (path, body) => request(path, { method: "POST", body: JSON.stringify(body) }),
};

// Matches GET /api/auth/me in your FastAPI backend
export function fetchCurrentUser() {
  return apiClient.get("/api/auth/me");
}