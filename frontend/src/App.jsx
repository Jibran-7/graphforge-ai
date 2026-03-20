import { useMemo, useState } from "react";

import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Documents from "./pages/Documents";
import GraphExplorer from "./pages/GraphExplorer";
import QueryWorkbench from "./pages/QueryWorkbench";

function App() {
  const [currentPage, setCurrentPage] = useState("dashboard");

  const pageTitle = useMemo(() => {
    const titles = {
      dashboard: "Dashboard",
      documents: "Documents",
      graph: "Graph Explorer",
      query: "Query Workbench",
    };
    return titles[currentPage] || "Dashboard";
  }, [currentPage]);

  const renderPage = () => {
    if (currentPage === "documents") {
      return <Documents />;
    }
    if (currentPage === "graph") {
      return <GraphExplorer />;
    }
    if (currentPage === "query") {
      return <QueryWorkbench />;
    }
    return <Dashboard onNavigate={setCurrentPage} />;
  };

  return (
    <Layout currentPage={currentPage} pageTitle={pageTitle} onNavigate={setCurrentPage}>
      {renderPage()}
    </Layout>
  );
}

export default App;
