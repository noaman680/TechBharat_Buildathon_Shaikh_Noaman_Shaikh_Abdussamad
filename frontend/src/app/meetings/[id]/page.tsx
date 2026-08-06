// Meeting detail page — transcript, live processing progress, report summary.
// TODO: fetch via api.getMeeting(params.id), subscribe to progress via
// subscribeToProgress() while status !== "complete".
export default function MeetingDetailPage({ params }: { params: { id: string } }) {
  return <div className="p-8">TODO: meeting detail view for {params.id}</div>;
}
