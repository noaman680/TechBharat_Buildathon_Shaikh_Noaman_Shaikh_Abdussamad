"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

interface OrgSummary {
  total_meetings: number;
  total_action_items: number;
  completion_rate: number;
  avg_items_per_meeting: number;
  overdue_count: number;
  top_owners: Array<{ name: string; count: number; completion_rate: number }>;
}

const StatCard = ({ label, value, sublabel }: { label: string; value: string | number; sublabel?: string }) => (
  <div className="bg-white rounded-xl p-6 shadow-sm border">
    <p className="text-sm text-gray-500">{label}</p>
    <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
    {sublabel && <p className="text-xs text-gray-400 mt-1">{sublabel}</p>}
  </div>
);

export default function AnalyticsPage() {
  const [summary, setSummary] = useState<OrgSummary | null>(null);

  useEffect(() => {
    api.get("/api/analytics/org/demo-org/summary").then((r) => setSummary(r.data)).catch(() => {});
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">📊 Meeting Analytics</h1>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard label="Total Meetings" value={summary?.total_meetings ?? 0} />
        <StatCard label="Action Items" value={summary?.total_action_items ?? 0} />
        <StatCard label="Completion Rate"
          value={`${((summary?.completion_rate ?? 0) * 100).toFixed(0)}%`}
          sublabel="of committed tasks done" />
        <StatCard label="Overdue Tasks" value={summary?.overdue_count ?? 0}
          sublabel="need attention" />
      </div>
      <div className="bg-white rounded-xl p-6 shadow-sm border">
        <h2 className="font-semibold text-gray-800 mb-4">Top Committers</h2>
        {summary?.top_owners?.length ? (
          <div className="space-y-3">
            {summary.top_owners.map((o) => (
              <div key={o.name} className="flex items-center gap-3">
                <span className="text-sm font-medium text-gray-700 w-32">{o.name}</span>
                <div className="flex-1 bg-gray-100 rounded-full h-2">
                  <div className="bg-blue-500 h-2 rounded-full"
                    style={{ width: `${o.completion_rate * 100}%` }} />
                </div>
                <span className="text-xs text-gray-500">{o.count} tasks</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-500">No meeting data yet. Upload your first meeting!</p>
        )}
      </div>
    </div>
  );
}
