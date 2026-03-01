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
      <main className="max-w-3xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">University Radar</h1>
          <p className="text-sm text-gray-400 mt-1">
            Track your institution&apos;s output and discover related work
          </p>
        </div>

        <form onSubmit={handleSearch} className="flex gap-2 mb-8">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search for your institution…"
            className="flex-1 px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          />
          <button
            type="submit"
            disabled={searching}
            className="px-5 py-2.5 bg-blue-600 text-white text-sm font-medium rounded-xl hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-sm"
          >
            {searching ? "Searching…" : "Search"}
          </button>
        </form>

        {/* Institution results */}
        {institutions.length > 0 && !selectedInst && (
          <div className="space-y-2 mb-8">
            {institutions.map((inst) => (
              <button
                key={inst.id}
                onClick={() => selectInstitution(inst)}
                className="w-full text-left p-4 bg-white rounded-xl border border-gray-100 hover:border-blue-300 hover:shadow-sm transition-all"
              >
                <p className="font-medium text-gray-900">{inst.name}</p>
                {inst.country && (
                  <p className="text-sm text-gray-400">{inst.country}</p>
                )}
              </button>
            ))}
          </div>
        )}

        {/* Selected institution view */}
        {selectedInst && (
          <div>
            <div className="flex items-center justify-between mb-6 bg-white rounded-xl border border-gray-100 p-4">
              <div>
                <p className="text-xs text-gray-400 font-medium uppercase tracking-wide">
                  Showing papers for
                </p>
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
                className="text-sm text-blue-600 hover:underline font-medium"
              >
                Change
              </button>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-16">
                <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
              </div>
            ) : (
              <>
                {/* New from university */}
                <div className="mb-10">
                  <h3 className="text-base font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <span className="w-2 h-2 bg-blue-600 rounded-full" />
                    New from this university
                  </h3>
                  {newPapers.length === 0 ? (
                    <div className="text-center py-10 bg-white rounded-xl border border-gray-100">
                      <p className="text-gray-400 text-sm">
                        No recent papers found from this institution.
                      </p>
                    </div>
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
                  <h3 className="text-base font-semibold text-gray-900 mb-1 flex items-center gap-2">
                    <span className="w-2 h-2 bg-green-600 rounded-full" />
                    Related elsewhere
                  </h3>
                  <p className="text-xs text-gray-400 mb-4">
                    Papers from other institutions similar to this
                    university&apos;s work and your interests.
                  </p>
                  {relatedPapers.length === 0 ? (
                    <div className="text-center py-10 bg-white rounded-xl border border-gray-100">
                      <p className="text-gray-400 text-sm">
                        No related papers found yet.
                      </p>
                    </div>
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
