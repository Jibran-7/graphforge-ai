function RelationshipTable({ relationships, entityNameById = {} }) {
  const resolveEntity = (entityId) => entityNameById[entityId] || `Entity #${entityId}`;

  return (
    <section className="panel">
      <div className="panel-header-row">
        <h3>Relationships</h3>
        <span className="badge">{relationships.length}</span>
      </div>
      {relationships.length === 0 ? (
        <p className="status">No relationships available for this scope.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Source Entity</th>
                <th>Canonical Relation Type</th>
                <th>Target Entity</th>
                <th>Evidence</th>
              </tr>
            </thead>
            <tbody>
              {relationships.map((relationship) => (
                <tr key={relationship.id}>
                  <td>{resolveEntity(relationship.source_entity_id)}</td>
                  <td>
                    <span className="relation-type-badge">{relationship.relation_type}</span>
                  </td>
                  <td>{resolveEntity(relationship.target_entity_id)}</td>
                  <td className="evidence-cell">{relationship.evidence_text || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

export default RelationshipTable;
