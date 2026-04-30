import React, { useEffect, useState } from "react";
import { getDAU, getUserGrowth } from "../services/api";
import StatCard from "../components/StatCard";
import ChartCard from "../components/ChartCard";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { Users, TrendingUp, DollarSign } from "lucide-react";

export default function Dashboard() {
  const [dau, setDau] = useState(0);
  const [growth, setGrowth] = useState([]);
  const [retention, setRetention] = useState([]);

  useEffect(() => {
    getDAU().then(res => setDau(res.data.dau)).catch(err => console.error(err));
    getUserGrowth().then(res => setGrowth(res.data)).catch(err => console.error(err));
    getRetention().then(res => setRetention(res.data)).catch(err => console.error(err));
  }, []);

  return (
    <div style={{ padding: "40px", background: "#000", minHeight: "100vh" }}>
      <h1 style={{ marginBottom: 32, fontWeight: "800", fontSize: "32px" }}>HabitHero Intelligence</h1>
      
      {/* TOP STATS */}
      <div style={{ display: "flex", gap: 24 }}>
        <StatCard title="Daily Active Users" value={dau} icon={<Users size={20} color="#00ffcc" />} />
        <StatCard title="Growth (7d)" value="+12%" icon={<TrendingUp size={20} color="#a855f7" />} />
        <StatCard title="Revenue (MTD)" value="₹0" icon={<DollarSign size={20} color="#eab308" />} />
      </div>

      {/* GROWTH CHART */}
      <ChartCard title="User Acquisition (Last 7 Days)">
        <div style={{ width: "100%", height: 300 }}>
          <ResponsiveContainer>
            <LineChart data={growth}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis dataKey="date" stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
              <Tooltip 
                contentStyle={{ backgroundColor: "#111", border: "none", borderRadius: 8 }}
                itemStyle={{ color: "#00ffcc" }}
              />
              <Line type="monotone" dataKey="users" stroke="#00ffcc" strokeWidth={3} dot={{ r: 4, fill: "#00ffcc" }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </ChartCard>

      <ChartCard title="Retention Cohorts">
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: 10 }}>
          <thead>
            <tr style={{ textAlign: "left", color: "rgba(255,255,255,0.3)", fontSize: "12px" }}>
              <th style={{ padding: 12 }}>Signup Date</th>
              <th style={{ padding: 12 }}>D0 (Acquisition)</th>
              <th style={{ padding: 12 }}>Day 1</th>
              <th style={{ padding: 12 }}>Day 7</th>
            </tr>
          </thead>
          <tbody>
            {retention.map((row: any, i: number) => (
              <tr key={i} style={{ borderTop: "1px solid rgba(255,255,255,0.05)" }}>
                <td style={{ padding: 12 }}>{row.signup_date}</td>
                <td style={{ padding: 12, color: "#00ffcc" }}>{row.d0} users</td>
                <td style={{ padding: 12, background: row.d1 > 0 ? "rgba(0, 255, 204, 0.1)" : "transparent" }}>
                  {row.d1} ({((row.d1/row.d0)*100 || 0).toFixed(1)}%)
                </td>
                <td style={{ padding: 12, background: row.d7 > 0 ? "rgba(168, 85, 247, 0.1)" : "transparent" }}>
                  {row.d7} ({((row.d7/row.d0)*100 || 0).toFixed(1)}%)
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </ChartCard>
    </div>
  );
}
