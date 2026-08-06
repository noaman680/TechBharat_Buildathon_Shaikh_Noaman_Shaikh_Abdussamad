"use client";

import { AgentPhase, getPhaseLabel } from "@/lib/websocket";

const PHASES: AgentPhase[] = [
  "ingested","transcribing","diarizing","planning",
  "extracting","verifying","resolving_identity",
  "resolving_dates","memory_enriching","awaiting_approval",
];

interface Props { phase: AgentPhase; progress: number; message: string; }

export function ProcessingProgress({ phase, progress, message }: Props) {
  const currentIdx = PHASES.indexOf(phase);

  return (
    <div className="bg-white rounded-xl p-8 shadow-sm border">
      {/* Progress bar */}
      <div className="mb-6">
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>Processing</span><span>{progress}%</span>
        </div>
        <div className="w-full bg-gray-100 rounded-full h-2">
          <div
            className="bg-blue-500 h-2 rounded-full transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Current phase */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-2 bg-blue-50 px-4 py-2 rounded-full">
          <span className="h-2 w-2 bg-blue-500 rounded-full animate-pulse" />
          <span className="text-sm font-medium text-blue-700">{message}</span>
        </div>
      </div>

      {/* Phase checklist */}
      <div className="space-y-2">
        {PHASES.map((p, idx) => {
          const done = idx < currentIdx;
          const active = idx === currentIdx;
          return (
            <div key={p} className={`flex items-center gap-3 py-1.5 px-3 rounded-lg text-sm
              ${active ? "bg-blue-50" : ""}`}>
              <span className={`w-5 h-5 rounded-full flex items-center justify-center text-xs flex-shrink-0
                ${done ? "bg-green-500 text-white" : active ? "bg-blue-500 text-white" : "bg-gray-100 text-gray-400"}`}>
                {done ? "✓" : idx + 1}
              </span>
              <span className={done ? "text-green-700" : active ? "text-blue-700 font-medium" : "text-gray-400"}>
                {getPhaseLabel(p)}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
