function EntityTable({ entities }) {
  return (
    <section className="panel">
      <div className="panel-header-row">
        <h3>Entities</h3>
        <span className="badge">{entities.length}</span>
      </div>
      {entities.length === 0 ? (
        <p className="status">No entities available for this scope.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Document ID</th>
              </tr>
            </thead>
            <tbody>
              {entities.map((entity) => (
                <tr key={entity.id}>
                  <td>{entity.name}</td>
                  <td>{entity.entity_type}</td>
                  <td>{entity.document_id}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export default EntityTable;
