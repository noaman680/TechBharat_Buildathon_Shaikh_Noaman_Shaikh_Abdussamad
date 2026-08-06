"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { uploadMeeting } from "@/lib/api";

const ACCEPTED_TYPES = {
  "text/plain": [".txt"],
  "text/vtt": [".vtt"],
  "application/x-subrip": [".srt"],
  "audio/mpeg": [".mp3"],
  "audio/wav": [".wav"],
  "audio/mp4": [".m4a"],
  "video/mp4": [".mp4"],
  "video/webm": [".webm"],
};

const INTEGRATIONS = ["jira", "github", "slack", "linear", "notion", "asana", "google_calendar"];

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [meetingDate, setMeetingDate] = useState(new Date().toISOString().split("T")[0]);
  const [timezone, setTimezone] = useState("Asia/Kolkata");
  const [participants, setParticipants] = useState("");
  const [selectedIntegrations, setSelectedIntegrations] = useState<string[]>(["jira", "slack"]);
  const [uploading, setUploading] = useState(false);

  const onDrop = useCallback((accepted: File[]) => {
    if (accepted.length > 0) setFile(accepted[0]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxFiles: 1,
  });

  const handleSubmit = async () => {
    if (!file) { toast.error("Please select a file"); return; }
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      fd.append("meeting_date", meetingDate);
      fd.append("timezone", timezone);
      fd.append("participants", JSON.stringify(
        participants.split(",").map((e) => e.trim()).filter(Boolean)
      ));
      fd.append("org_id", "demo-org");
      fd.append("user_id", "demo-user");

      const result = await uploadMeeting(fd);
      toast.success("Meeting uploaded! Processing started.");
      router.push(`/meetings/${result.meeting_id}`);
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <div className="text-center mb-10">
        <h1 className="text-4xl font-bold text-gray-900 mb-3">🧠 MeetMind</h1>
        <p className="text-xl text-gray-600">Transform meetings into structured intelligence</p>
        <p className="text-sm text-gray-500 mt-2">Upload audio, video, or a transcript — our AI does the rest</p>
      </div>

      {/* Drop Zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-colors
          ${isDragActive ? "border-blue-500 bg-blue-50" : "border-gray-300 hover:border-blue-400 bg-white"}`}
      >
        <input {...getInputProps()} />
        {file ? (
          <div>
            <p className="text-2xl mb-2">📄</p>
            <p className="font-semibold text-gray-800">{file.name}</p>
            <p className="text-sm text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
          </div>
        ) : (
          <div>
            <p className="text-4xl mb-3">📁</p>
            <p className="font-semibold text-gray-700">Drop your meeting file here</p>
            <p className="text-sm text-gray-500 mt-1">TXT, VTT, SRT, MP3, MP4, WAV, M4A, WebM</p>
          </div>
        )}
      </div>

      {/* Config */}
      <div className="mt-6 grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Meeting Date</label>
          <input type="date" value={meetingDate}
            onChange={(e) => setMeetingDate(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Timezone</label>
          <select value={timezone} onChange={(e) => setTimezone(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option value="Asia/Kolkata">IST — Asia/Kolkata</option>
            <option value="UTC">UTC</option>
            <option value="America/New_York">EST — New York</option>
            <option value="America/Los_Angeles">PST — Los Angeles</option>
            <option value="Europe/London">GMT — London</option>
          </select>
        </div>
      </div>

      <div className="mt-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Participant Emails (comma-separated, optional)
        </label>
        <input type="text" value={participants}
          onChange={(e) => setParticipants(e.target.value)}
          placeholder="alice@company.com, bob@company.com"
          className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>

      {/* Integrations */}
      <div className="mt-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">Send to Integrations</label>
        <div className="flex flex-wrap gap-2">
          {INTEGRATIONS.map((integ) => (
            <button key={integ} onClick={() => setSelectedIntegrations((prev) =>
              prev.includes(integ) ? prev.filter((i) => i !== integ) : [...prev, integ]
            )}
              className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors
                ${selectedIntegrations.includes(integ)
                  ? "bg-blue-600 text-white border-blue-600"
                  : "bg-white text-gray-600 border-gray-300 hover:border-blue-400"}`}>
              {integ}
            </button>
          ))}
        </div>
      </div>

      <button onClick={handleSubmit} disabled={!file || uploading}
        className="mt-8 w-full bg-blue-600 text-white rounded-xl py-3 font-semibold
          hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
        {uploading ? "Uploading & Processing..." : "🚀 Process Meeting"}
      </button>

      {/* Feature Pills */}
      <div className="mt-6 flex flex-wrap gap-2 justify-center text-xs text-gray-500">
        {["✅ Human approval before execution", "🔒 Zero unapproved actions",
          "🧠 Cross-meeting memory", "📊 Confidence scoring"].map((f) => (
          <span key={f} className="bg-gray-100 px-3 py-1 rounded-full">{f}</span>
        ))}
      </div>
    </div>
  );
}
