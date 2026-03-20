import Header from "./Header";
import Sidebar from "./Sidebar";

function Layout({ currentPage, pageTitle, onNavigate, children }) {
  return (
    <div className="layout">
      <Sidebar currentPage={currentPage} onNavigate={onNavigate} />
      <div className="layout-main">
        <Header pageTitle={pageTitle} />
        <main className="content">{children}</main>
      </div>
    </div>
  );
}

export default Layout;
