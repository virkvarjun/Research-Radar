"use client";

import { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import PaperCard from "@/components/PaperCard";
import { getSavedPapers, type SavedPaper } from "@/lib/api";

export default function SavedPage() {
  const [saved, setSaved] = useState<SavedPaper[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSavedPapers()
      .then(setSaved)
      .catch(() => setSaved([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-3xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Saved Papers</h1>
          <p className="text-sm text-gray-400 mt-1">
            Your research library — chat with any saved paper
          </p>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : saved.length === 0 ? (
          <div className="text-center py-20">
            <div className="text-5xl mb-4">📑</div>
            <p className="text-lg font-medium text-gray-900 mb-2">
              No saved papers yet
            </p>
            <p className="text-sm text-gray-400 max-w-sm mx-auto">
              Save papers from your feed to build your library and unlock Chat
              with Paper.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {saved.map((s) => (
              <div key={s.id}>
                <PaperCard paper={s.paper} showActions={false} />
                <p className="text-xs text-gray-400 mt-1.5 ml-2">
                  Saved {new Date(s.saved_at).toLocaleDateString()}
                </p>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
