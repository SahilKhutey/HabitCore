import React from 'react';
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Users from "./pages/Users";
import { LayoutDashboard, Users as UsersIcon } from "lucide-react";

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ display: "flex", minHeight: "100vh", background: "#000" }}>
        {/* Sidebar */}
        <div style={{ 
          width: "240px", 
          background: "#080808", 
          borderRight: "1px solid rgba(255,255,255,0.05)",
          padding: "32px 16px"
        }}>
          <h2 style={{ color: "#00ffcc", marginBottom: 40, fontSize: "20px", paddingLeft: 12 }}>HabitHero</h2>
          
          <Link to="/" style={navStyle}>
            <LayoutDashboard size={20} />
            Dashboard
          </Link>
          <Link to="/users" style={navStyle}>
            <UsersIcon size={20} />
            Live Feed
          </Link>
        </div>

        {/* Content */}
        <div style={{ flex: 1 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/users" element={<Users />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

const navStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: "12px",
  color: "rgba(255,255,255,0.6)",
  textDecoration: "none",
  padding: "12px",
  borderRadius: "8px",
  marginBottom: "8px",
  fontSize: "14px",
  fontWeight: "500"
};
