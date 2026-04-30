import React, { useEffect, useState } from "react";
import { getEvents, banUser, grantPremium } from "../services/api";
import { Activity, Clock, ShieldAlert, ShieldCheck } from "lucide-react";

export default function Users() {
  const [events, setEvents] = useState<any[]>([]);

  useEffect(() => {
    // Initial fetch
    getEvents().then(res => setEvents(res.data)).catch(err => console.error(err));

    // WebSocket connection
    const ws = new WebSocket("ws://localhost:8000/ws");
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setEvents(prev => [data, ...prev]);
    };

    return () => ws.close();
  }, []);

  const handleBan = async (id: string) => {
    if (window.confirm("Ban this user?")) {
      await banUser(id);
      alert("User banned");
    }
  };

  const handleGrantPremium = async (id: string) => {
    await grantPremium(id);
    alert("Premium granted 💎");
  };

  return (
    <div style={{ padding: "40px", color: "#fff", background: "#000", minHeight: "100vh" }}>
      <h2 style={{ marginBottom: 32, display: "flex", alignItems: "center", gap: 12 }}>
        <Activity color="#00ffcc" />
        Live Event Feed
      </h2>

      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {events.map((e: any, i: number) => (
          <div key={i} style={{ 
            padding: "16px", 
            background: "#111", 
            borderRadius: "12px",
            border: "1px solid rgba(255,255,255,0.05)",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center"
          }}>
            <div>
              <span style={{ color: "#00ffcc", fontWeight: "600", marginRight: 8 }}>{e.event_type}</span>
              <span style={{ color: "rgba(255,255,255,0.4)", fontSize: "14px" }}>User ID: {e.user_id}</span>
            </div>
            
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
              <div style={{ display: "flex", gap: 8 }}>
                <button onClick={() => handleGrantPremium(e.user_id)} style={controlBtnStyle}>
                  <ShieldCheck size={14} color="#00ffcc" />
                  Premium
                </button>
                <button onClick={() => handleBan(e.user_id)} style={controlBtnStyle}>
                  <ShieldAlert size={14} color="#ef4444" />
                  Ban
                </button>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 6, color: "rgba(255,255,255,0.3)", fontSize: "12px" }}>
                <Clock size={12} />
                {new Date(e.created_at).toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

const controlBtnStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: "4px",
  background: "rgba(255,255,255,0.05)",
  border: "none",
  color: "#fff",
  padding: "6px 10px",
  borderRadius: "6px",
  fontSize: "11px",
  cursor: "pointer"
};
