import { useEffect, useState } from "react";

import { getGlobalGraphSummary, listDocuments } from "../services/api";

function Dashboard({ onNavigate }) {
  const [docCount, setDocCount] = useState(0);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function loadDashboard() {
      try {
        const [documents, graphSummary] = await Promise.all([listDocuments(), getGlobalGraphSummary()]);
        if (!active) {
          return;
        }
        setDocCount(documents.length);
        setSummary(graphSummary);
      } catch (loadError) {
        if (!active) {
          return;
        }
        setError(loadError.message || "Failed to load dashboard.");
      }
    }

    loadDashboard();
    return () => {
      active = false;
    };
  }, []);

  return (
    <div className="page">
      <section className="panel hero-panel">
        <h3>GraphForge Intelligence Platform</h3>
        <p>
          Convert local documents into an entity-relationship graph for grounded exploration and deterministic
          graph-based question answering.
        </p>
        <div className="action-row">
          <button type="button" className="button" onClick={() => onNavigate("documents")}>
            Upload Documents
          </button>
          <button type="button" className="button secondary" onClick={() => onNavigate("graph")}>
            Explore Graph
          </button>
          <button type="button" className="button secondary" onClick={() => onNavigate("query")}>
            Query Relationships
          </button>
        </div>
      </section>

      {error ? <p className="status error">{error}</p> : null}

      <section className="stats-grid">
        <article className="stat-card">
          <h4>Documents</h4>
          <p>{docCount}</p>
        </article>
        <article className="stat-card">
          <h4>Entities</h4>
          <p>{summary?.entity_count ?? "-"}</p>
        </article>
        <article className="stat-card">
          <h4>Relationships</h4>
          <p>{summary?.relationship_count ?? "-"}</p>
        </article>
      </section>
    </div>
  );
}

export default Dashboard;
