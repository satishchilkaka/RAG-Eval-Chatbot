import { useRef, useState } from "react";
import "./DocumentUpload.css";

interface Props {
  onUpload: (file: File) => Promise<void>;
  uploading: boolean;
}

const ACCEPTED = ".pdf,.txt,.md,.docx,.csv";

export function DocumentUpload({ onUpload, uploading }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFile = async (file: File | undefined) => {
    if (!file || uploading) return;
    await onUpload(file);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <div className="upload-section">
      <h2>Documents</h2>
      <div
        className={`dropzone ${dragOver ? "drag-over" : ""} ${uploading ? "disabled" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          handleFile(e.dataTransfer.files[0]);
        }}
        onClick={() => !uploading && inputRef.current?.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED}
          hidden
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
        {uploading ? (
          <p className="dropzone-text">Indexing document…</p>
        ) : (
          <>
            <p className="dropzone-icon">📄</p>
            <p className="dropzone-text">
              Drop a file or <span className="link">browse</span>
            </p>
            <p className="dropzone-hint">PDF, TXT, MD, DOCX, CSV</p>
          </>
        )}
      </div>
    </div>
  );
}
