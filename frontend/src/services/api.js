const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, options);
  let payload = null;

  try {
    payload = await response.json();
  } catch {
    payload = null;
  }

  if (!response.ok) {
    const message = payload && typeof payload.detail === "string" ? payload.detail : `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  return payload;
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  return request("/documents/upload", {
    method: "POST",
    body: formData,
  });
}

export function listDocuments() {
  return request("/documents");
}

export function getDocument(documentId) {
  return request(`/documents/${documentId}`);
}

export function getGlobalGraph() {
  return request("/graph");
}

export function getGlobalGraphSummary() {
  return request("/graph/summary");
}

export function getDocumentGraph(documentId) {
  return request(`/graph/${documentId}`);
}

export function getDocumentGraphSummary(documentId) {
  return request(`/graph/${documentId}/summary`);
}

export function queryGraph(question, documentId = null) {
  return request("/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
      document_id: documentId,
    }),
  });
}

export { API_BASE_URL };
