import { useEffect, useState } from "react";

import EntityTable from "../components/EntityTable";
import GraphPanel from "../components/GraphPanel";
import RelationshipTable from "../components/RelationshipTable";
import {
  getDocumentGraph,
  getDocumentGraphSummary,
  getGlobalGraph,
  getGlobalGraphSummary,
  listDocuments,
} from "../services/api";

function GraphExplorer() {
  const [documents, setDocuments] = useState([]);
  const [selectedDocumentId, setSelectedDocumentId] = useState("");
  const [graph, setGraph] = useState({ entities: [], relationships: [] });
  const [summary, setSummary] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const loadGraphData = async (docId = "") => {
    setIsLoading(true);
    setError("");

    try {
      if (docId) {
        const [graphData, summaryData] = await Promise.all([
          getDocumentGraph(Number(docId)),
          getDocumentGraphSummary(Number(docId)),
        ]);
        setGraph(graphData);
        setSummary(summaryData);
      } else {
        const [graphData, summaryData] = await Promise.all([getGlobalGraph(), getGlobalGraphSummary()]);
        setGraph(graphData);
        setSummary(summaryData);
      }
    } catch (loadError) {
      setError(loadError.message || "Failed to load graph data.");
      setGraph({ entities: [], relationships: [] });
      setSummary(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    let active = true;

    async function bootstrap() {
      try {
        const docs = await listDocuments();
        if (!active) {
          return;
        }
        setDocuments(docs);
      } catch {
        if (!active) {
          return;
        }
        setDocuments([]);
      }
      await loadGraphData("");
    }

    bootstrap();
    return () => {
      active = false;
    };
  }, []);

  const handleScopeChange = async (event) => {
    const nextValue = event.target.value;
    setSelectedDocumentId(nextValue);
    await loadGraphData(nextValue);
  };

  const entityNameById = (graph.entities || []).reduce((acc, entity) => {
    acc[entity.id] = entity.name;
    return acc;
  }, {});

  const relationDistribution = (graph.relationships || []).reduce((acc, relationship) => {
    const key = relationship.relation_type || "UNKNOWN";
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});

  return (
    <div className="page">
      <section className="panel">
        <div className="panel-header-row">
          <h3>Graph Scope</h3>
        </div>
        <label className="field">
          <span>Select Document Scope</span>
          <select value={selectedDocumentId} onChange={handleScopeChange}>
            <option value="">Global Graph</option>
            {documents.map((doc) => (
              <option key={doc.id} value={doc.id}>
                {doc.filename}
              </option>
            ))}
          </select>
        </label>
        {isLoading ? <p className="status">Loading graph...</p> : null}
        {error ? <p className="status error">{error}</p> : null}
      </section>

      <section className="panel">
        <div className="panel-header-row">
          <h3>Relationship Distribution</h3>
        </div>
        {Object.keys(relationDistribution).length === 0 ? (
          <p className="status">No relationship types available for this scope.</p>
        ) : (
          <div className="chips">
            {Object.entries(relationDistribution).map(([relationType, count]) => (
              <span key={relationType} className="chip relation-chip">
                {relationType}: {count}
              </span>
            ))}
          </div>
        )}
      </section>

      <GraphPanel summary={summary} graph={graph} />
      <EntityTable entities={graph.entities || []} />
      <RelationshipTable relationships={graph.relationships || []} entityNameById={entityNameById} />
    </div>
  );
}

export default GraphExplorer;
