"use client";

import { useState } from "react";
import { ActionItem } from "@/lib/api";
import { EvidenceViewer } from "@/components/EvidenceViewer";

interface Props {
  item: ActionItem;
  onApprove: () => void;
  onReject: () => void;
  onEdit: (field: string, value: string) => void;
}

const PRIORITY_COLORS = {
  critical: "bg-red-100 text-red-700 border-red-200",
  high:     "bg-orange-100 text-orange-700 border-orange-200",
  medium:   "bg-yellow-100 text-yellow-700 border-yellow-200",
  low:      "bg-green-100 text-green-700 border-green-200",
};

const CONFIDENCE_COLOR = (c: number) =>
  c >= 0.85 ? "text-green-600" : c >= 0.7 ? "text-yellow-600" : "text-red-600";

export function ActionItemCard({ item, onApprove, onReject, onEdit }: Props) {
  const [editing, setEditing] = useState(false);
  const [showEvidence, setShowEvidence] = useState(false);

  const borderClass =
    item.status === "approved" ? "border-green-400 bg-green-50" :
    item.status === "rejected" ? "border-red-300 bg-red-50 opacity-60" :
    "border-gray-200 bg-white";

  return (
    <div className={`border-2 rounded-xl p-5 transition-all ${borderClass}`}>
      <div className="flex items-start justify-between gap-4">
        {/* Left: content */}
        <div className="flex-1 min-w-0">
          {editing ? (
            <input
              className="text-base font-semibold text-gray-900 border-b border-blue-300 outline-none w-full bg-transparent"
              value={item.title}
              onChange={(e) => onEdit("title", e.target.value)}
              onBlur={() => setEditing(false)}
              autoFocus
            />
          ) : (
            <h3
              className="text-base font-semibold text-gray-900 cursor-pointer hover:text-blue-600"
              onClick={() => setEditing(true)}
            >
              {item.title}
            </h3>
          )}

          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2 text-sm text-gray-600">
            {/* Owner */}
            <span>
              👤{" "}
              <input
                className="border-b border-transparent hover:border-gray-300 outline-none bg-transparent"
                value={item.owner_resolved?.resolved_name || item.owner_raw}
                onChange={(e) => onEdit("owner_raw", e.target.value)}
              />
              {item.owner_confidence < 0.7 && (
                <span className="ml-1 text-amber-500 text-xs">⚠️ low confidence</span>
              )}
            </span>

            {/* Due date */}
            <span>
              📅{" "}
              <input
                type="date"
                className="border-b border-transparent hover:border-gray-300 outline-none bg-transparent text-sm"
                value={item.due_date_resolved || ""}
                onChange={(e) => onEdit("due_date_resolved", e.target.value)}
              />
              {!item.due_date_resolved && item.due_date_raw && (
                <span className="text-gray-400 text-xs ml-1">({item.due_date_raw})</span>
              )}
            </span>

            {/* Priority */}
            <select
              value={item.priority}
              onChange={(e) => onEdit("priority", e.target.value)}
              className={`text-xs px-2 py-0.5 rounded-full border font-medium ${PRIORITY_COLORS[item.priority]}`}
            >
              {["critical","high","medium","low"].map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>

            {/* Confidence */}
            <span className={`text-xs font-medium ${CONFIDENCE_COLOR(item.confidence)}`}>
              {(item.confidence * 100).toFixed(0)}% confidence
            </span>

            {/* Integration */}
            <span className="text-xs bg-gray-100 px-2 py-0.5 rounded-full text-gray-500">
              → {item.target_integration}
            </span>
          </div>

          {/* Evidence toggle */}
          {item.evidence_quote && (
            <button
              onClick={() => setShowEvidence(!showEvidence)}
              className="mt-2 text-xs text-blue-500 hover:text-blue-700"
            >
              {showEvidence ? "Hide" : "Show"} evidence [{item.evidence_timestamp}]
            </button>
          )}
          {showEvidence && (
            <EvidenceViewer quote={item.evidence_quote} timestamp={item.evidence_timestamp} />
          )}
        </div>

        {/* Right: action buttons */}
        <div className="flex flex-col gap-2 flex-shrink-0">
          {item.status !== "approved" && (
            <button onClick={onApprove}
              className="px-4 py-1.5 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 font-medium">
              ✓ Approve
            </button>
          )}
          {item.status !== "rejected" && (
            <button onClick={onReject}
              className="px-4 py-1.5 border border-red-300 text-red-600 text-sm rounded-lg hover:bg-red-50 font-medium">
              ✕ Reject
            </button>
          )}
          {item.status === "approved" && (
            <span className="text-xs text-center text-green-700 font-medium">✓ Approved</span>
          )}
        </div>
      </div>
    </div>
  );
}
