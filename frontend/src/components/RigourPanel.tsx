"use client";

interface RigourPanelProps {
  panel: Record<
    string,
    {
      status: string;
      indicator: string;
      items?: unknown[];
      count?: number;
      url?: string;
    }
  >;
}

const LABELS: Record<string, string> = {
  datasets: "Datasets",
  metrics: "Metrics",
  baselines: "Baselines",
  limitations: "Limitations",
  code_link: "Code/Data Link",
};

const FIELD_ORDER = ["datasets", "metrics", "baselines", "code_link", "limitations"];

export default function RigourPanel({ panel }: RigourPanelProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <h3 className="text-sm font-semibold text-gray-900 mb-3">
        Evidence / Rigour Panel
      </h3>
      <div className="space-y-3">
        {FIELD_ORDER.map((key) => {
          const value = panel[key];
          if (!value) return null;
          return (
            <div key={key} className="border-b border-gray-50 pb-2 last:border-0 last:pb-0">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600 font-medium">{LABELS[key] || key}</span>
                <div className="flex items-center gap-2">
                  <span>{value.indicator}</span>
                  {key === "code_link" && value.url ? (
                    <a
                      href={value.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline text-xs"
                    >
                      {value.url.length > 40 ? value.url.slice(0, 40) + "…" : value.url}
                    </a>
                  ) : value.count !== undefined && value.count > 0 ? (
                    <span className="text-gray-500 text-xs">
                      {value.count} found
                    </span>
                  ) : (
                    <span className="text-gray-400 text-xs">
                      {value.status === "not_found" ? "not found" : value.status}
                    </span>
                  )}
                </div>
              </div>
              {/* Show extracted items */}
              {value.items && value.items.length > 0 && (
                <div className="mt-1 ml-4">
                  {value.items.slice(0, 5).map((item, idx) => (
                    <span
                      key={idx}
                      className="inline-block text-xs bg-gray-50 text-gray-600 rounded px-1.5 py-0.5 mr-1 mb-1"
                    >
                      {typeof item === "string"
                        ? item
                        : typeof item === "object" && item !== null
                        ? `${(item as Record<string, string>).name || ""}: ${(item as Record<string, string>).value || ""}`
                        : String(item)}
                    </span>
                  ))}
                  {value.items.length > 5 && (
                    <span className="text-xs text-gray-400">
                      +{value.items.length - 5} more
                    </span>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
      <p className="text-xs text-gray-400 mt-3 border-t border-gray-100 pt-2">
        Evidence is extracted from the paper text. Items marked ❌ were not found in the available text.
        Claims are grounded in extracted spans — &quot;not found&quot; means insufficient evidence.
      </p>
    </div>
  );
}
