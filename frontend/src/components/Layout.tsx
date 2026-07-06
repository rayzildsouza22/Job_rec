import type { ReactNode } from "react";
import NavBar from "./NavBar";

function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="app-shell">
      <NavBar />
      <main className="page">{children}</main>
    </div>
  );
}

export default Layout;
