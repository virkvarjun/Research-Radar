import { supabase } from "./supabase";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getAuthHeaders(): Promise<Record<string, string>> {
  const {
    data: { session },
  } = await supabase.auth.getSession();
  if (!session?.access_token) return {};
  return { Authorization: `Bearer ${session.access_token}` };
}

async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const headers = {
    "Content-Type": "application/json",
    ...(await getAuthHeaders()),
    ...(options.headers as Record<string, string>),
  };
  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json();
}

// --- Onboarding ---
export function submitOnboarding(data: {
  role: string;
  topics: string[];
  anchor_labels: Record<string, string>;
  pairwise_choices: { winner_id: string; loser_id: string }[];
}) {
  return apiFetch("/onboarding/answers", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function getAnchorPapers() {
  return apiFetch<Paper[]>("/onboarding/anchor-papers");
}

export function getPairwisePapers() {
  return apiFetch<{ paper_a: Paper; paper_b: Paper }[]>(
    "/onboarding/pairwise-papers"
  );
}

// --- Feed ---
export function getFeed(refresh = false) {
  return apiFetch<{ papers: Paper[]; has_more: boolean }>(
    `/feed?refresh=${refresh}`
  );
}

// --- Feedback ---
export function sendFeedback(paperId: string, action: string) {
  return apiFetch("/feedback", {
    method: "POST",
    body: JSON.stringify({ paper_id: paperId, action, source: "web" }),
  });
}

// --- University ---
export function searchInstitutions(query: string) {
  return apiFetch<{ institutions: Institution[] }>(
    `/university/search?q=${encodeURIComponent(query)}`
  );
}

export function getInstitutionPapers(institutionId: string) {
  return apiFetch<Paper[]>(`/university/${institutionId}/new`);
}

export function getRelatedPapers(institutionId: string) {
  return apiFetch<Paper[]>(`/university/${institutionId}/related`);
}

// --- Papers ---
export function getPaper(paperId: string) {
  return apiFetch<PaperDetail>(`/papers/${paperId}`);
}

export function savePaper(paperId: string) {
  return apiFetch(`/papers/${paperId}/save`, { method: "POST" });
}

export function chatWithPaper(paperId: string, question: string) {
  return apiFetch<ChatResponse>(`/papers/${paperId}/chat`, {
    method: "POST",
    body: JSON.stringify({ question }),
  });
}

// --- Saved ---
export function getSavedPapers() {
  return apiFetch<SavedPaper[]>("/saved");
}

// --- Settings ---
export function getSettings() {
  return apiFetch<UserSettings>("/settings");
}

export function updateSettings(data: Partial<UserSettings>) {
  return apiFetch("/settings", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// --- Types ---
export interface Paper {
  id: string;
  title: string;
  abstract?: string;
  authors?: { name: string }[];
  doi?: string;
  arxiv_id?: string;
  source: string;
  pdf_url?: string;
  published_date?: string;
  categories?: string[];
  evidence?: Record<string, unknown>;
  why_matched?: Record<string, unknown>;
}

export interface PaperDetail extends Paper {
  rigour_panel?: Record<
    string,
    { status: string; indicator: string; items?: unknown[]; count?: number; url?: string }
  >;
  chunks_available: boolean;
}

export interface ChatResponse {
  answer: string;
  citations: { chunk_index: number; text: string; score: number }[];
}

export interface Institution {
  id: string;
  openalex_id: string;
  name: string;
  country?: string;
}

export interface SavedPaper {
  id: string;
  paper: Paper;
  saved_at: string;
}

export interface UserSettings {
  role: string;
  topics?: string[];
  digest_enabled: boolean;
  institutions: Institution[];
  institution_ids?: string[];
}
