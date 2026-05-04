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
    <div style={{ 
      padding: "60px", 
      background: "radial-gradient(circle at top right, #1a1c2e, #0f1115)", 
      minHeight: "100vh", 
      color: "#ffffff",
      fontFamily: "'Inter', sans-serif"
    }}>
      <div style={{ maxWidth: "1200px", margin: "0 auto" }}>
        <header style={{ marginBottom: 48, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <h1 style={{ marginBottom: 8, fontWeight: "800", fontSize: "36px", letterSpacing: "-0.02em" }}>Intelligence Command</h1>
            <p style={{ color: "#9ca3af", fontSize: "16px" }}>Real-time behavioral heuristics & growth metrics.</p>
          </div>
          <div style={{ display: "flex", gap: 12 }}>
             <button style={{ padding: "10px 20px", borderRadius: "12px", background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)", color: "#fff", cursor: "pointer" }}>Export Data</button>
             <button style={{ padding: "10px 20px", borderRadius: "12px", background: "#7C8CFF", border: "none", color: "#fff", fontWeight: "600", cursor: "pointer" }}>Live View</button>
          </div>
        </header>
        
        {/* TOP STATS */}
        <div style={{ display: "flex", gap: 24 }}>
          <StatCard title="Daily Active Users" value={dau} icon={<Users size={20} color="#7C8CFF" />} />
          <StatCard title="Growth Velocity" value="+18.4%" icon={<TrendingUp size={20} color="#4ADE80" />} />
          <StatCard title="System Treasury" value="₹12.4K" icon={<DollarSign size={20} color="#FBBF24" />} />
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "2fr 1.2fr", gap: 24, marginTop: 24 }}>
          {/* GROWTH CHART */}
          <ChartCard title="User Acquisition Evolution">
            <div style={{ width: "100%", height: 350 }}>
              <ResponsiveContainer>
                <LineChart data={growth}>
                  <defs>
                    <linearGradient id="lineGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#7C8CFF" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#7C8CFF" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="date" stroke="#4b5563" tick={{ fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis stroke="#4b5563" tick={{ fontSize: 10 }} axisLine={false} tickLine={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: "#1c1f2a", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 12, boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)" }}
                    itemStyle={{ color: "#7C8CFF" }}
                  />
                  <Line type="monotone" dataKey="users" stroke="#7C8CFF" strokeWidth={4} dot={false} activeDot={{ r: 6, fill: "#7C8CFF", stroke: "#fff", strokeWidth: 2 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>

          <ChartCard title="Churn Risk Distribution">
             <div style={{ display: "flex", flexDirection: "column", gap: 20, marginTop: 10 }}>
                {[
                  { label: "High Risk (Inactive > 5d)", val: 12, color: "#F87171" },
                  { label: "Wandering (Burnout > 0.6)", val: 28, color: "#FBBF24" },
                  { label: "Stable (Consistent)", val: 60, color: "#4ADE80" }
                ].map(item => (
                  <div key={item.label}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                      <span style={{ fontSize: 12, color: "#9ca3af" }}>{item.label}</span>
                      <span style={{ fontSize: 12, fontWeight: "600" }}>{item.val}%</span>
                    </div>
                    <div style={{ height: 6, background: "rgba(255,255,255,0.05)", borderRadius: 3, overflow: "hidden" }}>
                      <div style={{ width: `${item.val}%`, height: "100%", background: item.color }} />
                    </div>
                  </div>
                ))}
             </div>
          </ChartCard>
        </div>

        <ChartCard title="Retention Cohort Analysis">
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ textAlign: "left", color: "#9ca3af", fontSize: "11px", textTransform: "uppercase", letterSpacing: "0.1em" }}>
                <th style={{ padding: "16px 12px" }}>Cohort Date</th>
                <th style={{ padding: "16px 12px" }}>Size</th>
                <th style={{ padding: "16px 12px" }}>D1 Retention</th>
                <th style={{ padding: "16px 12px" }}>D7 Retention</th>
                <th style={{ padding: "16px 12px" }}>Value Index</th>
              </tr>
            </thead>
            <tbody>
              {retention.map((row: any, i: number) => (
                <tr key={i} style={{ borderTop: "1px solid rgba(255,255,255,0.03)" }}>
                  <td style={{ padding: 16, fontWeight: 500, fontSize: "14px" }}>{row.signup_date}</td>
                  <td style={{ padding: 16, color: "#7C8CFF", fontWeight: "600" }}>{row.d0}</td>
                  <td style={{ padding: 16 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <div style={{ width: 40, height: 4, background: "rgba(255,255,255,0.05)", borderRadius: 2 }}>
                        <div style={{ width: `${(row.d1/row.d0)*100 || 0}%`, height: "100%", background: "#7C8CFF" }} />
                      </div>
                      <span style={{ fontSize: 13 }}>{((row.d1/row.d0)*100 || 0).toFixed(1)}%</span>
                    </div>
                  </td>
                  <td style={{ padding: 16 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      <div style={{ width: 40, height: 4, background: "rgba(255,255,255,0.05)", borderRadius: 2 }}>
                        <div style={{ width: `${(row.d7/row.d0)*100 || 0}%`, height: "100%", background: "#4ADE80" }} />
                      </div>
                      <span style={{ fontSize: 13 }}>{((row.d7/row.d0)*100 || 0).toFixed(1)}%</span>
                    </div>
                  </td>
                  <td style={{ padding: 16, color: "#4ADE80", fontSize: "13px" }}>A+</td>
                </tr>
              ))}
            </tbody>
          </table>
        </ChartCard>
      </div>
    </div>
  );
}
