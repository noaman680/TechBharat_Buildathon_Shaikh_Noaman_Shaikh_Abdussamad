interface Props { quote: string; timestamp: string; }

export function EvidenceViewer({ quote, timestamp }: Props) {
  return (
    <div className="mt-2 bg-gray-50 border-l-4 border-blue-300 pl-3 py-2 rounded-r-lg">
      <p className="text-xs text-gray-500 mb-1">
        🎙️ <strong>Evidence</strong> at {timestamp}
      </p>
      <p className="text-sm text-gray-700 italic">&quot;{quote}&quot;</p>
    </div>
  );
}
