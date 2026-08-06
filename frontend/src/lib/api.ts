/**
 * MeetMind API client
 */
import axios from "axios";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

// ── Types ────────────────────────────────────────────────────────────────────

export interface ActionItem {
  id: string;
  title: string;
  description: string;
  owner_raw: string;
  owner_resolved?: {
    resolved_name?: string;
    email?: string;
    confidence: number;
  };
  owner_confidence: number;
  due_date_raw: string;
  due_date_resolved?: string;
  priority: "critical" | "high" | "medium" | "low";
  confidence: number;
  evidence_timestamp: string;
  evidence_quote: string;
  meeting_section: string;
  dependencies: string[];
  fingerprint: string;
  status: "pending" | "approved" | "rejected" | "executed";
  target_integration: string;
  external_ref?: Record<string, string>;
}

export interface Decision {
  id: string;
  description: string;
  made_by: string[];
  timestamp: string;
  confidence: number;
}

export interface Risk {
  id: string;
  description: string;
  severity: "critical" | "high" | "medium" | "low";
  owner?: string;
}

export interface MeetingReport {
  executive_summary: string;
  decisions: Decision[];
  open_questions: string[];
  risks: Risk[];
  dependencies: string[];
  discussion_topics: string[];
  key_insights: string[];
  follow_ups: string[];
}

export interface ApprovalSession {
  meeting_id: string;
  status: string;
  action_items: ActionItem[];
  structured_report: MeetingReport;
  warnings: string[];
  overdue_followups: Array<{ title: string; owner: string; meeting_date: string }>;
  related_meetings: string[];
}

export interface AuditEntry {
  timestamp: string;
  agent: string;
  action: string;
  output_summary: string;
  reasoning?: string;
  duration_ms: number;
}

// ── API Calls ────────────────────────────────────────────────────────────────

export async function uploadMeeting(formData: FormData): Promise<{
  meeting_id: string;
  status: string;
  message: string;
}> {
  const resp = await api.post("/api/meetings/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return resp.data;
}

export async function getMeetingStatus(meetingId: string) {
  const resp = await api.get(`/api/meetings/${meetingId}/status`);
  return resp.data;
}

export async function getMeetingReport(meetingId: string): Promise<MeetingReport> {
  const resp = await api.get(`/api/meetings/${meetingId}/report`);
  return resp.data.report;
}

export async function getApprovalSession(meetingId: string): Promise<ApprovalSession> {
  const resp = await api.get(`/api/approvals/${meetingId}`);
  return resp.data;
}

export async function submitApproval(
  meetingId: string,
  approved: ActionItem[],
  rejectedIds: string[],
  rejectionReasons: Record<string, string> = {}
) {
  const resp = await api.post(`/api/approvals/${meetingId}/submit`, {
    approved_items: approved.map((i) => ({ ...i, status: "approved" })),
    rejected_ids: rejectedIds,
    rejection_reasons: rejectionReasons,
  });
  return resp.data;
}

export async function getExecutionResults(meetingId: string) {
  const resp = await api.get(`/api/approvals/${meetingId}/results`);
  return resp.data;
}

export async function getAuditTrail(meetingId: string): Promise<AuditEntry[]> {
  const resp = await api.get(`/api/meetings/${meetingId}/audit`);
  return resp.data.audit_entries || [];
}

export async function listIntegrations(): Promise<string[]> {
  const resp = await api.get("/api/integrations/available");
  return resp.data.integrations || [];
}

export async function askAboutMeetings(orgId: string, question: string) {
  const resp = await api.post("/api/ask", { org_id: orgId, question });
  return resp.data;
}
