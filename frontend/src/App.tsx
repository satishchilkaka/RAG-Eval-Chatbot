import { useCallback, useEffect, useState } from "react";
import {
  askQuestion,
  deleteDocument,
  fetchDocuments,
  fetchHealth,
  uploadDocument,
  type ChatResponse,
  type DocumentInfo,
  type HealthResponse,
} from "./api/client";
import { ChatInterface } from "./components/ChatInterface";
import { DocumentList } from "./components/DocumentList";
import { DocumentUpload } from "./components/DocumentUpload";
import "./App.css";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: ChatResponse["sources"];
  model?: string;
}

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const [healthData, docs] = await Promise.all([
        fetchHealth(),
        fetchDocuments(),
      ]);
      setHealth(healthData);
      setDocuments(docs);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to connect to API");
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleUpload = async (file: File) => {
    setUploading(true);
    setError(null);
    try {
      await uploadDocument(file);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    setError(null);
    try {
      await deleteDocument(id);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed");
    }
  };

  const handleAsk = async (question: string) => {
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: question,
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);
    setError(null);

    try {
      const response = await askQuestion(question);
      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.answer,
        sources: response.sources,
        model: response.model,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Chat failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>RAG Eval Chatbot</h1>
          <p className="subtitle">
            Upload documents and ask questions grounded in your files
          </p>
        </div>
        {health && (
          <div className="status-badge">
            <span className="dot" />
            {health.documents_indexed} doc{health.documents_indexed !== 1 && "s"}{" "}
            · {health.model.split("/").pop()}
          </div>
        )}
      </header>

      {error && (
        <div className="error-banner" role="alert">
          {error}
        </div>
      )}

      <main className="layout">
        <aside className="sidebar">
          <DocumentUpload onUpload={handleUpload} uploading={uploading} />
          <DocumentList documents={documents} onDelete={handleDelete} />
        </aside>

        <section className="chat-panel">
          <ChatInterface
            messages={messages}
            onAsk={handleAsk}
            loading={loading}
            hasDocuments={documents.length > 0}
          />
        </section>
      </main>
    </div>
  );
}

export default App;
