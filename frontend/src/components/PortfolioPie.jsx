import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { PieChart as PieIcon, DollarSign } from 'lucide-react';

const COLORS = ['#2563eb', '#38bdf8', '#6366f1', '#10b981', '#f59e0b', '#ec4899', '#64748b'];

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
        <div className="glass-panel" style={{ padding: '10px 14px', border: '1px solid #2563eb', backgroundColor: '#1f2937' }}>
          <p style={{ margin: 0, fontWeight: 600, color: '#ffffff', fontSize: '0.9rem' }}>{item.name}</p>
          <p className="font-mono" style={{ margin: '4px 0 2px 0', color: '#38bdf8', fontSize: '1rem', fontWeight: 600 }}>
            Allocation: {item.formattedAmount}
          </p>
          <span style={{ fontSize: '0.75rem', color: '#9ca3af' }}>{item.weightPct}% of total budget</span>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="glass-panel" style={{ padding: '20px', height: '100%', display: 'flex', flexDirection: 'column', backgroundColor: '#111827' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
        <PieIcon size={18} color="#38bdf8" />
        <h3 style={{ fontSize: '1rem', margin: 0, color: '#f9fafb', fontWeight: 600 }}>Optimal Asset Deployment</h3>
        <span style={{ marginLeft: 'auto', fontSize: '0.75rem', background: '#1e293b', color: '#93c5fd', padding: '4px 10px', borderRadius: '4px', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 500, border: '1px solid #334155' }}>
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
                paddingAngle={3}
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="#111827" strokeWidth={2} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          
          {/* Center label */}
          <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center', pointerEvents: 'none' }}>
            <div style={{ fontSize: '0.7rem', color: '#9ca3af', textTransform: 'uppercase' }}>Assets</div>
            <div className="font-mono" style={{ fontSize: '1.25rem', fontWeight: 700, color: '#ffffff' }}>{chartData.length}</div>
          </div>
        </div>

        {/* Exact Dollar Breakdown List */}
        <div style={{ flex: '1 1 180px', display: 'flex', flexDirection: 'column', gap: '6px', maxHeight: '240px', overflowY: 'auto', paddingRight: '4px' }}>
          <div style={{ fontSize: '0.75rem', color: '#9ca3af', fontWeight: 500, marginBottom: '2px', textTransform: 'uppercase' }}>
            Exact Amount per Asset
          </div>
          {chartData.map((item, index) => (
            <div 
              key={index} 
              style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'space-between', 
                padding: '8px 12px', 
                background: '#1f2937', 
                borderRadius: '6px', 
                borderLeft: `3px solid ${COLORS[index % COLORS.length]}`,
                borderTop: '1px solid #374151',
                borderRight: '1px solid #374151',
                borderBottom: '1px solid #374151'
              }}
            >
              <span style={{ fontWeight: 600, color: '#f9fafb', fontSize: '0.85rem' }}>{item.name}</span>
              <span className="font-mono" style={{ fontWeight: 600, color: '#38bdf8', fontSize: '0.88rem' }}>
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
