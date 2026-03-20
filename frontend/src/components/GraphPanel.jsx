function GraphPanel({ summary, graph }) {
  const nodes = graph?.entities || [];
  const edges = graph?.relationships || [];

  return (
    <section className="panel graph-panel">
      <div className="panel-header-row">
        <h3>Graph Snapshot</h3>
        <span className="badge">Scope: {summary?.document_id ?? 0}</span>
      </div>
      <div className="stats-grid compact">
        <div className="stat-card">
          <h4>Entities</h4>
          <p>{summary?.entity_count ?? nodes.length}</p>
        </div>
        <div className="stat-card">
          <h4>Relationships</h4>
          <p>{summary?.relationship_count ?? edges.length}</p>
        </div>
        <div className="stat-card">
          <h4>Top Entities</h4>
          <p>{summary?.top_entity_names?.slice(0, 3).join(", ") || "-"}</p>
        </div>
      </div>
      <div className="node-edge-layout">
        <div>
          <h4>Nodes</h4>
          <ul className="list-inline">
            {nodes.slice(0, 20).map((node) => (
              <li key={node.id}>
                <span className="node-name">{node.name}</span>
                <span className="muted">({node.entity_type})</span>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <h4>Edges</h4>
          <ul className="list-inline">
            {edges.slice(0, 20).map((edge) => (
              <li key={edge.id}>
                <span>{edge.source_entity_id}</span>
                <span className="relation-pill">{edge.relation_type}</span>
                <span>{edge.target_entity_id}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}

export default GraphPanel;
