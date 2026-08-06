"use client";

import { ActionItem } from "@/lib/api";

interface Props { items: ActionItem[]; }

function buildJiraPayload(item: ActionItem) {
  return {
    fields: {
      project: { key: "MEET" },
      summary: item.title,
      description: item.description,
      issuetype: { name: "Task" },
      priority: { name: item.priority === "critical" ? "Highest" : item.priority.charAt(0).toUpperCase() + item.priority.slice(1) },
      duedate: item.due_date_resolved || null,
      assignee: item.owner_resolved?.email ? { email: item.owner_resolved.email } : null,
      labels: ["meetmind", `meetmind-${item.fingerprint}`],
    },
  };
}

export function PayloadPreview({ items }: Props) {
  if (items.length === 0) {
    return <div className="bg-gray-50 rounded-xl p-4 mb-4 text-sm text-gray-500">No approved items to preview.</div>;
  }

  return (
    <div className="bg-gray-900 rounded-xl p-4 mb-4 overflow-auto max-h-64">
      <p className="text-xs text-gray-400 mb-2">API Payload Preview — exactly what will be sent:</p>
      {items.slice(0, 3).map((item) => (
        <div key={item.id} className="mb-3">
          <p className="text-xs text-blue-400 mb-1">POST /rest/api/3/issue  ({item.title})</p>
          <pre className="text-xs text-green-300 overflow-x-auto">
            {JSON.stringify(buildJiraPayload(item), null, 2)}
          </pre>
        </div>
      ))}
      {items.length > 3 && (
        <p className="text-xs text-gray-500">... and {items.length - 3} more</p>
      )}
    </div>
  );
}
