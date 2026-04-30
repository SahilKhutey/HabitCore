import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
}

export default function StatCard({ title, value, icon }: StatCardProps) {
  return (
    <div style={{
      background: "#111",
      padding: "24px",
      borderRadius: "16px",
      color: "#fff",
      flex: 1,
      border: "1px solid rgba(255,255,255,0.05)",
      display: "flex",
      flexDirection: "column",
      gap: 8
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h4 style={{ margin: 0, color: "rgba(255,255,255,0.5)", fontWeight: 500 }}>{title}</h4>
        {icon}
      </div>
      <h2 style={{ margin: 0, fontSize: "32px", fontWeight: "700", color: "#00ffcc" }}>{value}</h2>
    </div>
  );
}
