import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "MeetMind — Agentic AI Meeting Assistant",
  description: "Turn meetings into tracked, approved, executed action items.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 text-gray-900">{children}</body>
    </html>
  );
}
