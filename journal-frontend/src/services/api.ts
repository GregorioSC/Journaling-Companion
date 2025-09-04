import axios from "axios"

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000"
export const AUTH_BASE = import.meta.env.VITE_AUTH_BASE || "/auth"
export const USERS_BASE = import.meta.env.VITE_USERS_BASE || "/users"
export const ENTRIES_BASE = import.meta.env.VITE_ENTRIES_BASE || "/entries"
export const INSIGHTS_BASE = import.meta.env.VITE_INSIGHTS_BASE || "/insights"

export const api = axios.create({
  baseURL: API_BASE,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token")
  if (token) {
    config.headers = config.headers || {}
    config.headers["Authorization"] = `Bearer ${token}`
  }
  return config
})

export type Entry = { id: number, user_id: number, title: string, text: string, created_at: string }
export type User = {
  id: number, username: string, email: string, age: number, gender: string,
  last_entry_date?: string | null, current_streak?: number, longest_streak?: number
}
export type Insight = { id: number, entry_id: number, sentiment: number, themes: string[], embedding: number[], created_at: string }

export async function login(email: string, password: string) {
  const { data } = await api.post(`${AUTH_BASE}/login`, { email, password })
  localStorage.setItem("token", data.access_token)
  return data
}

export async function registerUser(payload: { username: string, email: string, password: string, age: number, gender: string }) {
  const { data } = await api.post(`${AUTH_BASE}/register`, payload)
  return data
}

export async function getMe(): Promise<User> {
  const { data } = await api.get(`${USERS_BASE}/me`)
  return data
}


export async function updateMe(body: Partial<{ username: string; age: number | null; gender: string | null }>): Promise<User> {
  const { data } = await api.patch(`${USERS_BASE}/me`, body, {
    headers: { "Content-Type": "application/json" },
  })
  return data
}

export async function getMyEntries(): Promise<Entry[]> {
  const { data } = await api.get(`${ENTRIES_BASE}`)
  return data
}

export async function createEntry(payload: { user_id: number, title: string, text: string }): Promise<Entry> {
  const { data } = await api.post(`${ENTRIES_BASE}`, payload)
  return data
}

export async function patchEntry(id: number, patch: Partial<Pick<Entry, "title" | "text">>): Promise<Entry> {
  const { data } = await api.patch(`${ENTRIES_BASE}/${id}`, patch)
  return data
}

export async function getEntry(id: number): Promise<Entry> {
  const { data } = await api.get(`${ENTRIES_BASE}/${id}`)
  return data
}

export async function deleteEntry(id: number): Promise<{ ok: boolean }> {
  const { data } = await api.delete(`${ENTRIES_BASE}/${id}`)
  return data
}

export async function getInsightByEntry(entryId: number): Promise<Insight> {
  const { data } = await api.get(`${INSIGHTS_BASE}/by-entry/${entryId}`)
  return data
}

export async function patchInsightByEntry(entryId: number, patch: Partial<Pick<Insight, "sentiment" | "themes" | "embedding">>): Promise<Insight> {
  const { data } = await api.patch(`${INSIGHTS_BASE}/by-entry/${entryId}`, patch)
  return data
}

// ---- AI types ----
export type PromptResponse = {
  prompts: string[];
  context_entry_ids: number[];
};

export type AnalyzeEntryResponse = {
  entry_id: number;
  sentiment: number;
  themes: string[];
};

export type WeeklySummary = {
  week_start: string;   // YYYY-MM-DD
  summary: string;
  insights: Record<string, any>;
};

// ---- AI endpoints ----
export async function getAIPrompts(goal = "daily reflection", k_context = 5): Promise<PromptResponse> {
  const { data } = await api.post("/ai/prompt", { goal, k_context });
  return data;
}

export async function analyzeEntryAI(entryId: number): Promise<AnalyzeEntryResponse> {
  const { data } = await api.post(`/ai/entries/${entryId}/analyze`);
  return data;
}

export async function getWeeklySummary(): Promise<WeeklySummary> {
  const { data } = await api.get("/ai/summary/weekly");
  return data;
}
