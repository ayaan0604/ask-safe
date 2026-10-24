
import { useState } from "react";
import "./App.css";
import Navbar from "./componenets/navbar";
import LoginPage from "./componenets/login-page";
import ChatPage from "./componenets/chatpage";
import AdminPage from "./componenets/AdminPage";

export default function App() {
  const [user, setUser] = useState(null);
  const [view, setView] = useState("chat");

  function handleLogout() {
    sessionStorage.removeItem("access_token");
    setUser(null);
    setView("chat");
  }

  function handleLogin(userData) {
    setUser(userData);
    setView("chat");
  }

  return (
    <div className="app">
      {!user && <Navbar />}

      {!user ? (
        <div className="login-container">
          <LoginPage onLogin={handleLogin} />
        </div>
      ) : view === "admin" ? (
        <AdminPage
          user={user}
          onBackToChat={() => setView("chat")}
          onLogout={handleLogout}
        />
      ) : (
        <ChatPage
          user={user}
          onLogout={handleLogout}
          onOpenAdmin={() => setView("admin")}
        />
      )}
    </div>
  );
}
