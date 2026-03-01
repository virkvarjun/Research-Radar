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
      <main className="max-w-3xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Saved Papers</h1>

        {loading ? (
          <p className="text-gray-500 text-center py-12">Loading...</p>
        ) : saved.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <p className="text-lg mb-2">No saved papers yet.</p>
            <p className="text-sm">Save papers from your feed to see them here.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {saved.map((s) => (
              <div key={s.id}>
                <PaperCard paper={s.paper} showActions={false} />
                <p className="text-xs text-gray-400 mt-1 ml-1">
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
