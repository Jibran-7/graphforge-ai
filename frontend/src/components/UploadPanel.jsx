import { useState } from "react";

import { uploadDocument } from "../services/api";

function UploadPanel({ onUploaded }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedFile) {
      setError("Please choose a file to upload.");
      return;
    }

    setIsUploading(true);
    setError("");

    try {
      if (!Number.isFinite(selectedFile.size) || selectedFile.size <= 0) {
        throw new Error("Selected file is empty (0 bytes).");
      }

      const result = await uploadDocument(selectedFile);
      setSelectedFile(null);
      event.target.reset();
      if (onUploaded) {
        onUploaded(result);
      }
    } catch (uploadError) {
      setError(uploadError.message || "Upload failed.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <section className="panel">
      <div className="panel-header-row">
        <h3>Upload Document</h3>
        <span className="badge">TXT / MD</span>
      </div>
      <form className="form-grid" onSubmit={handleSubmit}>
        <input
          type="file"
          accept=".txt,.md,text/plain,text/markdown"
          onChange={(event) => {
            const file = event.target.files?.[0] || null;
            setSelectedFile(file);
          }}
        />
        <button type="submit" className="button" disabled={isUploading}>
          {isUploading ? "Uploading..." : "Upload"}
        </button>
      </form>
      {error ? <p className="status error">{error}</p> : null}
    </section>
  );
}

export default UploadPanel;
