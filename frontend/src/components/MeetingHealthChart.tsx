"use client";

import { RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip } from "recharts";

const DEFAULT_DATA = [
  { metric: "Participation", value: 80 },
  { metric: "Decision Rate", value: 65 },
  { metric: "Commitment Rate", value: 90 },
  { metric: "Follow-through", value: 70 },
  { metric: "Agenda Adherence", value: 75 },
  { metric: "Time Efficiency", value: 60 },
];

interface Props { data?: typeof DEFAULT_DATA; }

export function MeetingHealthChart({ data = DEFAULT_DATA }: Props) {
  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border">
      <h3 className="font-semibold text-gray-800 mb-4">🏥 Meeting Health Score</h3>
      <ResponsiveContainer width="100%" height={250}>
        <RadarChart data={data}>
          <PolarGrid />
          <PolarAngleAxis dataKey="metric" tick={{ fontSize: 11 }} />
          <Radar name="Score" dataKey="value" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.25} />
          <Tooltip />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
