/**
 * WebSocket / SSE client for real-time agent progress streaming
 */

export type AgentPhase =
  | "starting" | "ingested" | "transcribing" | "diarizing"
  | "planning" | "extracting" | "verifying"
  | "resolving_identity" | "resolving_dates"
  | "memory_enriching" | "awaiting_approval"
  | "executing" | "complete" | "error";

export interface AgentProgressEvent {
  meeting_id: string;
  phase: AgentPhase;
  message: string;
  progress: number;       // 0–100
  details?: Record<string, unknown>;
}

const PHASE_LABELS: Record<AgentPhase, string> = {
  starting:          "Initialising...",
  ingested:          "File validated",
  transcribing:      "Transcribing audio with Whisper...",
  diarizing:         "Identifying speakers...",
  planning:          "Planning extraction strategy...",
  extracting:        "Extracting action items with GPT-4o...",
  verifying:         "Verifying extracted items...",
  resolving_identity:"Resolving owner identities...",
  resolving_dates:   "Resolving dates to calendar...",
  memory_enriching:  "Loading cross-meeting context...",
  awaiting_approval: "Ready for your review ✅",
  executing:         "Creating tasks in external systems...",
  complete:          "Done!",
  error:             "Processing failed",
};

export function getPhaseLabel(phase: AgentPhase): string {
  return PHASE_LABELS[phase] || phase;
}

export function getPhaseProgress(phase: AgentPhase): number {
  const order: AgentPhase[] = [
    "starting", "ingested", "transcribing", "diarizing",
    "planning", "extracting", "verifying",
    "resolving_identity", "resolving_dates",
    "memory_enriching", "awaiting_approval",
    "executing", "complete",
  ];
  const idx = order.indexOf(phase);
  return idx === -1 ? 0 : Math.round((idx / (order.length - 1)) * 100);
}

export function subscribeToMeetingStream(
  meetingId: string,
  baseUrl: string = "http://localhost:8000",
  onEvent: (event: AgentProgressEvent) => void,
  onError?: (error: Event) => void,
): () => void {
  const url = `${baseUrl}/api/meetings/${meetingId}/status`;
  const source = new EventSource(url);

  source.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data) as AgentProgressEvent;
      data.progress = getPhaseProgress(data.phase);
      onEvent(data);
    } catch {
      // ignore parse errors
    }
  };

  if (onError) source.onerror = onError;

  return () => source.close();
}
