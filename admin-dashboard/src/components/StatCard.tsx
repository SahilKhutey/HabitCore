import React from "react";

interface StatCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
}

export default function StatCard({ title, value, icon }: StatCardProps) {
  return (
    <div style={{
      flex: 1,
      background: "rgba(255, 255, 255, 0.03)",
      backdropFilter: "blur(10px)",
      padding: "24px",
      borderRadius: "20px",
      border: "1px solid rgba(255, 255, 255, 0.05)",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      boxShadow: "0 8px 32px 0 rgba(0, 0, 0, 0.37)"
    }}>
      <div>
        <p style={{ color: "#9ca3af", fontSize: "12px", fontWeight: "600", marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.1em" }}>{title}</p>
        <h2 style={{ fontSize: "32px", margin: 0, fontWeight: "700", color: "#ffffff" }}>{value}</h2>
      </div>
      <div style={{ 
        width: 48, 
        height: 48, 
        borderRadius: "16px", 
        background: "rgba(124, 140, 255, 0.1)", 
        display: "flex", 
        alignItems: "center", 
        justifyContent: "center",
        border: "1px solid rgba(124, 140, 255, 0.2)"
      }}>
        {icon}
      </div>
    </div>
  );
}
