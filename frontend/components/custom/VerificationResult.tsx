import type { VerificationResponse } from "@/lib/api";

const COLORS: Record<string, string> = {
  SUPPORTED: "text-emerald-400 border-emerald-800",
  "PARTIALLY SUPPORTED": "text-amber-400 border-amber-800",
  UNSUPPORTED: "text-red-400 border-red-800",
  CONTRADICTED: "text-red-400 border-red-800",
};

export default function VerificationResult({ data }: { data: VerificationResponse }) {
  if (data.status !== "success") {
    return (
      <p className="text-sm text-red-400">
        Verification failed ({data.status}){data.error ? `: ${data.error}` : ""}.
      </p>
    );
  }

  const s = data.summary ?? {};
  const stats: [string, number | undefined][] = [
    ["Supported", s.verified],
    ["Partial", s.partially_supported],
    ["Unsupported", s.unsupported],
    ["Contradicted", s.contradicted],
    ["Source not found", (s.source_not_found ?? 0) + (s.reference_not_found ?? 0)],
  ];

  return (
    <div className="flex w-full max-w-[85%] flex-col gap-3 text-sm text-zinc-200">
      <div className="rounded-2xl border border-zinc-800 bg-zinc-900 px-4 py-3">
        <p className="mb-2 font-medium">
          {data.total_cited_claims} cited claim(s) · {data.total_references} reference(s)
        </p>
        <div className="flex flex-wrap gap-2 text-xs">
          {stats.map(([label, n]) => (
            <span key={label} className="rounded-full bg-zinc-800 px-2.5 py-1">
              {label}: {n ?? 0}
            </span>
          ))}
        </div>
      </div>

      {data.results.map((r, i) => {
        const verdict = (r.final_verdict?.verdict ?? "UNKNOWN").toUpperCase();
        return (
          <div key={i} className="rounded-2xl border border-zinc-800 bg-zinc-900 px-4 py-3">
            <span
              className={`rounded-full border px-2 py-0.5 text-xs font-semibold ${
                COLORS[verdict] ?? "border-zinc-700 text-zinc-400"
              }`}
            >
              {verdict}
              {r.final_verdict?.confidence != null && ` · ${r.final_verdict.confidence}%`}
            </span>
            <p className="mt-2">{r.claim}</p>
            {r.paper?.title && (
              <p className="mt-1 text-xs text-zinc-500">
                Source: {r.paper.title}
                {r.paper.year ? ` (${r.paper.year})` : ""}
                {r.paper.doi && (
                  <>
                    {" · "}
                    <a
                      className="underline"
                      href={`https://doi.org/${r.paper.doi}`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      DOI
                    </a>
                  </>
                )}
              </p>
            )}
            {r.final_verdict?.reason && (
              <p className="mt-2 text-xs text-zinc-400">{r.final_verdict.reason}</p>
            )}
          </div>
        );
      })}
    </div>
  );
}
