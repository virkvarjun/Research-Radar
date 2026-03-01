"use client";

import { useEffect, useState, useCallback } from "react";
import Navbar from "@/components/Navbar";
import PaperCard from "@/components/PaperCard";
import { getFeed, sendFeedback, type Paper } from "@/lib/api";

export default function FeedPage() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadFeed = useCallback(async (refresh = false) => {
    setLoading(true);
    setError("");
    try {
      const data = await getFeed(refresh);
      setPapers(data.papers);
    } catch (err) {
      setError("Failed to load feed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadFeed();
  }, [loadFeed]);

  async function handleAction(paperId: string, action: string) {
    try {
      await sendFeedback(paperId, action);
      setPapers((prev) => prev.filter((p) => p.id !== paperId));
    } catch {
      // Optimistically remove even if API fails
      setPapers((prev) => prev.filter((p) => p.id !== paperId));
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-3xl mx-auto px-4 py-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Your Feed</h1>
          <button
            onClick={() => loadFeed(true)}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {loading ? "Loading..." : "Refresh"}
          </button>
        </div>

        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-4 text-sm">
            {error}
          </div>
        )}

        {!loading && papers.length === 0 && !error && (
          <div className="text-center py-12 text-gray-500">
            <p className="text-lg mb-2">No papers in your feed yet.</p>
            <p className="text-sm">
              Complete onboarding or wait for the daily ingestion job.
            </p>
          </div>
        )}

        <div className="space-y-4">
          {papers.map((paper) => (
            <PaperCard
              key={paper.id}
              paper={paper}
              onSave={() => handleAction(paper.id, "save")}
              onSkip={() => handleAction(paper.id, "skip")}
              onNotRelevant={() => handleAction(paper.id, "not_relevant")}
            />
          ))}
        </div>
      </main>
    </div>
  );
}
