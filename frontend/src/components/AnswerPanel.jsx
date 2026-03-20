function AnswerPanel({ result, error }) {
  return (
    <section className="panel answer-panel">
      <div className="panel-header-row">
        <h3>Query Result</h3>
      </div>
      {error ? <p className="status error">{error}</p> : null}
      {!error && !result ? <p className="status">Submit a graph query to see results.</p> : null}
      {result ? (
        <>
          <div className="answer-box">
            <h4>Answer</h4>
            <p>{result.answer}</p>
          </div>
          <div className="chips-wrap">
            <h4>Matched Entities</h4>
            <div className="chips">
              {result.matched_entities.length > 0 ? (
                result.matched_entities.map((entity) => (
                  <span key={entity} className="chip">
                    {entity}
                  </span>
                ))
              ) : (
                <span className="muted">No matched entities.</span>
              )}
            </div>
          </div>
          <div>
            <h4>Path Steps</h4>
            {result.paths.length === 0 ? (
              <p className="muted">No path steps returned.</p>
            ) : (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Source</th>
                      <th>Relation</th>
                      <th>Target</th>
                      <th>Evidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.paths.map((step, index) => (
                      <tr key={`${step.source_entity}-${step.target_entity}-${index}`}>
                        <td>{step.source_entity}</td>
                        <td>{step.relation_type}</td>
                        <td>{step.target_entity}</td>
                        <td className="evidence-cell">{step.evidence_text || "-"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      ) : null}
    </section>
  );
}

export default AnswerPanel;
