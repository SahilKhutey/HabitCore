import React, { useEffect, useState } from "react";
import { AnalyticsAdapter } from "../services/AnalyticsAdapter";
import StatCard from "../components/StatCard";
import ChartCard from "../components/ChartCard";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { Users, TrendingUp, DollarSign } from "lucide-react";

export default function Dashboard() {
  const [dau, setDau] = useState(0);
  const [growth, setGrowth] = useState([]);
  const [retention, setRetention] = useState([]);

  useEffect(() => {
    AnalyticsAdapter.getDAU().then(setDau);
    AnalyticsAdapter.getUserGrowth().then(setGrowth);
    AnalyticsAdapter.getRetention().then(setRetention);
  }, []);

  return (
    <div style={{ padding: "40px", background: "#f9fafb", minHeight: "100vh", color: "#111827" }}>
      <h1 style={{ marginBottom: 32, fontWeight: "700", fontSize: "32px", color: "#111827" }}>HabitHero Intelligence</h1>
      
      {/* TOP STATS */}
      <div style={{ display: "flex", gap: 24 }}>
        <StatCard title="Daily Active Users" value={dau} icon={<Users size={20} color="#3b82f6" />} />
        <StatCard title="Growth (7d)" value="+12%" icon={<TrendingUp size={20} color="#10b981" />} />
        <StatCard title="Revenue (MTD)" value="₹0" icon={<DollarSign size={20} color="#f59e0b" />} />
      </div>

      {/* GROWTH CHART */}
      <ChartCard title="User Acquisition (Last 7 Days)">
        <div style={{ width: "100%", height: 300 }}>
          <ResponsiveContainer>
            <LineChart data={growth}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" vertical={false} />
              <XAxis dataKey="date" stroke="#6b7280" tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis stroke="#6b7280" tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
              <Tooltip 
                contentStyle={{ backgroundColor: "#ffffff", border: "1px solid #e5e7eb", borderRadius: 8, boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)" }}
                itemStyle={{ color: "#3b82f6" }}
              />
              <Line type="monotone" dataKey="users" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4, fill: "#3b82f6" }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </ChartCard>

      <ChartCard title="Retention Cohorts">
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: 10 }}>
          <thead>
            <tr style={{ textAlign: "left", color: "#6b7280", fontSize: "12px", borderBottom: "1px solid #e5e7eb" }}>
              <th style={{ padding: 12 }}>Signup Date</th>
              <th style={{ padding: 12 }}>D0 (Acquisition)</th>
              <th style={{ padding: 12 }}>Day 1</th>
              <th style={{ padding: 12 }}>Day 7</th>
            </tr>
          </thead>
          <tbody>
            {retention.map((row: any, i: number) => (
              <tr key={i} style={{ borderBottom: "1px solid #f3f4f6" }}>
                <td style={{ padding: 12, fontWeight: 500 }}>{row.signup_date}</td>
                <td style={{ padding: 12, color: "#3b82f6", fontWeight: 600 }}>{row.d0} users</td>
                <td style={{ padding: 12, background: row.d1 > 0 ? "#eff6ff" : "transparent" }}>
                  {row.d1} ({((row.d1/row.d0)*100 || 0).toFixed(1)}%)
                </td>
                <td style={{ padding: 12, background: row.d7 > 0 ? "#ecfdf5" : "transparent" }}>
                  {row.d7} ({((row.d7/row.d0)*100 || 0).toFixed(1)}%)
                </td>
              </tr>
            ))}
            {retention.length === 0 && (
              <tr><td colSpan={4} style={{ padding: 12, textAlign: "center", color: "#9ca3af" }}>No cohort data available.</td></tr>
            )}
          </tbody>
        </table>
      </ChartCard>
    </div>
  );
}
