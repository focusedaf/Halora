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

export interface PaperData {
  title?: string;
  authors?: unknown;
  year?: number | string;
  doi?: string | null;
  source?: string;
  title_similarity?: number;
  ranking_score?: number;
}

export interface SourceData {
  status?: string;
  source?: string;
  title?: string;
  url?: string | null;
  content_type?: string;
}

export interface EvidenceItem {
  rank?: number;
  text?: string;
  similarity?: number;
  coverage?: number;
}

export interface CitationMetadata {
  raw?: string;
  title?: string;
  authors?: string[];
  year?: number;
  doi?: string | null;
  url?: string | null;
  arxiv_id?: string | null;
}

export interface ClaimResult {
  citation: string;
  reference_number?: string;

  claim: string;
  context?: string;

  reference_found?: boolean;
  reference?: string | null;

  metadata?: CitationMetadata | null;

  paper?: PaperData | null;
  source?: SourceData | null;

  evidence?: EvidenceItem[];

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

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function verifyResponse(
  response: string,
  topK = 5,
  signal?: AbortSignal,
): Promise<VerificationResponse> {
  const res = await fetch(`${API_URL}/api/verify-response`, {
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

      if (typeof data?.detail === "string") {
        detail = data.detail;
      }
    } catch {
      // Keep default error message
    }

    throw new Error(detail);
  }

  return res.json();
}
