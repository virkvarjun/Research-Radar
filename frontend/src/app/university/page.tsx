"use client";

import { useState } from "react";
import Navbar from "@/components/Navbar";
import PaperCard from "@/components/PaperCard";
import {
  searchInstitutions,
  getInstitutionPapers,
  getRelatedPapers,
  sendFeedback,
  type Institution,
  type Paper,
} from "@/lib/api";

export default function UniversityPage() {
  const [query, setQuery] = useState("");
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [selectedInst, setSelectedInst] = useState<Institution | null>(null);
  const [newPapers, setNewPapers] = useState<Paper[]>([]);
  const [relatedPapers, setRelatedPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setSearching(true);
    try {
      const data = await searchInstitutions(query);
      setInstitutions(data.institutions);
    } catch {
      setInstitutions([]);
    } finally {
      setSearching(false);
    }
  }

  async function selectInstitution(inst: Institution) {
    setSelectedInst(inst);
    setLoading(true);
    try {
      const [newData, relatedData] = await Promise.all([
        getInstitutionPapers(inst.id),
        getRelatedPapers(inst.id),
      ]);
      setNewPapers(newData);
      setRelatedPapers(relatedData);
    } catch {
      setNewPapers([]);
      setRelatedPapers([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-3xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">
          University Radar
        </h1>

        <form onSubmit={handleSearch} className="flex gap-2 mb-6">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for your institution..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            type="submit"
            disabled={searching}
            className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {searching ? "Searching..." : "Search"}
          </button>
        </form>

        {institutions.length > 0 && !selectedInst && (
          <div className="space-y-2 mb-6">
            {institutions.map((inst) => (
              <button
                key={inst.id}
                onClick={() => selectInstitution(inst)}
                className="w-full text-left p-3 bg-white rounded-lg border border-gray-200 hover:border-blue-300 transition-colors"
              >
                <p className="font-medium text-gray-900">{inst.name}</p>
                {inst.country && (
                  <p className="text-sm text-gray-500">{inst.country}</p>
                )}
              </button>
            ))}
          </div>
        )}

        {selectedInst && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">
                  {selectedInst.name}
                </h2>
              </div>
              <button
                onClick={() => {
                  setSelectedInst(null);
                  setNewPapers([]);
                  setRelatedPapers([]);
                }}
                className="text-sm text-blue-600 hover:underline"
              >
                Change institution
              </button>
            </div>

            {loading ? (
              <p className="text-gray-500 text-center py-8">Loading papers...</p>
            ) : (
              <>
                {/* New from my university */}
                <div className="mb-8">
                  <h3 className="text-md font-semibold text-gray-800 mb-3 flex items-center gap-2">
                    <span className="w-2 h-2 bg-blue-600 rounded-full" />
                    New from this university
                  </h3>
                  {newPapers.length === 0 ? (
                    <p className="text-gray-400 text-sm py-4">
                      No recent papers found from this institution.
                    </p>
                  ) : (
                    <div className="space-y-4">
                      {newPapers.map((paper) => (
                        <PaperCard
                          key={paper.id}
                          paper={paper}
                          onSave={() => sendFeedback(paper.id, "save")}
                          showActions={true}
                        />
                      ))}
                    </div>
                  )}
                </div>

                {/* Related elsewhere */}
                <div>
                  <h3 className="text-md font-semibold text-gray-800 mb-3 flex items-center gap-2">
                    <span className="w-2 h-2 bg-green-600 rounded-full" />
                    Related elsewhere
                  </h3>
                  <p className="text-xs text-gray-400 mb-3">
                    Papers from other institutions similar to this university&apos;s work and your interests.
                  </p>
                  {relatedPapers.length === 0 ? (
                    <p className="text-gray-400 text-sm py-4">
                      No related papers found yet.
                    </p>
                  ) : (
                    <div className="space-y-4">
                      {relatedPapers.map((paper) => (
                        <PaperCard
                          key={paper.id}
                          paper={paper}
                          onSave={() => sendFeedback(paper.id, "save")}
                          showActions={true}
                        />
                      ))}
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
