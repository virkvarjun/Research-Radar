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
  const [chatHistory, setChatHistory] = useState<
    { question: string; response: ChatResponse }[]
  >([]);
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
      /* ignore */
    }
  }

  async function handleChat(e: React.FormEvent) {
    e.preventDefault();
    if (!chatQuestion.trim()) return;
    const q = chatQuestion;
    setChatQuestion("");
    setChatLoading(true);
    try {
      const resp = await chatWithPaper(paperId, q);
      setChatHistory((prev) => [...prev, { question: q, response: resp }]);
    } catch (err) {
      setChatHistory((prev) => [
        ...prev,
        {
          question: q,
          response: {
            answer:
              err instanceof Error
                ? err.message
                : "Chat failed. Save the paper first.",
            citations: [],
          },
        },
      ]);
    } finally {
      setChatLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="max-w-3xl mx-auto px-4 py-8">
          <div className="flex items-center justify-center py-20">
            <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
          </div>
        </main>
      </div>
    );
  }

  if (!paper) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main className="max-w-3xl mx-auto px-4 py-8">
          <div className="text-center py-20">
            <div className="text-5xl mb-4">🔍</div>
            <p className="text-lg font-medium text-gray-900 mb-2">
              Paper not found
            </p>
            <p className="text-sm text-gray-400">
              This paper may have been removed or the link is invalid.
            </p>
          </div>
        </main>
      </div>
    );
  }

  const authors = paper.authors?.map((a) => a.name).join(", ");

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-3xl mx-auto px-4 py-8">
        {/* Title */}
        <h1 className="text-2xl font-bold text-gray-900 mb-2 leading-snug">
          {paper.title}
        </h1>

        {authors && (
          <p className="text-sm text-gray-400 mb-3">{authors}</p>
        )}

        {/* Metadata pills */}
        <div className="flex items-center gap-2 text-xs text-gray-400 mb-5 flex-wrap">
          <span className="px-2.5 py-1 bg-gray-100 text-gray-500 rounded-md font-medium">
            {paper.source}
          </span>
          {paper.published_date && (
            <span className="px-2.5 py-1 bg-gray-50 rounded-md">
              {new Date(paper.published_date).toLocaleDateString()}
            </span>
          )}
          {paper.doi && (
            <span className="px-2.5 py-1 bg-gray-50 rounded-md">
              DOI: {paper.doi}
            </span>
          )}
          {paper.arxiv_id && (
            <span className="px-2.5 py-1 bg-gray-50 rounded-md">
              arXiv: {paper.arxiv_id}
            </span>
          )}
          {paper.pdf_url && (
            <a
              href={paper.pdf_url}
              target="_blank"
              rel="noopener noreferrer"
              className="px-2.5 py-1 bg-blue-50 text-blue-600 rounded-md font-medium hover:bg-blue-100 transition-colors"
            >
              📄 PDF
            </a>
          )}
        </div>

        {/* Save button */}
        <button
          onClick={handleSave}
          disabled={saved}
          className={`mb-6 px-5 py-2 text-sm rounded-xl font-medium transition-all ${
            saved
              ? "bg-green-50 text-green-700 border border-green-200"
              : "bg-blue-600 text-white hover:bg-blue-700 shadow-sm"
          }`}
        >
          {saved ? "✓ Saved" : "Save Paper"}
        </button>

        {/* Abstract */}
        {paper.abstract && (
          <div className="bg-white rounded-2xl border border-gray-100 p-5 mb-5">
            <h2 className="text-sm font-semibold text-gray-900 mb-3">
              Abstract
            </h2>
            <p className="text-sm text-gray-600 leading-relaxed">
              {paper.abstract}
            </p>
          </div>
        )}

        {/* Rigour Panel */}
        {paper.rigour_panel && (
          <div className="mb-5">
            <RigourPanel panel={paper.rigour_panel} />
          </div>
        )}

        {/* Chat section */}
        <div className="bg-white rounded-2xl border border-gray-100 p-5">
          <h2 className="text-sm font-semibold text-gray-900 mb-1">
            💬 Chat with Paper
          </h2>
          {!saved && (
            <p className="text-xs text-gray-400 mb-3">
              Save this paper first to enable chat.
            </p>
          )}

          {/* Chat history */}
          {chatHistory.length > 0 && (
            <div className="space-y-4 mb-4 max-h-96 overflow-y-auto">
              {chatHistory.map((entry, i) => (
                <div key={i}>
                  <div className="flex gap-2 items-start mb-2">
                    <span className="text-xs font-bold text-blue-600 mt-0.5 flex-shrink-0">
                      Q:
                    </span>
                    <p className="text-sm text-gray-900 font-medium">
                      {entry.question}
                    </p>
                  </div>
                  <div className="bg-gray-50 rounded-xl p-4 text-sm text-gray-700 leading-relaxed ml-4">
                    {entry.response.answer}
                  </div>
                  {entry.response.citations.length > 0 && (
                    <div className="ml-4 mt-2">
                      <p className="text-xs font-medium text-gray-400 mb-1">
                        Citations:
                      </p>
                      {entry.response.citations.map((c, ci) => (
                        <div
                          key={ci}
                          className="text-xs text-gray-400 bg-gray-50 rounded-lg p-2 mb-1"
                        >
                          <span className="font-medium text-gray-500">
                            [Chunk {c.chunk_index}]
                          </span>{" "}
                          {c.text.slice(0, 150)}…
                          <span className="ml-1 text-gray-300">
                            (score: {c.score.toFixed(3)})
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Chat input */}
          <form onSubmit={handleChat} className="flex gap-2">
            <input
              type="text"
              value={chatQuestion}
              onChange={(e) => setChatQuestion(e.target.value)}
              placeholder="Ask a question about this paper…"
              className="flex-1 px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-gray-50"
            />
            <button
              type="submit"
              disabled={chatLoading || !chatQuestion.trim()}
              className="px-5 py-2.5 bg-blue-600 text-white text-sm font-medium rounded-xl hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-sm"
            >
              {chatLoading ? (
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin inline-block" />
              ) : (
                "Ask"
              )}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
