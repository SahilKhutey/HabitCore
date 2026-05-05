import React, { useEffect, useState } from "react";
import { AnalyticsAdapter } from "../services/AnalyticsAdapter";
import StatCard from "../components/StatCard";
import ChartCard from "../components/ChartCard";
import { 
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  PieChart, Pie, Cell, BarChart, Bar
} from "recharts";
import { Users, TrendingUp, DollarSign, Activity, Zap, ShieldCheck, ShieldAlert, Clock } from "lucide-react";

const COLORS_WELLNESS = ['#6DBA9D', '#8BA4D0', '#E89B9B', '#A78BFA'];

export default function Dashboard() {
  const [stats, setStats] = useState<any>({});
  const [growth, setGrowth] = useState([]);
  const [retention, setRetention] = useState([]);
  const [archetypes, setArchetypes] = useState([]);
  const [topHabits, setTopHabits] = useState([]);
  const [events, setEvents] = useState<any[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      const [s, g, r, a, th, e] = await Promise.all([
        AnalyticsAdapter.getStats(),
        AnalyticsAdapter.getUserGrowth(),
        AnalyticsAdapter.getRetention(),
        AnalyticsAdapter.getArchetypeDistribution(),
        AnalyticsAdapter.getTopHabits(),
        AnalyticsAdapter.getRecentEvents()
      ]);
      setStats(s);
      setGrowth(g);
      setRetention(r);
      setArchetypes(a);
      setTopHabits(th);
      setEvents(e);
    };

    fetchData();

    // WebSocket connection for real-time events
    const ws = new WebSocket("ws://localhost:8000/ws");
    ws.onmessage = (msg) => {
      const data = JSON.parse(msg.data);
      setEvents(prev => [data, ...prev].slice(0, 50));
    };

    return () => ws.close();
  }, []);

  const handleAction = async (action: 'ban' | 'premium', userId: string) => {
    try {
      if (action === 'ban') {
        if (window.confirm("Ban this user?")) {
           await AnalyticsAdapter.banUser(userId);
           alert("User banned");
        }
      } else {
        await AnalyticsAdapter.grantPremium(userId);
        alert("Premium granted");
      }
    } catch (e) {
      alert("Action failed");
    }
  };

  return (
    <div style={{ 
      padding: "60px", 
      background: "#F8F9FB",
      minHeight: "100vh", 
      color: "#1A1F2E",
      fontFamily: "'Space Grotesk', sans-serif"
    }}>
      <div style={{ maxWidth: "1500px", margin: "0 auto" }}>
        <header style={{ 
          marginBottom: 64, 
          display: "flex", 
          justifyContent: "space-between", 
          alignItems: "center",
          background: "#ffffff",
          padding: "32px",
          borderRadius: "32px",
          border: "1px solid #E5E7EB",
          boxShadow: "0 4px 20px rgba(0, 0, 0, 0.02)"
        }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
              <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#6DBA9D", boxShadow: "0 0 15px rgba(109, 186, 157, 0.3)" }} />
              <h1 style={{ margin: 0, fontWeight: "900", fontSize: "42px", letterSpacing: "-0.04em", color: "#1A1F2E" }}>Intelligence Command</h1>
            </div>
            <p style={{ color: "#6B7280", fontSize: "18px", margin: 0, fontWeight: "500" }}>
              Real-time behavioral heuristics <span style={{ color: "#E5E7EB", margin: "0 8px" }}>|</span> Growth velocity metrics
            </p>
          </div>
          <div style={{ display: "flex", gap: 16 }}>
             <button style={headerButtonStyle}>Export Analytics</button>
             <button style={{ ...headerButtonStyle, background: "#6DBA9D", border: "none", fontWeight: "700", color: "#fff" }}>
                Deploy Insights
             </button>
          </div>
        </header>
        
        {/* TOP STATS */}
        <div style={{ display: "flex", gap: 24 }}>
          <StatCard title="Total Users" value={stats.total_users || 0} icon={<Users size={20} color="#6DBA9D" />} />
          <StatCard title="Growth Velocity" value={stats.growth_velocity || "0%"} icon={<TrendingUp size={20} color="#6DBA9D" />} />
          <StatCard title="Premium Rate" value={`${stats.premium_rate || 0}%`} icon={<Zap size={20} color="#6DBA9D" />} />
          <StatCard title="System Treasury" value={`₹${(stats.system_treasury || 0).toLocaleString()}`} icon={<DollarSign size={20} color="#6DBA9D" />} />
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1.5fr 1fr", gap: 24, marginTop: 24 }}>
          {/* GROWTH CHART */}
          <ChartCard title="User Acquisition Evolution">
            <div style={{ width: "100%", height: 350 }}>
              <ResponsiveContainer>
                <LineChart data={growth}>
                  <XAxis dataKey="date" stroke="#4b5563" tick={{ fontSize: 10 }} axisLine={false} tickLine={false} />
                  <YAxis stroke="#4b5563" tick={{ fontSize: 10 }} axisLine={false} tickLine={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: "#ffffff", border: "1px solid #E5E7EB", borderRadius: 12, color: "#1A1F2E" }}
                    itemStyle={{ color: "#1A1F2E" }}
                  />
                  <Line type="monotone" dataKey="users" stroke="#6DBA9D" strokeWidth={4} dot={false} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>

          {/* IDENTITY DISTRIBUTION */}
          <ChartCard title="Identity Archetype Distribution">
             <div style={{ width: "100%", height: 350 }}>
                <ResponsiveContainer>
                  <PieChart>
                    <Pie
                      data={archetypes}
                      dataKey="count"
                      nameKey="archetype"
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      innerRadius={60}
                      stroke="none"
                    >
                      {archetypes.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS_WELLNESS[index % COLORS_WELLNESS.length]} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid #E5E7EB" }} />
                  </PieChart>
                </ResponsiveContainer>
             </div>
          </ChartCard>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1.5fr", gap: 24, marginTop: 24 }}>
           {/* TOP HABITS */}
           <ChartCard title="Top Behavioral Anchors">
              <div style={{ width: "100%", height: 350 }}>
                <ResponsiveContainer>
                  <BarChart data={topHabits} layout="vertical">
                    <XAxis type="number" hide />
                    <YAxis dataKey="name" type="category" stroke="#6B7280" fontSize={12} width={100} />
                    <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid #E5E7EB" }} />
                    <Bar dataKey="count" fill="#6DBA9D" radius={[0, 4, 4, 0]} barSize={20} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
           </ChartCard>

           {/* LIVE FEED */}
           <ChartCard title="Live Intelligence Feed">
              <div style={{ height: 350, overflowY: "auto", paddingRight: 10 }}>
                 {events.length === 0 && <p style={{ color: "#9CA3AF", textAlign: "center", marginTop: 100 }}>Waiting for signals...</p>}
                 {events.map((e, i) => (
                   <div key={i} style={eventItemStyle}>
                      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                        <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#6DBA9D", boxShadow: "0 0 10px rgba(109, 186, 157, 0.3)" }} />
                        <div>
                          <p style={{ fontSize: 13, fontWeight: "600", margin: 0, color: "#1A1F2E" }}>{e.event_type}</p>
                          <p style={{ fontSize: 11, color: "#6B7280", margin: 0 }}>User: {e.user_id.slice(0, 8)}...</p>
                        </div>
                      </div>
                      <div style={{ display: "flex", gap: 8 }}>
                         <button onClick={() => handleAction('premium', e.user_id)} style={miniButtonStyle} title="Grant Premium">
                            <ShieldCheck size={14} color="#6DBA9D" />
                         </button>
                         <button onClick={() => handleAction('ban', e.user_id)} style={miniButtonStyle} title="Ban User">
                            <ShieldAlert size={14} color="#F87171" />
                         </button>
                      </div>
                   </div>
                 ))}
              </div>
           </ChartCard>
        </div>

        {/* RETENTION TABLE */}
        <div style={{ marginTop: 24 }}>
          <ChartCard title="Retention Cohort Analysis">
            <table style={{ width: "100%", borderCollapse: "separate", borderSpacing: "0 8px" }}>
              <thead>
                <tr style={{ textAlign: "left", color: "#9CA3AF", fontSize: "11px", textTransform: "uppercase", letterSpacing: "0.2em" }}>
                  <th style={{ padding: "16px 24px" }}>Cohort Date</th>
                  <th style={{ padding: "16px 24px" }}>Size</th>
                  <th style={{ padding: "16px 24px" }}>D1 Retention</th>
                  <th style={{ padding: "16px 24px" }}>D7 Retention</th>
                  <th style={{ padding: "16px 24px" }}>Value Index</th>
                </tr>
              </thead>
              <tbody>
                {retention.map((row: any, i: number) => (
                  <tr key={i} style={{ 
                    background: "#F9FAFB", 
                    borderRadius: "16px",
                    transition: "all 0.2s"
                  }}>
                    <td style={{ padding: "20px 24px", fontWeight: "600", fontSize: "15px", color: "#1A1F2E", borderTopLeftRadius: "16px", borderBottomLeftRadius: "16px" }}>{row.signup_date}</td>
                    <td style={{ padding: "20px 24px", color: "#6DBA9D", fontWeight: "700", fontSize: "16px" }}>{row.d0}</td>
                    <td style={{ padding: "20px 24px" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                        <div style={{ width: 60, height: 6, background: "#E5E7EB", borderRadius: 3, overflow: "hidden" }}>
                          <div style={{ width: `${(row.d1/row.d0)*100 || 0}%`, height: "100%", background: "#6DBA9D" }} />
                        </div>
                        <span style={{ fontSize: 14, fontWeight: "600", color: "#4B5563" }}>{((row.d1/row.d0)*100 || 0).toFixed(1)}%</span>
                      </div>
                    </td>
                    <td style={{ padding: "20px 24px" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                        <div style={{ width: 60, height: 6, background: "#E5E7EB", borderRadius: 3, overflow: "hidden" }}>
                          <div style={{ width: `${(row.d7/row.d0)*100 || 0}%`, height: "100%", background: "#8BA4D0" }} />
                        </div>
                        <span style={{ fontSize: 14, fontWeight: "600", color: "#4B5563" }}>{((row.d7/row.d0)*100 || 0).toFixed(1)}%</span>
                      </div>
                    </td>
                    <td style={{ padding: "20px 24px", borderTopRightRadius: "16px", borderBottomRightRadius: "16px" }}>
                      <span style={{ 
                        padding: "6px 12px", 
                        background: "rgba(109, 186, 157, 0.1)", 
                        color: "#6DBA9D", 
                        borderRadius: "8px", 
                        fontSize: "12px", 
                        fontWeight: "700",
                        border: "1px solid rgba(109, 186, 157, 0.2)"
                      }}>
                        A+ HIGH
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </ChartCard>
        </div>
      </div>
    </div>
  );
}

const headerButtonStyle: React.CSSProperties = {
  padding: "10px 20px", 
  borderRadius: "12px", 
  background: "#F9FAFB", 
  border: "1px solid #E5E7EB", 
  color: "#4B5563", 
  cursor: "pointer",
  fontWeight: "600",
  transition: "all 0.2s"
};

const eventItemStyle: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  padding: "12px",
  background: "#ffffff",
  borderRadius: "12px",
  marginBottom: "8px",
  border: "1px solid #F0F2F5"
};

const miniButtonStyle: React.CSSProperties = {
  background: "#F9FAFB",
  border: "1px solid #E5E7EB",
  padding: "6px",
  borderRadius: "8px",
  cursor: "pointer",
  display: "flex",
  alignItems: "center",
  justifyContent: "center"
};

