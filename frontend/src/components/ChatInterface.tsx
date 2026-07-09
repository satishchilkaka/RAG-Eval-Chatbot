import { useEffect, useRef, useState } from "react";
import type { Message } from "../App";
import "./ChatInterface.css";

interface Props {
  messages: Message[];
  onAsk: (question: string) => Promise<void>;
  loading: boolean;
  hasDocuments: boolean;
}

const SUGGESTIONS = [
  "What is this document about?",
  "Summarize the key points.",
  "What are the main topics covered?",
];

export function ChatInterface({ messages, onAsk, loading, hasDocuments }: Props) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const submit = async () => {
    const q = input.trim();
    if (!q || loading || !hasDocuments) return;
    setInput("");
    await onAsk(q);
  };

  return (
    <div className="chat">
      <div className="messages">
        {messages.length === 0 && (
          <div className="welcome">
            <h2>Ask anything about your documents</h2>
            <p>
              Upload a PDF, Word doc, or text file, then ask questions. Answers
              are grounded in your uploaded content using RAG.
            </p>
            {hasDocuments && (
              <div className="suggestions">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    className="suggestion"
                    onClick={() => onAsk(s)}
                    disabled={loading}
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.role}`}>
            <div className="bubble">
              <p>{msg.content}</p>
              {msg.role === "assistant" && msg.sources && msg.sources.length > 0 && (
                <details className="sources">
                  <summary>
                    {msg.sources.length} source chunk
                    {msg.sources.length !== 1 && "s"}
                    {msg.model && ` · ${msg.model.split("/").pop()}`}
                  </summary>
                  <ul>
                    {msg.sources.map((s, i) => (
                      <li key={i}>
                        <strong>{s.filename}</strong> (score: {s.score})
                        <p>{s.text}</p>
                      </li>
                    ))}
                  </ul>
                </details>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="message assistant">
            <div className="bubble typing">
              <span />
              <span />
              <span />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form
        className="input-bar"
        onSubmit={(e) => {
          e.preventDefault();
          submit();
        }}
      >
        <input
          type="text"
          placeholder={
            hasDocuments
              ? "Ask a question about your documents…"
              : "Upload a document first…"
          }
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading || !hasDocuments}
        />
        <button type="submit" disabled={loading || !hasDocuments || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
