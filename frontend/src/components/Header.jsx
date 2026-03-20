function Header({ pageTitle }) {
  return (
    <header className="header">
      <div>
        <h2>{pageTitle}</h2>
        <p>Local-first graph intelligence workspace</p>
      </div>
    </header>
  );
}

export default Header;
