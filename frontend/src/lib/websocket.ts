// Real-time processing progress via WebSocket.
// WS /ws/meetings/{id}/progress — see docs/BLUEPRINT.md §15 for the message schema.
export function subscribeToProgress(
  meetingId: string,
  onEvent: (event: { event: string; progress: number; [key: string]: unknown }) => void
) {
  const wsUrl = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(
    /^http/,
    "ws"
  );
  const socket = new WebSocket(`${wsUrl}/ws/meetings/${meetingId}/progress`);
  socket.onmessage = (msg) => onEvent(JSON.parse(msg.data));
  return () => socket.close();
}
