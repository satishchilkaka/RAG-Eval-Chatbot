export interface DocumentInfo {
  id: string;
  filename: string;
  chunk_count: number;
  status: string;
}

export interface SourceChunk {
  document_id: string;
  filename: string;
  text: string;
  score: number;
}

export interface ChatResponse {
  answer: string;
  sources: SourceChunk[];
  model: string;
}

export interface HealthResponse {
  status: string;
  documents_indexed: number;
  model: string;
}

// In local dev / Docker Compose, the frontend and backend share an origin
// (via the Vite proxy or nginx), so a relative "/api" works. When deployed
// as separate services (e.g. Render static site + web service), set
// VITE_API_URL at build time to the backend's full URL.
const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api`
  : "/api";

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || "Request failed");
  }
  return response.json();
}

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`);
  return handleResponse<HealthResponse>(res);
}

export async function fetchDocuments(): Promise<DocumentInfo[]> {
  const res = await fetch(`${API_BASE}/documents`);
  return handleResponse<DocumentInfo[]>(res);
}

export async function uploadDocument(file: File): Promise<DocumentInfo> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: "POST",
    body: formData,
  });
  const data = await handleResponse<{ document: DocumentInfo }>(res);
  return data.document;
}

export async function deleteDocument(documentId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/documents/${documentId}`, {
    method: "DELETE",
  });
  await handleResponse(res);
}

export async function askQuestion(
  question: string,
  documentIds?: string[]
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, document_ids: documentIds }),
  });
  return handleResponse<ChatResponse>(res);
}
