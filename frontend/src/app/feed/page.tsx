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
    } catch {
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
      setPapers((prev) => prev.filter((p) => p.id !== paperId));
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-3xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Your Feed</h1>
            <p className="text-sm text-gray-400 mt-1">
              Papers ranked by your interests
            </p>
          </div>
          <button
            onClick={() => loadFeed(true)}
            disabled={loading}
            className="px-5 py-2 bg-blue-600 text-white text-sm font-medium rounded-xl hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-sm"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Loading
              </span>
            ) : (
              "↻ Refresh"
            )}
          </button>
        </div>

        {error && (
          <div className="bg-red-50 text-red-600 p-4 rounded-xl mb-6 text-sm">
            {error}
          </div>
        )}

        {!loading && papers.length === 0 && !error && (
          <div className="text-center py-20">
            <div className="text-5xl mb-4">📭</div>
            <p className="text-lg font-medium text-gray-900 mb-2">
              No papers in your feed yet
            </p>
            <p className="text-sm text-gray-400 max-w-sm mx-auto">
              Complete onboarding or wait for the daily ingestion job to populate
              your personalized feed.
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
