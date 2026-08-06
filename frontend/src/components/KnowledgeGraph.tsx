"use client";

import { useEffect, useRef } from "react";

interface Node { id: string; label: string; type: "meeting" | "person" | "task" | "decision"; }
interface Edge { source: string; target: string; label: string; }
interface Props { nodes: Node[]; edges: Edge[]; }

export function KnowledgeGraph({ nodes, edges }: Props) {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || nodes.length === 0) return;
    // In production: use d3-force or vis.js for graph layout
    // For demo: simple static SVG placeholder
  }, [nodes, edges]);

  const TYPE_COLORS = { meeting: "#3b82f6", person: "#10b981", task: "#f59e0b", decision: "#8b5cf6" };

  return (
    <div className="bg-white rounded-xl p-6 shadow-sm border">
      <h3 className="font-semibold text-gray-800 mb-4">🕸️ Knowledge Graph</h3>
      {nodes.length === 0 ? (
        <p className="text-sm text-gray-500">Knowledge graph builds as you process more meetings.</p>
      ) : (
        <div className="flex flex-wrap gap-3">
          {nodes.map((node) => (
            <span key={node.id}
              className="px-3 py-1.5 rounded-full text-sm text-white font-medium"
              style={{ backgroundColor: TYPE_COLORS[node.type] }}>
              {node.label}
            </span>
          ))}
        </div>
      )}
      <div className="flex gap-4 mt-4">
        {Object.entries(TYPE_COLORS).map(([type, color]) => (
          <div key={type} className="flex items-center gap-1.5 text-xs text-gray-500">
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
            {type}
          </div>
        ))}
      </div>
    </div>
  );
}
