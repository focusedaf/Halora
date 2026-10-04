export interface FinalVerdict {
  verdict: string;
  confidence?: number;
  score?: number;
  llm_classification?: string;
  reason?: string;
}

export interface VerificationData {
  status?: string;
  classification?: string;
  score?: number;
  reasoning?: string;
  key_differences?: string[];
}

export interface ClaimResult {
  citation?: string;
  reference_number?: string;
  claim: string;
  context?: string;
  reference_found?: boolean;
  reference?: string | null;

  metadata?: {
    raw?: string;
    title?: string;
    authors?: string[];
    year?: number | string;
    doi?: string | null;
    url?: string | null;
    arxiv_id?: string | null;
  } | null;

  paper?: {
    title?: string;
    authors?: unknown;
    year?: number | string;
    doi?: string;
    source?: string;
    title_similarity?: number;
    ranking_score?: number;
  } | null;

  verification?: VerificationData | null;

  final_verdict?: FinalVerdict;
}

export interface VerificationSummary {
  verified?: number;
  partially_supported?: number;
  unsupported?: number;
  contradicted?: number;
  citation_mismatch?: number;
  source_not_found?: number;
  no_evidence?: number;
  verification_error?: number;
  reference_not_found?: number;
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
  const res = await fetch("http://localhost:8000/api/verify-response", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      response,
      top_k: topK,
    }),
    signal,
  });

  if (!res.ok) {
    let detail = `Request failed (${res.status})`;

    try {
      const data = await res.json();
      detail = data.detail ?? detail;
    } catch {}

    throw new Error(detail);
  }

  return res.json();
}
