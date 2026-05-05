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
      padding: "28px",
      borderRadius: "24px",
      border: "1px solid #E5E7EB",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      boxShadow: "0 10px 25px rgba(0, 0, 0, 0.03)",
      position: "relative",
      overflow: "hidden"
    }}>
      <div style={{ position: "relative", zIndex: 1 }}>
        <p style={{ 
          color: "#6B7280", 
          fontSize: "11px", 
          fontWeight: "700", 
          marginBottom: 10, 
          textTransform: "uppercase", 
          letterSpacing: "0.15em" 
        }}>
          {title}
        </p>
        <h2 style={{ 
          fontSize: "36px", 
          margin: 0, 
          fontWeight: "800", 
          color: "#1A1F2E",
          letterSpacing: "-0.02em"
        }}>
          {value}
        </h2>
      </div>
      
      <div style={{ 
        width: 56, 
        height: 56, 
        borderRadius: "18px", 
        background: "#F9FAFB", 
        display: "flex", 
        alignItems: "center", 
        justifyContent: "center",
        border: "1px solid #E5E7EB",
        boxShadow: "0 4px 6px rgba(0, 0, 0, 0.02)",
        position: "relative",
        zIndex: 1
      }}>
        {icon}
      </div>
    </div>
  );
}
