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
      background: "#ffffff",
      padding: "24px",
      borderRadius: "12px",
      border: "1px solid #e5e7eb",
      boxShadow: "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between"
    }}>
      <div>
        <p style={{ color: "#6b7280", fontSize: "14px", fontWeight: "500", marginBottom: 8, textTransform: "uppercase", letterSpacing: "0.05em" }}>{title}</p>
        <h2 style={{ fontSize: "36px", margin: 0, fontWeight: "700", color: "#111827" }}>{value}</h2>
      </div>
      <div style={{ 
        width: 48, 
        height: 48, 
        borderRadius: "12px", 
        background: "#f3f4f6", 
        display: "flex", 
        alignItems: "center", 
        justifyContent: "center" 
      }}>
        {icon}
      </div>
    </div>
  );
}
