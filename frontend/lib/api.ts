const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ??
  (process.env.NODE_ENV === "production" ? "" : "http://localhost:8000");

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

export type UrlHealth =
  | "alive"
  | "restricted"
  | "archived"
  | "dead"
  | "unreachable"
  | "unsafe"
  | "invalid";

export interface ArchiveSnapshot {
  provider: string;
  status: string;
  snapshot_url?: string | null;
  captured_at?: string | null;
  http_status?: number | null;
  error?: string | null;
  newly_created?: boolean;
}

export interface CascadeStep {
  stage: string;
  status: string;
  detail?: string | number | null;
  duration_ms?: number | null;
}

export interface UrlHealthResult {
  url: string;
  normalized_url?: string | null;
  health: UrlHealth;
  error?: string;
  cached?: boolean;
  live?: {
    status: string;
    final_url: string;
    http_status?: number | null;
    title?: string | null;
    reason?: string | null;
  } | null;
  archive?: {
    checked: boolean;
    best: ArchiveSnapshot | null;
    snapshots: ArchiveSnapshot[];
  } | null;
  recommended?: {
    type: "live" | "archive";
    url: string;
    provider?: string;
  } | null;
  cascade: CascadeStep[];
  checked_at?: string;
}

export interface UrlHealthBatchResponse {
  status: string;
  total: number;
  summary: Partial<Record<UrlHealth, number>>;
  results: UrlHealthResult[];
  extracted_urls?: string[];
}

export interface UrlHealthOptions {
  mode?: "first_hit" | "all";
  providers?: string[];
  preserve?: boolean;
  refresh?: boolean;
}

export interface UrlHealthProvider {
  name: string;
  label: string;
  supports_save: boolean;
  save_configured: boolean;
}

async function request<T>(
  path: string,
  init: {
    method?: "GET" | "POST";
    body?: unknown;
    signal?: AbortSignal;
  } = {},
): Promise<T> {
  const { method = "GET", body, signal } = init;

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: body !== undefined ? JSON.stringify(body) : undefined,
    signal,
  });

  if (!res.ok) {
    let detail = `Request failed (${res.status})`;

    try {
      const data = await res.json();

      if (typeof data.detail === "string") {
        detail = data.detail;
      } else if (Array.isArray(data.detail) && data.detail[0]?.msg) {
        detail = data.detail[0].msg;
      } else if (typeof data.error === "string") {
        detail = data.error;
      }
    } catch {}

    throw new Error(detail);
  }

  return res.json();
}

export function verifyResponse(
  response: string,
  topK = 5,
  signal?: AbortSignal,
): Promise<VerificationResponse> {
  return request<VerificationResponse>("/api/verify-response", {
    method: "POST",
    body: {
      response,
      top_k: topK,
    },
    signal,
  });
}

export function checkUrlHealth(
  url: string,
  options: UrlHealthOptions = {},
  signal?: AbortSignal,
): Promise<UrlHealthResult & { status: string }> {
  return request("/api/url-health", {
    method: "POST",
    body: {
      url,
      ...options,
    },
    signal,
  });
}

export function checkUrlsHealth(
  input: { urls: string[] } | { text: string },
  options: UrlHealthOptions = {},
  signal?: AbortSignal,
): Promise<UrlHealthBatchResponse> {
  return request<UrlHealthBatchResponse>("/api/url-health/batch", {
    method: "POST",
    body: {
      ...input,
      ...options,
    },
    signal,
  });
}

export function getUrlHealthProviders(signal?: AbortSignal): Promise<{
  status: string;
  providers: UrlHealthProvider[];
}> {
  return request("/api/url-health/providers", {
    signal,
  });
}

export interface FullAnalysis {
  verification: VerificationResponse;
  urlHealth: UrlHealthBatchResponse | null;
}

export async function analyzeResponse(
  response: string,
  topK = 5,
  urlOptions: UrlHealthOptions = {},
  signal?: AbortSignal,
): Promise<FullAnalysis> {
  const [verificationResult, urlHealthResult] = await Promise.allSettled([
    verifyResponse(response, topK, signal),
    checkUrlsHealth({ text: response }, urlOptions, signal),
  ]);

  if (verificationResult.status === "rejected") {
    throw verificationResult.reason;
  }

  return {
    verification: verificationResult.value,
    urlHealth:
      urlHealthResult.status === "fulfilled" && urlHealthResult.value.total > 0
        ? urlHealthResult.value
        : null,
  };
}
