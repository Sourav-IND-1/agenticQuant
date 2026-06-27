import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const FALLBACK = [
  { feature: 'MA50',         importance: 0.38 },
  { feature: 'MACD_signal',  importance: 0.33 },
  { feature: 'RSI',          importance: 0.11 },
  { feature: 'BB_lower',     importance: 0.07 },
  { feature: 'ADX',          importance: 0.05 },
  { feature: 'Volume_chg',   importance: 0.04 },
];

/* Single blue palette, varying opacity — professional, readable */
const barColor = (i) => {
  const opacities = [1, 0.85, 0.65, 0.5, 0.4, 0.3];
  return `rgba(59,130,246,${opacities[i] ?? 0.25})`;
};

const Tooltip_ = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: '#18181b', border: '1px solid #27272a', borderRadius: '6px', padding: '8px 12px' }}>
      <div style={{ fontSize: '0.78rem', fontWeight: 600, color: '#fafafa', marginBottom: '2px' }}>{payload[0].payload.feature}</div>
      <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.88rem', color: '#60a5fa' }}>
        {payload[0].value.toFixed(1)}% attribution
      </div>
    </div>
  );
};

const ShapChart = ({ featureImportances = [] }) => {
  const raw = featureImportances.length ? featureImportances : FALLBACK;
  const data = raw.slice(0, 6).map(d => ({
    feature: d.feature,
    value: +(d.importance * 100).toFixed(1),
  }));

  return (
    <div className="card" style={{ padding: '16px', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div className="section-label">
        <h3>Feature Attribution</h3>
        <span className="badge badge-zinc" style={{ marginLeft: 'auto' }}>SHAP · XGBoost</span>
      </div>

      <div style={{ flex: 1, minHeight: '220px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 0, right: 16, left: 0, bottom: 0 }}
          >
            <XAxis
              type="number" unit="%" dataKey="value"
              tick={{ fill: '#71717a', fontSize: 11, fontFamily: 'var(--font-mono)' }}
              axisLine={{ stroke: '#1c1c1e' }} tickLine={false}
            />
            <YAxis
              dataKey="feature" type="category" width={88}
              tick={{ fill: '#a1a1aa', fontSize: 11, fontFamily: 'var(--font-mono)' }}
              axisLine={false} tickLine={false}
            />
            <Tooltip content={<Tooltip_ />} cursor={{ fill: 'rgba(255,255,255,0.025)' }} />
            <Bar dataKey="value" radius={[0, 3, 3, 0]} barSize={14}>
              {data.map((_, i) => <Cell key={i} fill={barColor(i)} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div style={{ marginTop: '8px', fontSize: '0.7rem', color: 'var(--t-2)', borderTop: '1px solid var(--line-0)', paddingTop: '8px' }}>
        Shapley values — average marginal contribution to model prediction across held-out test data.
      </div>
    </div>
  );
};

export default ShapChart;
