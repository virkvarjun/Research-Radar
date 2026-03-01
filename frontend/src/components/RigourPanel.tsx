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

export default function RigourPanel({ panel }: RigourPanelProps) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <h3 className="text-sm font-semibold text-gray-900 mb-3">
        Evidence / Rigour Panel
      </h3>
      <div className="space-y-2">
        {Object.entries(panel).map(([key, value]) => (
          <div key={key} className="flex items-center justify-between text-sm">
            <span className="text-gray-600">{LABELS[key] || key}</span>
            <div className="flex items-center gap-2">
              <span>{value.indicator}</span>
              {key === "code_link" && value.url ? (
                <a
                  href={value.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline text-xs"
                >
                  Link
                </a>
              ) : value.count !== undefined ? (
                <span className="text-gray-400 text-xs">
                  {value.count} found
                </span>
              ) : (
                <span className="text-gray-400 text-xs">
                  {value.status === "not_found" ? "not found" : value.status}
                </span>
              )}
            </div>
          </div>
        ))}
      </div>
      <p className="text-xs text-gray-400 mt-3">
        Claims are grounded in extracted text. If insufficient text is available, items show &quot;not found&quot;.
      </p>
    </div>
  );
}
