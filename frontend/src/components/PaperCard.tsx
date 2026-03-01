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
    <div className="bg-white rounded-lg border border-gray-200 p-5 hover:shadow-md transition-shadow">
      <Link href={`/paper/${paper.id}`}>
        <h3 className="text-lg font-semibold text-gray-900 hover:text-blue-600 transition-colors mb-1">
          {paper.title}
        </h3>
      </Link>

      {authors && (
        <p className="text-sm text-gray-500 mb-2">
          {authors}
          {hasMore && " et al."}
        </p>
      )}

      {paper.abstract && (
        <p className="text-sm text-gray-700 mb-3 line-clamp-3">
          {paper.abstract}
        </p>
      )}

      <div className="flex items-center gap-2 text-xs text-gray-400 mb-3">
        {paper.source && (
          <span className="px-2 py-0.5 bg-gray-100 rounded">{paper.source}</span>
        )}
        {paper.published_date && (
          <span>{new Date(paper.published_date).toLocaleDateString()}</span>
        )}
        {paper.categories?.slice(0, 3).map((cat) => (
          <span key={cat} className="px-2 py-0.5 bg-blue-50 text-blue-600 rounded">
            {cat}
          </span>
        ))}
      </div>

      {paper.why_matched && (
        <div className="text-xs text-gray-400 mb-3">
          <span className="font-medium">Match:</span>{" "}
          score {(paper.why_matched as Record<string, number>).total_score?.toFixed(3)}
          {(paper.why_matched as Record<string, number>).user_similarity > 0 && (
            <span> · interest {((paper.why_matched as Record<string, number>).user_similarity * 100).toFixed(0)}%</span>
          )}
        </div>
      )}

      {showActions && (
        <div className="flex gap-2">
          {onSave && (
            <button
              onClick={onSave}
              className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors"
            >
              Save
            </button>
          )}
          {onSkip && (
            <button
              onClick={onSkip}
              className="px-3 py-1.5 bg-gray-100 text-gray-700 text-sm rounded-md hover:bg-gray-200 transition-colors"
            >
              Skip
            </button>
          )}
          {onNotRelevant && (
            <button
              onClick={onNotRelevant}
              className="px-3 py-1.5 bg-red-50 text-red-600 text-sm rounded-md hover:bg-red-100 transition-colors"
            >
              Not relevant
            </button>
          )}
        </div>
      )}
    </div>
  );
}
