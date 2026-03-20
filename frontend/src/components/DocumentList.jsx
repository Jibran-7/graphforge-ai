function formatTimestamp(value) {
  if (!value) {
    return "-";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}

function DocumentList({ documents, isLoading, error, onSelect, selectedDocumentId }) {
  return (
    <section className="panel">
      <div className="panel-header-row">
        <h3>Documents</h3>
        <span className="badge">{documents.length}</span>
      </div>
      {isLoading ? <p className="status">Loading documents...</p> : null}
      {error ? <p className="status error">{error}</p> : null}
      {!isLoading && !error && documents.length === 0 ? <p className="status">No documents uploaded yet.</p> : null}
      {documents.length > 0 ? (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Filename</th>
                <th>Content Type</th>
                <th>Uploaded At</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((doc) => (
                <tr
                  key={doc.id}
                  className={selectedDocumentId === doc.id ? "row-selected" : ""}
                  onClick={() => onSelect && onSelect(doc.id)}
                >
                  <td>{doc.filename}</td>
                  <td>{doc.content_type}</td>
                  <td>{formatTimestamp(doc.uploaded_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </section>
  );
}

export default DocumentList;
