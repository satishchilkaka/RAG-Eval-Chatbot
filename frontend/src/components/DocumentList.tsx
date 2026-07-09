import type { DocumentInfo } from "../api/client";
import "./DocumentList.css";

interface Props {
  documents: DocumentInfo[];
  onDelete: (id: string) => void;
}

export function DocumentList({ documents, onDelete }: Props) {
  if (documents.length === 0) {
    return (
      <div className="doc-list empty">
        <p>No documents yet. Upload one to get started.</p>
      </div>
    );
  }

  return (
    <ul className="doc-list">
      {documents.map((doc) => (
        <li key={doc.id} className="doc-item">
          <div className="doc-info">
            <span className="doc-name" title={doc.filename}>
              {doc.filename}
            </span>
            <span className="doc-meta">{doc.chunk_count} chunks</span>
          </div>
          <button
            className="delete-btn"
            onClick={() => onDelete(doc.id)}
            aria-label={`Delete ${doc.filename}`}
          >
            ×
          </button>
        </li>
      ))}
    </ul>
  );
}
