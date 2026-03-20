import { useEffect, useState } from "react";

import DocumentList from "../components/DocumentList";
import UploadPanel from "../components/UploadPanel";
import { listDocuments } from "../services/api";

function Documents() {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const loadDocuments = async () => {
    setIsLoading(true);
    setError("");

    try {
      const data = await listDocuments();
      setDocuments(data);
    } catch (loadError) {
      setError(loadError.message || "Failed to load documents.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  return (
    <div className="page">
      <UploadPanel onUploaded={loadDocuments} />
      <DocumentList documents={documents} isLoading={isLoading} error={error} />
    </div>
  );
}

export default Documents;
