import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { PieChart as PieIcon, DollarSign } from 'lucide-react';

const COLORS = ['#3b82f6', '#06b6d4', '#8b5cf6', '#10b981', '#f59e0b', '#ec4899', '#64748b'];

const PortfolioPie = ({ weights = {}, capital = 100000 }) => {
  const data = Object.entries(weights)
    .filter(([_, weight]) => weight > 0.001)
    .map(([key, weight]) => {
      const exactAmount = Math.round(weight * capital);
      return {
        name: key,
        value: exactAmount,
        weightPct: (weight * 100).toFixed(1),
        formattedAmount: exactAmount.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })
      };
    })
    .sort((a, b) => b.value - a.value);

  const fallbackData = [
    { name: 'NVDA', weight: 0.324 },
    { name: 'MSFT', weight: 0.248 },
    { name: 'AAPL', weight: 0.182 },
    { name: 'GOOGL', weight: 0.146 },
    { name: 'JPM', weight: 0.100 }
  ].map(item => {
    const exactAmount = Math.round(item.weight * capital);
    return {
      name: item.name,
      value: exactAmount,
      weightPct: (item.weight * 100).toFixed(1),
      formattedAmount: exactAmount.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })
    };
  });

  const chartData = data.length > 0 ? data : fallbackData;
  const totalAllocated = chartData.reduce((sum, item) => sum + item.value, 0).toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="glass-panel" style={{ padding: '12px 16px', border: '1px solid var(--accent-blue)', boxShadow: '0 8px 32px rgba(0,0,0,0.5)' }}>
          <p style={{ margin: 0, fontWeight: 800, color: '#ffffff', fontSize: '1rem' }}>{item.name}</p>
          <p className="font-mono" style={{ margin: '4px 0 2px 0', color: 'var(--accent-cyan)', fontSize: '1.1rem', fontWeight: 700 }}>
            Exact Investment: {item.formattedAmount}
          </p>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{item.weightPct}% of total deployment</span>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="glass-panel" style={{ padding: '20px', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
        <PieIcon size={18} color="var(--accent-blue)" />
        <h3 style={{ fontSize: '1.05rem', margin: 0 }}>Optimal Asset Allocation (Exact Dollar Deployment)</h3>
        <span style={{ marginLeft: 'auto', fontSize: '0.75rem', background: 'rgba(59,130,246,0.15)', color: 'var(--accent-cyan)', padding: '4px 10px', borderRadius: '12px', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600 }}>
          <DollarSign size={12} /> Total: {totalAllocated}
        </span>
      </div>

      <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap', minHeight: '260px' }}>
        {/* Donut Chart */}
        <div style={{ flex: '1 1 200px', height: '240px', position: 'relative' }}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={4}
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="rgba(0,0,0,0.3)" strokeWidth={2} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          
          {/* Center label */}
          <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center', pointerEvents: 'none' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Companies</div>
            <div className="font-mono" style={{ fontSize: '1.3rem', fontWeight: 800, color: '#ffffff' }}>{chartData.length}</div>
          </div>
        </div>

        {/* Exact Dollar Breakdown List */}
        <div style={{ flex: '1 1 180px', display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '240px', overflowY: 'auto', paddingRight: '4px' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '2px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Exact Amount per Company
          </div>
          {chartData.map((item, index) => (
            <div 
              key={index} 
              style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between', 
                padding: '8px 12px', 
                background: 'rgba(255,255,255,0.03)', 
                borderRadius: '10px', 
                borderLeft: `4px solid ${COLORS[index % COLORS.length]}`,
                borderTop: '1px solid rgba(255,255,255,0.05)',
                borderRight: '1px solid rgba(255,255,255,0.05)',
                borderBottom: '1px solid rgba(255,255,255,0.05)',
                transition: 'all 0.2s'
              }}
              onMouseOver={(e) => { e.currentTarget.style.background = 'rgba(255,255,255,0.08)'; }}
              onMouseOut={(e) => { e.currentTarget.style.background = 'rgba(255,255,255,0.03)'; }}
            >
              <span style={{ fontWeight: 800, color: '#ffffff', fontSize: '0.9rem' }}>{item.name}</span>
              <span className="font-mono" style={{ fontWeight: 700, color: 'var(--accent-cyan)', fontSize: '0.92rem' }}>
                {item.formattedAmount}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PortfolioPie;
