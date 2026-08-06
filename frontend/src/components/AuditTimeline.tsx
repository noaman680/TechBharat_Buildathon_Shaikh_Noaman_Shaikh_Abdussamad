import { AuditEntry } from "@/lib/api";

interface Props { entries: AuditEntry[]; }

const AGENT_COLORS: Record<string, string> = {
  IngestionAgent:          "bg-gray-100 text-gray-700",
  TranscriptionAgent:      "bg-purple-100 text-purple-700",
  DiarizationAgent:        "bg-indigo-100 text-indigo-700",
  PlanningAgent:           "bg-blue-100 text-blue-700",
  ExtractionAgent:         "bg-cyan-100 text-cyan-700",
  VerificationAgent:       "bg-teal-100 text-teal-700",
  IdentityResolutionAgent: "bg-green-100 text-green-700",
  CalendarResolutionAgent: "bg-lime-100 text-lime-700",
  MemoryAgent:             "bg-yellow-100 text-yellow-700",
  ApprovalAgent:           "bg-orange-100 text-orange-700",
  IntegrationAgent:        "bg-red-100 text-red-700",
  AuditAgent:              "bg-pink-100 text-pink-700",
};

export function AuditTimeline({ entries }: Props) {
  if (entries.length === 0) {
    return <p className="text-gray-500 text-sm">No audit entries found.</p>;
  }

  return (
    <div className="space-y-4">
      {entries.map((entry, i) => (
        <div key={i} className="flex gap-4">
          <div className="flex flex-col items-center">
            <div className="w-3 h-3 rounded-full bg-blue-500 flex-shrink-0 mt-1" />
            {i < entries.length - 1 && <div className="w-0.5 flex-1 bg-gray-200 mt-1" />}
          </div>
          <div className="pb-4 flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${AGENT_COLORS[entry.agent] || "bg-gray-100 text-gray-700"}`}>
                {entry.agent}
              </span>
              <span className="text-xs text-gray-400">
                {new Date(entry.timestamp).toLocaleTimeString()} — {entry.duration_ms}ms
              </span>
            </div>
            <p className="text-sm font-medium text-gray-800">{entry.action}</p>
            <p className="text-xs text-gray-500 mt-0.5">{entry.output_summary}</p>
            {entry.reasoning && (
              <p className="text-xs text-gray-400 mt-1 italic">&ldquo;{entry.reasoning}&rdquo;</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
