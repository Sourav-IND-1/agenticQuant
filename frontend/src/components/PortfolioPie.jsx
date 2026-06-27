import React from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';

/* Tight, desaturated palette — no neon */
const PALETTE = ['#3b82f6','#6366f1','#8b5cf6','#06b6d4','#10b981','#f59e0b','#ef4444'];

const fmt = (n) =>
  n.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });

const Tooltip_ = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div style={{
      background: '#18181b', border: '1px solid #27272a',
      borderRadius: '6px', padding: '8px 12px',
    }}>
      <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#fafafa', marginBottom: '3px' }}>{d.name}</div>
      <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.9rem', color: '#60a5fa' }}>{fmt(d.value)}</div>
      <div style={{ fontSize: '0.72rem', color: '#71717a', marginTop: '2px' }}>{d.pct}% of capital</div>
    </div>
  );
};

const PortfolioPie = ({ weights = {}, capital = 100000 }) => {
  const raw = Object.entries(weights).filter(([, w]) => w > 0.001)
    .map(([name, w]) => ({ name, value: Math.round(w * capital), pct: (w * 100).toFixed(1) }))
    .sort((a, b) => b.value - a.value);

  const data = raw.length ? raw : [
    { name: 'NVDA', value: Math.round(0.324 * capital), pct: '32.4' },
    { name: 'MSFT', value: Math.round(0.248 * capital), pct: '24.8' },
    { name: 'AAPL', value: Math.round(0.182 * capital), pct: '18.2' },
    { name: 'GOOGL',value: Math.round(0.146 * capital), pct: '14.6' },
    { name: 'JPM',  value: Math.round(0.100 * capital), pct: '10.0' },
  ];

  const total = data.reduce((s, d) => s + d.value, 0);

  return (
    <div className="card" style={{ padding: '16px', height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div className="section-label">
        <h3>Optimal Allocation</h3>
        <span className="badge badge-blue" style={{ marginLeft: 'auto' }}>PyPortfolioOpt</span>
      </div>

      {/* Total */}
      <div style={{ marginBottom: '12px', display: 'flex', alignItems: 'baseline', gap: '6px' }}>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '1.25rem', fontWeight: 600, color: '#fafafa' }}>{fmt(total)}</span>
        <span style={{ fontSize: '0.72rem', color: 'var(--t-2)' }}>total deployed across {data.length} assets</span>
      </div>

      <div style={{ display: 'flex', gap: '16px', flex: 1, minHeight: 0 }}>
        {/* Donut */}
        <div style={{ width: '160px', flexShrink: 0, position: 'relative' }}>
          <ResponsiveContainer width="100%" height={160}>
            <PieChart>
              <Pie data={data} cx="50%" cy="50%" innerRadius={48} outerRadius={72}
                paddingAngle={2} dataKey="value" strokeWidth={0}>
                {data.map((_, i) => <Cell key={i} fill={PALETTE[i % PALETTE.length]} />)}
              </Pie>
              <Tooltip content={<Tooltip_ />} />
            </PieChart>
          </ResponsiveContainer>
          {/* Center label */}
          <div style={{
            position: 'absolute', top: '50%', left: '50%',
            transform: 'translate(-50%, -50%)',
            textAlign: 'center', pointerEvents: 'none',
          }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.1rem', fontWeight: 600, color: '#fafafa' }}>{data.length}</div>
            <div style={{ fontSize: '0.62rem', color: 'var(--t-2)', textTransform: 'uppercase' }}>assets</div>
          </div>
        </div>

        {/* Allocation table */}
        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '2px' }}>
          {data.map((d, i) => (
            <div key={i} className="alloc-row">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '2px', background: PALETTE[i % PALETTE.length], flexShrink: 0 }} />
                <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--t-0)' }}>{d.name}</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem', color: 'var(--t-2)', minWidth: '38px', textAlign: 'right' }}>{d.pct}%</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', fontWeight: 600, color: '#fafafa', minWidth: '70px', textAlign: 'right' }}>{fmt(d.value)}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PortfolioPie;
