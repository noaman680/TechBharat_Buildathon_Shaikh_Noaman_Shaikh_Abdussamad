// Thin fetch wrapper around the MeetMind FastAPI backend.
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${await res.text()}`);
  }
  return res.json();
}

export const api = {
  uploadMeeting: (formData: FormData) =>
    fetch(`${API_URL}/api/meetings/upload`, { method: "POST", body: formData }),
  getMeeting: (id: string) => request(`/api/meetings/${id}`),
  getReport: (id: string) => request(`/api/meetings/${id}/report`),
  getActionItems: (id: string) => request(`/api/meetings/${id}/items`),
  getApproval: (id: string) => request(`/api/approvals/${id}`),
  executeApproval: (id: string) =>
    request(`/api/approvals/${id}/execute`, { method: "POST" }),
  ask: (q: string, orgId: string) =>
    request(`/api/ask?q=${encodeURIComponent(q)}&org_id=${orgId}`),
};
