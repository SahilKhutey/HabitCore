import React from "react";

interface ChartCardProps {
  title: string;
  children: React.ReactNode;
}

export default function ChartCard({ title, children }: ChartCardProps) {
  return (
    <div style={{
      background: "#ffffff",
      padding: "24px",
      borderRadius: "12px",
      border: "1px solid #e5e7eb",
      boxShadow: "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)",
      marginTop: 24
    }}>
      <h3 style={{ margin: "0 0 24px 0", fontSize: "18px", fontWeight: "600", color: "#111827" }}>{title}</h3>
      {children}
    </div>
  );
}
