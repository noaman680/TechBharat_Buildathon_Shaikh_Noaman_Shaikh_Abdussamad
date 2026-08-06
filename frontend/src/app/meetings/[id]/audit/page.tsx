"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getAuditTrail, AuditEntry } from "@/lib/api";
import { AuditTimeline } from "@/components/AuditTimeline";

export default function AuditPage() {
  const { id } = useParams<{ id: string }>();
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAuditTrail(id).then(setEntries).finally(() => setLoading(false));
  }, [id]);

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">🔍 Audit Trail</h1>
      <p className="text-sm text-gray-500 mb-8">
        Every AI decision, tool call, and user action — fully transparent and explainable.
      </p>
      {loading ? (
        <p className="text-gray-500">Loading audit trail...</p>
      ) : (
        <AuditTimeline entries={entries} />
      )}
    </div>
  );
}
