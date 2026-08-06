"use client";

import { useState } from "react";
import { ActionItem, ApprovalSession } from "@/lib/api";
import { ActionItemCard } from "@/components/ActionItemCard";
import { PayloadPreview } from "@/components/PayloadPreview";

interface Props {
  session: ApprovalSession;
  onSubmit: (approved: ActionItem[], rejectedIds: string[]) => Promise<void>;
  submitting: boolean;
}

export function ApprovalDashboard({ session, onSubmit, submitting }: Props) {
  const [items, setItems] = useState<ActionItem[]>(
    session.action_items.map((i) => ({ ...i, status: "pending" as const }))
  );
  const [showPayload, setShowPayload] = useState(false);

  const approved = items.filter((i) => i.status === "approved");
  const rejected = items.filter((i) => i.status === "rejected");
  const pending = items.filter((i) => i.status === "pending");

  const setItemStatus = (id: string, status: "approved" | "rejected") =>
    setItems((prev) => prev.map((i) => (i.id === id ? { ...i, status } : i)));

  const editItem = (id: string, field: keyof ActionItem, value: string) =>
    setItems((prev) => prev.map((i) => (i.id === id ? { ...i, [field]: value } : i)));

  const approveAll = () => setItems((prev) => prev.map((i) => ({ ...i, status: "approved" })));

  const handleSubmit = async () => {
    await onSubmit(approved, rejected.map((i) => i.id));
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">✅ Review & Approve</h1>
          <p className="text-sm text-gray-500 mt-1">
            {items.length} action items extracted — nothing executes without your approval
          </p>
        </div>
        <div className="flex gap-2">
          <span className="px-3 py-1 bg-green-100 text-green-700 text-sm rounded-full font-medium">
            {approved.length} approved
          </span>
          <span className="px-3 py-1 bg-red-100 text-red-700 text-sm rounded-full font-medium">
            {rejected.length} rejected
          </span>
          <span className="px-3 py-1 bg-gray-100 text-gray-600 text-sm rounded-full font-medium">
            {pending.length} pending
          </span>
        </div>
      </div>

      {/* Warnings */}
      {session.warnings.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-4">
          <p className="text-sm font-medium text-amber-800 mb-1">⚠️ Warnings</p>
          {session.warnings.map((w, i) => (
            <p key={i} className="text-xs text-amber-700">{w}</p>
          ))}
        </div>
      )}

      {/* Overdue from past meetings */}
      {session.overdue_followups.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-4">
          <p className="text-sm font-medium text-red-800 mb-1">🔴 Overdue from Past Meetings</p>
          {session.overdue_followups.slice(0, 3).map((t, i) => (
            <p key={i} className="text-xs text-red-700">
              {t.meeting_date}: &quot;{t.title}&quot; — {t.owner}
            </p>
          ))}
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-3 mb-6">
        <button onClick={approveAll}
          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm hover:bg-gray-50">
          Approve All
        </button>
        <button onClick={() => setShowPayload(!showPayload)}
          className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm hover:bg-gray-50">
          {showPayload ? "Hide" : "Preview"} API Payloads
        </button>
      </div>

      {showPayload && <PayloadPreview items={approved} />}

      {/* Action Item Cards */}
      <div className="space-y-4">
        {items.map((item) => (
          <ActionItemCard
            key={item.id}
            item={item}
            onApprove={() => setItemStatus(item.id, "approved")}
            onReject={() => setItemStatus(item.id, "rejected")}
            onEdit={(field, value) => editItem(item.id, field as keyof ActionItem, value)}
          />
        ))}
      </div>

      {/* Submit */}
      <div className="mt-8 flex justify-end">
        <button onClick={handleSubmit} disabled={approved.length === 0 || submitting}
          className="px-8 py-3 bg-blue-600 text-white rounded-xl font-semibold
            hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
          {submitting ? "Executing..." : `Execute ${approved.length} Approved Actions →`}
        </button>
      </div>
    </div>
  );
}
