// Landing / upload page.
// TODO: wire MeetingUpload component to api.uploadMeeting() and route to
// /meetings/[id] once processing starts (see ProcessingProgress component).
import MeetingUpload from "@/components/MeetingUpload";

export default function HomePage() {
  return (
    <main className="max-w-2xl mx-auto py-16 px-4">
      <h1 className="text-3xl font-semibold mb-2">MeetMind</h1>
      <p className="text-gray-600 mb-8">
        Upload a meeting recording or transcript to extract decisions, risks,
        and action items — with evidence, confidence scores, and human
        approval before anything executes.
      </p>
      <MeetingUpload />
    </main>
  );
}
