"use client";

import Link from "next/link";
import type { Paper } from "@/lib/api";

interface PaperCardProps {
  paper: Paper;
  onSave?: () => void;
  onSkip?: () => void;
  onNotRelevant?: () => void;
  showActions?: boolean;
}

export default function PaperCard({
  paper,
  onSave,
  onSkip,
  onNotRelevant,
  showActions = true,
}: PaperCardProps) {
  const authors = paper.authors?.slice(0, 3).map((a) => a.name).join(", ");
  const hasMore = (paper.authors?.length || 0) > 3;

  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-5 hover:shadow-md hover:border-gray-200 transition-all">
      <Link href={`/paper/${paper.id}`}>
        <h3 className="text-base font-semibold text-gray-900 hover:text-blue-600 transition-colors mb-1 leading-snug">
          {paper.title}
        </h3>
      </Link>

      {authors && (
        <p className="text-sm text-gray-400 mb-2">
          {authors}
          {hasMore && " et al."}
        </p>
      )}

      {paper.abstract && (
        <p className="text-sm text-gray-600 mb-3 line-clamp-3 leading-relaxed">
          {paper.abstract}
        </p>
      )}

      <div className="flex items-center gap-2 text-xs text-gray-400 mb-3 flex-wrap">
        {paper.source && (
          <span className="px-2 py-0.5 bg-gray-50 text-gray-500 rounded-md font-medium">
            {paper.source}
          </span>
        )}
        {paper.published_date && (
          <span>{new Date(paper.published_date).toLocaleDateString()}</span>
        )}
        {paper.categories?.slice(0, 3).map((cat) => (
          <span
            key={cat}
            className="px-2 py-0.5 bg-blue-50 text-blue-600 rounded-md font-medium"
          >
            {cat}
          </span>
        ))}
      </div>

      {/* Why matched */}
      {paper.why_matched && (
        <div className="text-xs text-gray-400 mb-3 bg-gray-50 rounded-lg px-3 py-2">
          <span className="font-medium text-gray-500">Why matched:</span>{" "}
          {(() => {
            const m = paper.why_matched as Record<string, number>;
            const parts: string[] = [];
            if (m.total_score != null)
              parts.push(`score ${m.total_score.toFixed(3)}`);
            if (m.user_similarity > 0)
              parts.push(`interest ${(m.user_similarity * 100).toFixed(0)}%`);
            if (m.thread_similarity > 0)
              parts.push(`thread ${(m.thread_similarity * 100).toFixed(0)}%`);
            if (m.novelty > 0)
              parts.push(`novelty ${(m.novelty * 100).toFixed(0)}%`);
            if (m.role_boost > 0)
              parts.push(`role boost +${m.role_boost.toFixed(2)}`);
            return parts.length > 0 ? parts.join("  ·  ") : "relevance match";
          })()}
        </div>
      )}

      {showActions && (
        <div className="flex gap-2 pt-1">
          {onSave && (
            <button
              onClick={onSave}
              className="px-4 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Save
            </button>
          )}
          {onSkip && (
            <button
              onClick={onSkip}
              className="px-4 py-1.5 bg-gray-100 text-gray-600 text-sm rounded-lg hover:bg-gray-200 transition-colors font-medium"
            >
              Skip
            </button>
          )}
          {onNotRelevant && (
            <button
              onClick={onNotRelevant}
              className="px-4 py-1.5 bg-red-50 text-red-500 text-sm rounded-lg hover:bg-red-100 transition-colors font-medium"
            >
              Not relevant
            </button>
          )}
        </div>
      )}
    </div>
  );
}
