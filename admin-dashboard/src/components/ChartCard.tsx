import React from "react";

interface ChartCardProps {
  title: string;
  children: React.ReactNode;
}

export default function ChartCard({ title, children }: ChartCardProps) {
  return (
    <div style={{
      background: "#ffffff",
      padding: "36px",
      borderRadius: "32px",
      border: "1px solid #E5E7EB",
      boxShadow: "0 10px 25px rgba(0, 0, 0, 0.02)",
      position: "relative",
      overflow: "hidden"
    }}>
      <h3 style={{ 
        margin: "0 0 32px 0", 
        fontSize: "16px", 
        fontWeight: "700", 
        color: "#1A1F2E", 
        letterSpacing: "0.05em",
        textTransform: "uppercase"
      }}>
        {title}
      </h3>
      {children}
    </div>
  );
}
