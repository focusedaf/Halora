"use client";

import { AlertTriangle, ShieldAlert, ShieldCheck, XCircle } from "lucide-react";

import type {
  ClaimResult,
  UrlHealthBatchResponse,
  VerificationResponse,
} from "@/lib/api";

const VERDICT_STYLES: Record<string, string> = {
  SUPPORTED: "text-emerald-400",
  "PARTIALLY SUPPORTED": "text-yellow-400",
  UNSUPPORTED: "text-orange-400",
  CONTRADICTED: "text-red-400",
};

function getVerdictStyle(verdict: string) {
  return VERDICT_STYLES[verdict.toUpperCase()] ?? "text-zinc-400";
}

export default function VerificationResult({
  result,
}: {
  result: VerificationResponse;
}) {
  const summary = result.summary ?? {};

  const verified = summary.verified ?? 0;
  const partial = summary.partially_supported ?? 0;
  const unsupported = summary.unsupported ?? 0;
  const contradicted = summary.contradicted ?? 0;

  return (
    <div className="mt-3 w-full max-w-[75%] overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-800">
      <div className="border-b border-zinc-800 px-4 py-3">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-sm font-medium text-zinc-200">
              Verification Result
            </p>

            <p className="mt-0.5 text-xs text-zinc-500">
              {result.total_cited_claims} cited{" "}
              {result.total_cited_claims === 1 ? "claim" : "claims"} checked
            </p>
          </div>

          <div className="shrink-0 rounded-lg border border-zinc-800 bg-zinc-900 px-2.5 py-1 text-xs text-zinc-400">
            {result.status}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-4 divide-x divide-zinc-800 border-b border-zinc-800">
        <SummaryItem label="Supported" value={verified} type="supported" />
        <SummaryItem label="Partial" value={partial} type="partial" />
        <SummaryItem
          label="Unsupported"
          value={unsupported}
          type="unsupported"
        />
        <SummaryItem
          label="Contradicted"
          value={contradicted}
          type="contradicted"
        />
      </div>

      {result.results.length > 0 && (
        <div className="divide-y divide-zinc-800">
          {result.results.map((claim, index) => (
            <ClaimVerification
              key={`${claim.citation ?? "claim"}-${index}`}
              claim={claim}
            />
          ))}
        </div>
      )}

      {result.results.length === 0 && (
        <div className="px-4 py-5 text-center text-xs text-zinc-500">
          No cited claims were found to verify.
        </div>
      )}
    </div>
  );
}

function SummaryItem({
  label,
  value,
  type,
}: {
  label: string;
  value: number;
  type: "supported" | "partial" | "unsupported" | "contradicted";
}) {
  const icon =
    type === "supported" ? (
      <ShieldCheck className="size-3.5" />
    ) : type === "partial" ? (
      <AlertTriangle className="size-3.5" />
    ) : type === "unsupported" ? (
      <ShieldAlert className="size-3.5" />
    ) : (
      <XCircle className="size-3.5" />
    );

  const textColor =
    type === "supported"
      ? "text-emerald-400"
      : type === "partial"
        ? "text-yellow-400"
        : type === "unsupported"
          ? "text-orange-400"
          : "text-red-400";

  return (
    <div className="flex min-w-0 flex-col items-center justify-center px-2 py-3">
      <div className={`flex items-center gap-1 text-xs ${textColor}`}>
        {icon}

        <span className="truncate">{label}</span>
      </div>

      <span className="mt-1 text-lg font-semibold text-zinc-200">{value}</span>
    </div>
  );
}

function ClaimVerification({ claim }: { claim: ClaimResult }) {
  const verdict = (claim.final_verdict?.verdict ?? "UNKNOWN").toUpperCase();

  const confidence = claim.final_verdict?.confidence;
  const score = claim.final_verdict?.score;
  const reason = claim.final_verdict?.reason;

  const verdictColor = getVerdictStyle(verdict);

  return (
    <div className="px-4 py-4">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            {claim.citation && (
              <span className="rounded-md border border-zinc-800 bg-zinc-900 px-1.5 py-0.5 text-xs font-medium text-zinc-400">
                {claim.citation}
              </span>
            )}

            <span className={`text-xs font-semibold ${verdictColor}`}>
              {verdict}
            </span>
          </div>

          <p className="mt-2 text-sm leading-6 text-zinc-300">{claim.claim}</p>
        </div>

        <div className="shrink-0 text-right">
          {confidence !== undefined && (
            <p className="text-xs text-zinc-500">{confidence}% confidence</p>
          )}

          {score !== undefined && (
            <p className="mt-0.5 text-xs text-zinc-600">{score}/10</p>
          )}
        </div>
      </div>

      {reason && (
        <div className="mt-3 rounded-lg border border-zinc-800 bg-zinc-900/60 px-3 py-2.5">
          <p className="text-xs leading-5 text-zinc-500">{reason}</p>
        </div>
      )}

      {claim.reference && (
        <div className="mt-2">
          <p className="line-clamp-2 text-xs text-zinc-600">
            {claim.reference}
          </p>
        </div>
      )}

      {claim.paper?.title && (
        <div className="mt-2 text-xs text-zinc-500">
          <span>Source: {claim.paper.title}</span>

          {claim.paper.year && <span> ({claim.paper.year})</span>}

          {claim.paper.doi && (
            <>
              {" · "}
              <a
                href={`https://doi.org/${claim.paper.doi}`}
                target="_blank"
                rel="noreferrer"
                className="text-zinc-400 underline underline-offset-2 hover:text-zinc-200"
              >
                DOI
              </a>
            </>
          )}
        </div>
      )}
    </div>
  );
}

export function UrlHealthResult({
  result,
}: {
  result: UrlHealthBatchResponse;
}) {
  if (!result.results.length) {
    return null;
  }

  return (
    <div className="mt-3 w-full max-w-[75%] overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-800">
      <div className="border-b border-zinc-800 px-4 py-3">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-sm font-medium text-zinc-200">URL Health</p>

            <p className="mt-0.5 text-xs text-zinc-500">
              {result.total} URL{result.total === 1 ? "" : "s"} checked
            </p>
          </div>

          <div className="rounded-lg border border-zinc-800 bg-zinc-900 px-2.5 py-1 text-xs text-zinc-400">
            {result.status}
          </div>
        </div>
      </div>

      <div className="divide-y divide-zinc-800">
        {result.results.map((item) => (
          <div key={item.url} className="px-4 py-4">
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0 flex-1">
                <p className="break-all text-sm text-zinc-300">{item.url}</p>

                {item.live?.final_url && item.live.final_url !== item.url && (
                  <p className="mt-1 break-all text-xs text-zinc-600">
                    Final URL: {item.live.final_url}
                  </p>
                )}
              </div>

              <span className="shrink-0 rounded-md border border-zinc-800 bg-zinc-900 px-2 py-1 text-xs font-medium capitalize text-zinc-400">
                {item.health}
              </span>
            </div>

            {item.error && (
              <p className="mt-2 text-xs text-red-400">{item.error}</p>
            )}

            {item.recommended?.url && (
              <a
                href={item.recommended.url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-2 block break-all text-xs text-blue-400 underline underline-offset-2 hover:text-blue-300"
              >
                {item.recommended.type === "archive"
                  ? "View archived source"
                  : "Open source"}
              </a>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
