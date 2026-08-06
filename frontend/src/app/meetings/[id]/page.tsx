"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getMeetingStatus, getMeetingReport } from "@/lib/api";
import { subscribeToMeetingStream, getPhaseLabel, AgentPhase } from "@/lib/websocket";
import { ProcessingProgress } from "@/components/ProcessingProgress";
import Link from "next/link";

export default function MeetingDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [phase, setPhase] = useState<AgentPhase>("starting");
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState("Starting...");
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Poll status every 3s (fallback if SSE not available)
    const pollInterval = setInterval(async () => {
      try {
        const status = await getMeetingStatus(id);
        if (status.phase) {
          setPhase(status.phase);
          setMessage(getPhaseLabel(status.phase));
        }
        if (status.phase === "awaiting_approval") {
          clearInterval(pollInterval);
          router.push(`/approvals/${id}`);
        }
        if (status.phase === "complete") {
          setDone(true);
          clearInterval(pollInterval);
        }
        if (status.phase === "error") {
          setError(status.message || "Processing failed");
          clearInterval(pollInterval);
        }
      } catch {
        // API may not be ready yet
      }
    }, 3000);

    // SSE stream
    const unsubscribe = subscribeToMeetingStream(id, undefined, (event) => {
      setPhase(event.phase);
      setProgress(event.progress);
      setMessage(event.message);
      if (event.phase === "awaiting_approval") {
        clearInterval(pollInterval);
        router.push(`/approvals/${id}`);
      }
      if (event.phase === "complete") { setDone(true); clearInterval(pollInterval); }
      if (event.phase === "error") { setError(event.message); clearInterval(pollInterval); }
    });

    return () => { clearInterval(pollInterval); unsubscribe(); };
  }, [id, router]);

  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Processing Meeting</h1>
      <p className="text-sm text-gray-500 mb-8">ID: {id}</p>

      <ProcessingProgress phase={phase} progress={progress} message={message} />

      {error && (
        <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700">
          <strong>Error:</strong> {error}
        </div>
      )}

      {done && (
        <div className="mt-6 flex gap-3">
          <Link href={`/meetings/${id}/report`}
            className="flex-1 text-center bg-blue-600 text-white py-3 rounded-xl font-semibold hover:bg-blue-700">
            View Report
          </Link>
          <Link href={`/meetings/${id}/audit`}
            className="flex-1 text-center bg-gray-100 text-gray-700 py-3 rounded-xl font-semibold hover:bg-gray-200">
            Audit Trail
          </Link>
        </div>
      )}
    </div>
  );
}
