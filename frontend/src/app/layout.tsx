import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "sonner";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "MeetMind — Agentic AI Meeting Assistant",
  description: "Transform meetings into structured intelligence and executed action items",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <nav className="border-b bg-white px-6 py-3 flex items-center gap-4 shadow-sm">
          <span className="text-xl font-bold text-blue-600">🧠 MeetMind</span>
          <span className="text-sm text-gray-500">Agentic AI Meeting Assistant</span>
          <div className="ml-auto flex gap-4">
            <a href="/" className="text-sm text-gray-600 hover:text-blue-600">Upload</a>
            <a href="/analytics" className="text-sm text-gray-600 hover:text-blue-600">Analytics</a>
          </div>
        </nav>
        <main className="min-h-screen bg-gray-50">
          {children}
        </main>
        <Toaster position="top-right" richColors />
      </body>
    </html>
  );
}
