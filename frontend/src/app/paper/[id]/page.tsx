"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Navbar from "@/components/Navbar";
import RigourPanel from "@/components/RigourPanel";
import {
  getPaper,
  savePaper,
  chatWithPaper,
  type PaperDetail,
  type ChatResponse,
} from "@/lib/api";

export default function PaperPage() {
  const params = useParams();
  const paperId = params.id as string;

  const [paper, setPaper] = useState<PaperDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [chatQuestion, setChatQuestion] = useState("");
  const [chatResponse, setChatResponse] = useState<ChatResponse | null>(null);
  const [chatLoading, setChatLoading] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (!paperId) return;
    getPaper(paperId)
      .then(setPaper)
      .catch(() => setPaper(null))
      .finally(() => setLoading(false));
  }, [paperId]);

  async function handleSave() {
    try {
      await savePaper(paperId);
      setSaved(true);
    } catch {
      // ignore
    }
  }

  async function handleChat(e: React.FormEvent) {
    e.preventDefault();
    if (!chatQuestion.trim()) return;
    setChatLoading(true);
    try {
      const resp = await chatWithPaper(paperId, chatQuestion);
      setChatResponse(resp);
    } catch (err) {
      setChatResponse({
        answer: err instanceof Error ? err.message : "Chat failed. Save the paper first.",
        citations: [],
      });
    } finally {
      setChatLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="max-w-3xl mx-auto px-4 py-6">
          <p className="text-gray-500 text-center py-12">Loading paper...</p>
        </main>
      </div>
    );
  }

  if (!paper) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="max-w-3xl mx-auto px-4 py-6">
          <p className="text-red-500 text-center py-12">Paper not found.</p>
        </main>
      </div>
    );
  }

  const authors = paper.authors?.map((a) => a.name).join(", ");

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-3xl mx-auto px-4 py-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">{paper.title}</h1>

        {authors && <p className="text-sm text-gray-500 mb-2">{authors}</p>}

        <div className="flex items-center gap-2 text-xs text-gray-400 mb-4">
          <span className="px-2 py-0.5 bg-gray-100 rounded">{paper.source}</span>
          {paper.published_date && (
            <span>{new Date(paper.published_date).toLocaleDateString()}</span>
          )}
          {paper.doi && <span>DOI: {paper.doi}</span>}
          {paper.arxiv_id && <span>arXiv: {paper.arxiv_id}</span>}
          {paper.pdf_url && (
            <a
              href={paper.pdf_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              PDF
            </a>
          )}
        </div>

        <button
          onClick={handleSave}
          disabled={saved}
          className={`mb-6 px-4 py-2 text-sm rounded-md font-medium transition-colors ${
            saved
              ? "bg-green-100 text-green-700"
              : "bg-blue-600 text-white hover:bg-blue-700"
          }`}
        >
          {saved ? "Saved" : "Save Paper"}
        </button>

        {paper.abstract && (
          <div className="bg-white rounded-lg border border-gray-200 p-4 mb-4">
            <h2 className="text-sm font-semibold text-gray-900 mb-2">Abstract</h2>
            <p className="text-sm text-gray-700 leading-relaxed">{paper.abstract}</p>
          </div>
        )}

        {paper.rigour_panel && (
          <div className="mb-4">
            <RigourPanel panel={paper.rigour_panel} />
          </div>
        )}

        {/* Chat section */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h2 className="text-sm font-semibold text-gray-900 mb-3">
            Chat with Paper
          </h2>
          {!saved && (
            <p className="text-xs text-gray-400 mb-2">
              Save this paper first to enable chat.
            </p>
          )}
          <form onSubmit={handleChat} className="flex gap-2 mb-3">
            <input
              type="text"
              value={chatQuestion}
              onChange={(e) => setChatQuestion(e.target.value)}
              placeholder="Ask a question about this paper..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={chatLoading || !chatQuestion.trim()}
              className="px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {chatLoading ? "..." : "Ask"}
            </button>
          </form>

          {chatResponse && (
            <div className="mt-3">
              <div className="bg-gray-50 rounded-md p-3 text-sm text-gray-700 mb-2">
                {chatResponse.answer}
              </div>
              {chatResponse.citations.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-gray-500 mb-1">
                    Citations:
                  </p>
                  {chatResponse.citations.map((c, i) => (
                    <div
                      key={i}
                      className="text-xs text-gray-400 bg-gray-50 rounded p-2 mb-1"
                    >
                      <span className="font-medium">
                        [Chunk {c.chunk_index}]
                      </span>{" "}
                      {c.text.slice(0, 150)}...
                      <span className="ml-1 text-gray-300">
                        (score: {c.score.toFixed(3)})
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
