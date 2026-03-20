import { useEffect, useState } from "react";

import AnswerPanel from "../components/AnswerPanel";
import QueryPanel from "../components/QueryPanel";
import { listDocuments, queryGraph } from "../services/api";

function QueryWorkbench() {
  const [documents, setDocuments] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    let active = true;

    async function loadDocuments() {
      try {
        const docs = await listDocuments();
        if (active) {
          setDocuments(docs);
        }
      } catch {
        if (active) {
          setDocuments([]);
        }
      }
    }

    loadDocuments();
    return () => {
      active = false;
    };
  }, []);

  const handleSubmit = async (question, documentId) => {
    setIsSubmitting(true);
    setError("");

    try {
      const response = await queryGraph(question, documentId);
      setResult(response);
    } catch (queryError) {
      setResult(null);
      setError(queryError.message || "Query failed.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="page">
      <QueryPanel documents={documents} onSubmit={handleSubmit} isSubmitting={isSubmitting} />
      <AnswerPanel result={result} error={error} />
    </div>
  );
}

export default QueryWorkbench;
