// Full audit trail for a meeting — every agent decision, reasoning, tool call.
// TODO: fetch via GET /api/meetings/{id}/audit, render with AuditTimeline.
export default function MeetingAuditPage({ params }: { params: { id: string } }) {
  return <div className="p-8">TODO: audit timeline for {params.id}</div>;
}
