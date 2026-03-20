import { useState } from "react";

function QueryPanel({ documents, onSubmit, isSubmitting }) {
  const [question, setQuestion] = useState("");
  const [documentId, setDocumentId] = useState("");

  const submitQuery = (event) => {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed) {
      return;
    }
    const selected = documentId ? Number(documentId) : null;
    onSubmit(trimmed, selected);
  };

  return (
    <section className="panel">
      <div className="panel-header-row">
        <h3>Ask The Graph</h3>
      </div>
      <form className="form-grid" onSubmit={submitQuery}>
        <label className="field">
          <span>Question</span>
          <textarea
            rows={3}
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="How is OpenAI connected to Microsoft?"
          />
        </label>
        <label className="field">
          <span>Scope (optional)</span>
          <select value={documentId} onChange={(event) => setDocumentId(event.target.value)}>
            <option value="">Global Graph</option>
            {documents.map((doc) => (
              <option key={doc.id} value={doc.id}>
                {doc.filename}
              </option>
            ))}
          </select>
        </label>
        <button type="submit" className="button" disabled={isSubmitting}>
          {isSubmitting ? "Running Query..." : "Run Query"}
        </button>
      </form>
      <div className="example-row">
        <span className="muted">Examples:</span>
        <code>Who works with Microsoft?</code>
        <code>How is OpenAI connected to Microsoft?</code>
      </div>
    </section>
  );
}

export default QueryPanel;
