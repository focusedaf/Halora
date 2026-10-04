export interface FinalVerdict {
  verdict: string; // SUPPORTED | PARTIALLY SUPPORTED | UNSUPPORTED | CONTRADICTED | PAPER NOT FOUND | ...
  confidence?: number;
  score?: number;
  reason?: string;
}

export interface ClaimResult {
  claim: string;
  citation?: unknown;
  paper?: {
    title?: string;
    authors?: unknown;
    year?: number | string;
    doi?: string;
  } | null;
  verification?: { reasoning?: string; key_differences?: string[] } | null;
  final_verdict?: FinalVerdict;
}

export interface VerificationSummary {
  verified?: number;
  partially_supported?: number;
  unsupported?: number;
  contradicted?: number;
  source_not_found?: number;
  reference_not_found?: number;
  verification_error?: number;
  no_evidence?: number;
}

export interface VerificationResponse {
  status: string;
  error?: string;
  total_citations: number;
  total_references: number;
  total_cited_claims: number;
  summary: VerificationSummary;
  results: ClaimResult[];
}

export async function verifyResponse(
  response: string,
  topK = 5,
  signal?: AbortSignal,
): Promise<VerificationResponse> {
  const res = await fetch("/api/verify-response", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ response, top_k: topK }),
    signal,
  });
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {}
    throw new Error(detail);
  }
  return res.json();
}
