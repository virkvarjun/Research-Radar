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
  code_link: "Code / Data Link",
};

const FIELD_ORDER = [
  "datasets",
  "metrics",
  "baselines",
  "code_link",
  "limitations",
];

export default function RigourPanel({ panel }: RigourPanelProps) {
  return (
    <div className="bg-white rounded-2xl border border-gray-100 p-5">
      <h3 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
        🔬 Evidence &amp; Rigour
      </h3>
      <div className="space-y-1">
        {FIELD_ORDER.map((key) => {
          const value = panel[key];
          if (!value) return null;
          const found = value.status === "found";
          return (
            <div
              key={key}
              className={`flex items-center justify-between py-2.5 px-3 rounded-xl transition-colors ${
                found ? "bg-green-50/50" : "bg-gray-50/50"
              }`}
            >
              <span className="text-sm text-gray-700 font-medium">
                {LABELS[key] || key}
              </span>
              <div className="flex items-center gap-2 text-xs">
                <span className="text-base">{value.indicator}</span>
                {key === "code_link" && value.url ? (
                  <a
                    href={value.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline font-medium"
                  >
                    {value.url.length > 35
                      ? value.url.slice(0, 35) + "…"
                      : value.url}
                  </a>
                ) : value.count !== undefined && value.count > 0 ? (
                  <span className="text-gray-500 font-medium">
                    {value.count} found
                  </span>
                ) : (
                  <span className="text-gray-400">
                    {value.status === "not_found"
                      ? "not found in text"
                      : value.status}
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Extracted items */}
      {FIELD_ORDER.map((key) => {
        const value = panel[key];
        if (!value?.items || value.items.length === 0) return null;
        return (
          <div key={`${key}-items`} className="mt-3">
            <p className="text-xs font-medium text-gray-500 mb-1.5 ml-1">
              {LABELS[key]}:
            </p>
            <div className="flex flex-wrap gap-1.5 ml-1">
              {value.items.slice(0, 6).map((item, idx) => (
                <span
                  key={idx}
                  className="inline-block text-xs bg-gray-100 text-gray-600 rounded-lg px-2.5 py-1"
                >
                  {typeof item === "string"
                    ? item
                    : typeof item === "object" && item !== null
                    ? `${(item as Record<string, string>).name || ""}: ${
                        (item as Record<string, string>).value || ""
                      }`
                    : String(item)}
                </span>
              ))}
              {value.items.length > 6 && (
                <span className="text-xs text-gray-400 self-center">
                  +{value.items.length - 6} more
                </span>
              )}
            </div>
          </div>
        );
      })}

      <p className="text-xs text-gray-400 mt-4 pt-3 border-t border-gray-100 leading-relaxed">
        Evidence is extracted from the paper text. Items marked ❌ were not found
        in the available text. &quot;Not found&quot; means insufficient evidence,
        not necessarily absence.
      </p>
    </div>
  );
}
