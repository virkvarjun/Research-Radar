"use client";

import { useState } from "react";
import Navbar from "@/components/Navbar";
import PaperCard from "@/components/PaperCard";
import {
  searchInstitutions,
  getInstitutionPapers,
  sendFeedback,
  type Institution,
  type Paper,
} from "@/lib/api";

export default function UniversityPage() {
  const [query, setQuery] = useState("");
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [selectedInst, setSelectedInst] = useState<Institution | null>(null);
  const [papers, setPapers] = useState<Paper[]>([]);
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
      const data = await getInstitutionPapers(inst.id);
      setPapers(data);
    } catch {
      setPapers([]);
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
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">
                  {selectedInst.name}
                </h2>
                <p className="text-sm text-gray-500">New papers from this institution</p>
              </div>
              <button
                onClick={() => {
                  setSelectedInst(null);
                  setPapers([]);
                }}
                className="text-sm text-blue-600 hover:underline"
              >
                Change institution
              </button>
            </div>

            {loading ? (
              <p className="text-gray-500 text-center py-8">Loading papers...</p>
            ) : papers.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                No recent papers found from this institution.
              </p>
            ) : (
              <div className="space-y-4">
                {papers.map((paper) => (
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
        )}
      </main>
    </div>
  );
}
