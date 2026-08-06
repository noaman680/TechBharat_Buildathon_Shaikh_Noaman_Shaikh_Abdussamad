"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getApprovalSession, submitApproval, ActionItem, ApprovalSession } from "@/lib/api";
import { ApprovalDashboard } from "@/components/ApprovalDashboard";
import { toast } from "sonner";

export default function ApprovalPage() {
  const { id } = useParams<{ id: string }>();
  const [session, setSession] = useState<ApprovalSession | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    getApprovalSession(id)
      .then(setSession)
      .catch(() => toast.error("Failed to load approval session"))
      .finally(() => setLoading(false));
  }, [id]);

  const handleSubmit = async (approved: ActionItem[], rejectedIds: string[]) => {
    setSubmitting(true);
    try {
      await submitApproval(id, approved, rejectedIds);
      toast.success(`Executing ${approved.length} action items...`);
      setSubmitted(true);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Submission failed");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return (
    <div className="flex items-center justify-center min-h-screen">
      <p className="text-gray-500">Loading approval session...</p>
    </div>
  );

  if (submitted) return (
    <div className="max-w-2xl mx-auto px-4 py-12 text-center">
      <p className="text-5xl mb-4">🚀</p>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Actions Executing</h1>
      <p className="text-gray-600">Creating tasks in your connected tools. Check your Jira/Slack for updates.</p>
    </div>
  );

  if (!session) return (
    <div className="max-w-2xl mx-auto px-4 py-12 text-center">
      <p className="text-gray-500">No approval session found for meeting {id}</p>
    </div>
  );

  return (
    <ApprovalDashboard
      session={session}
      onSubmit={handleSubmit}
      submitting={submitting}
    />
  );
}
