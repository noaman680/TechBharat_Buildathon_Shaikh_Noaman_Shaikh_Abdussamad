"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getMeetingReport, MeetingReport } from "@/lib/api";

const Section = ({ title, items, icon }: { title: string; items: string[]; icon: string }) =>
  items.length === 0 ? null : (
    <div className="bg-white rounded-xl p-6 shadow-sm border">
      <h3 className="font-semibold text-gray-800 mb-3">{icon} {title}</h3>
      <ul className="space-y-1">
        {items.map((item, i) => (
          <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
            <span className="text-gray-400 mt-0.5">•</span>{item}
          </li>
        ))}
      </ul>
    </div>
  );

export default function ReportPage() {
  const { id } = useParams<{ id: string }>();
  const [report, setReport] = useState<MeetingReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMeetingReport(id).then(setReport).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="p-12 text-center text-gray-500">Loading report...</div>;
  if (!report) return <div className="p-12 text-center text-gray-500">Report not found</div>;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">📋 Meeting Intelligence Report</h1>
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-6">
        <h2 className="font-semibold text-blue-800 mb-2">Executive Summary</h2>
        <p className="text-blue-900 text-sm leading-relaxed">{report.executive_summary}</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Section title="Decisions Made" icon="✅"
          items={report.decisions.map((d) => d.description)} />
        <Section title="Open Questions" icon="❓" items={report.open_questions} />
        <Section title="Risks Identified" icon="⚠️"
          items={report.risks.map((r) => `[${r.severity.toUpperCase()}] ${r.description}`)} />
        <Section title="Key Insights" icon="💡" items={report.key_insights} />
        <Section title="Follow-ups" icon="📅" items={report.follow_ups} />
        <Section title="Discussion Topics" icon="💬" items={report.discussion_topics} />
      </div>
    </div>
  );
}
