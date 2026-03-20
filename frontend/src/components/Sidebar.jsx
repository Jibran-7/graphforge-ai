function Sidebar({ currentPage, onNavigate }) {
  const items = [
    { key: "dashboard", label: "Dashboard" },
    { key: "documents", label: "Documents" },
    { key: "graph", label: "Graph Explorer" },
    { key: "query", label: "Query Workbench" },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <h1>GraphForge</h1>
        <p>Intelligence Platform</p>
      </div>
      <nav className="sidebar-nav" aria-label="Primary Navigation">
        {items.map((item) => (
          <button
            key={item.key}
            type="button"
            className={`nav-link ${currentPage === item.key ? "active" : ""}`}
            onClick={() => onNavigate(item.key)}
          >
            {item.label}
          </button>
        ))}
      </nav>
    </aside>
  );
}

export default Sidebar;
