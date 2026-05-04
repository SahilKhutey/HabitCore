import React from "react";

interface ChartCardProps {
  title: string;
  children: React.ReactNode;
}

export default function ChartCard({ title, children }: ChartCardProps) {
  return (
    <div style={{
      background: "rgba(255, 255, 255, 0.02)",
      backdropFilter: "blur(20px)",
      padding: "32px",
      borderRadius: "24px",
      border: "1px solid rgba(255, 255, 255, 0.03)",
      marginTop: 24,
      boxShadow: "0 10px 40px 0 rgba(0, 0, 0, 0.2)"
    }}>
      <h3 style={{ margin: "0 0 24px 0", fontSize: "18px", fontWeight: "600", color: "#ffffff", letterSpacing: "0.02em" }}>{title}</h3>
      {children}
    </div>
  );
}
