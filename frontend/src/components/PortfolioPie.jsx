import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { PieChart as PieIcon } from 'lucide-react';

const COLORS = ['#3b82f6', '#06b6d4', '#8b5cf6', '#10b981', '#f59e0b', '#ec4899', '#64748b'];

const PortfolioPie = ({ weights = {} }) => {
  const data = Object.entries(weights)
    .filter(([_, value]) => value > 0.001)
    .map(([key, value]) => ({
      name: key,
      value: Math.round(value * 1000) / 10
    }))
    .sort((a, b) => b.value - a.value);

  const fallbackData = [
    { name: 'NVDA', value: 32.4 },
    { name: 'MSFT', value: 24.8 },
    { name: 'AAPL', value: 18.2 },
    { name: 'GOOGL', value: 14.6 },
    { name: 'JPM', value: 10.0 }
  ];

  const chartData = data.length > 0 ? data : fallbackData;

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="glass-panel" style={{ padding: '10px 14px', border: '1px solid var(--accent-blue)' }}>
          <p style={{ margin: 0, fontWeight: 700, color: '#ffffff' }}>{payload[0].name}</p>
          <p className="font-mono" style={{ margin: 0, color: 'var(--accent-cyan)', fontSize: '0.9rem' }}>
            Weight: {payload[0].value}%
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="glass-panel" style={{ padding: '20px', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
        <PieIcon size={18} color="var(--accent-blue)" />
        <h3 style={{ fontSize: '1.05rem', margin: 0 }}>Optimal Asset Allocation</h3>
        <span style={{ marginLeft: 'auto', fontSize: '0.75rem', background: 'rgba(59,130,246,0.15)', color: 'var(--accent-blue)', padding: '2px 8px', borderRadius: '12px' }}>
          PyPortfolioOpt
        </span>
      </div>

      <div style={{ flex: 1, minHeight: '260px', position: 'relative' }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={65}
              outerRadius={95}
              paddingAngle={4}
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="rgba(0,0,0,0.3)" strokeWidth={2} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
            <Legend 
              layout="vertical" 
              verticalAlign="middle" 
              align="right"
              wrapperStyle={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}
            />
          </PieChart>
        </ResponsiveContainer>
        
        {/* Center label */}
        <div style={{ position: 'absolute', top: '50%', left: '42%', transform: 'translate(-50%, -50%)', textAlign: 'center', pointerEvents: 'none' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Assets</div>
          <div className="font-mono" style={{ fontSize: '1.2rem', fontWeight: 700, color: '#ffffff' }}>{chartData.length}</div>
        </div>
      </div>
    </div>
  );
};

export default PortfolioPie;
