import React from 'react';

interface ChartCardProps {
  title: string;
  children: React.ReactNode;
}

export default function ChartCard({ title, children }: ChartCardProps) {
  return (
    <div style={{
      background: "#111",
      padding: "24px",
      borderRadius: "16px",
      color: "#fff",
      marginTop: 24,
      border: "1px solid rgba(255,255,255,0.05)"
    }}>
      <h3 style={{ marginTop: 0, marginBottom: 20, color: "rgba(255,255,255,0.8)" }}>{title}</h3>
      {children}
    </div>
  );
}
