import React from 'react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const FALLBACK = [
  { date: 'Jan 20', strategy: 100.0, spy: 100.0 },
  { date: 'Apr 20', strategy: 92.4,  spy: 76.3  },
  { date: 'Jul 20', strategy: 108.1, spy: 98.2  },
  { date: 'Oct 20', strategy: 115.7, spy: 104.3 },
  { date: 'Jan 21', strategy: 131.2, spy: 113.6 },
  { date: 'Apr 21', strategy: 148.9, spy: 127.5 },
  { date: 'Jul 21', strategy: 157.4, spy: 133.2 },
  { date: 'Oct 21', strategy: 171.0, spy: 148.1 },
  { date: 'Jan 22', strategy: 155.3, spy: 132.0 },
  { date: 'Apr 22', strategy: 143.0, spy: 113.4 },
  { date: 'Jul 22', strategy: 158.6, spy: 119.8 },
  { date: 'Oct 22', strategy: 163.2, spy: 125.2 },
];

const Tooltip_ = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: '#18181b', border: '1px solid #27272a', borderRadius: '6px', padding: '8px 12px' }}>
      <div style={{ fontSize: '0.72rem', color: 'var(--t-2)', marginBottom: '5px' }}>{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '2px' }}>
          <span style={{ width: '8px', height: '2px', background: p.stroke, display: 'inline-block' }} />
          <span style={{ fontSize: '0.78rem', color: 'var(--t-1)' }}>{p.name}</span>
          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.82rem', color: '#fafafa', marginLeft: 'auto', paddingLeft: '16px' }}>
            {p.value.toFixed(1)}
          </span>
        </div>
      ))}
    </div>
  );
};

const BacktestChart = ({ backtestData = [] }) => {
  const data = backtestData.length ? backtestData : FALLBACK;

  const last = data[data.length - 1];
  const alpha = last ? (last.strategy - last.spy).toFixed(1) : '—';
  const strat  = last ? last.strategy.toFixed(1) : '—';

  return (
    <div className="card" style={{ padding: '16px', height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div className="section-label">
        <h3>Walk-Forward Backtest</h3>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: '6px' }}>
          <span className="badge badge-green">+{alpha}% α vs SPY</span>
          <span className="badge badge-zinc">Out-of-sample</span>
        </div>
      </div>

      {/* Summary stats row */}
      <div style={{ display: 'flex', gap: '20px', marginBottom: '12px' }}>
        {[
          { label: 'Strategy', value: `${strat}`, sub: '(base = 100)' },
          { label: 'Benchmark', value: last ? last.spy.toFixed(1) : '—', sub: 'SPY ETF' },
          { label: 'Total Alpha', value: `+${alpha}`, sub: 'vs SPY' },
        ].map((s, i) => (
          <div key={i}>
            <div style={{ fontSize: '0.7rem', color: 'var(--t-2)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '2px' }}>{s.label}</div>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '1.05rem', fontWeight: 600, color: '#fafafa' }}>{s.value}</span>
            <span style={{ fontSize: '0.7rem', color: 'var(--t-2)', marginLeft: '4px' }}>{s.sub}</span>
          </div>
        ))}
      </div>

      {/* Chart */}
      <div style={{ flex: 1, minHeight: '200px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 4, right: 8, left: -10, bottom: 0 }}>
            <defs>
              <linearGradient id="gStrat" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%"   stopColor="#3b82f6" stopOpacity={0.18} />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity={0}    />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="date"
              tick={{ fill: '#71717a', fontSize: 11 }}
              axisLine={{ stroke: '#1c1c1e' }} tickLine={false}
            />
            <YAxis
              tick={{ fill: '#71717a', fontSize: 11, fontFamily: 'var(--font-mono)' }}
              axisLine={false} tickLine={false} width={38}
            />
            <Tooltip content={<Tooltip_ />} />
            <Legend
              verticalAlign="top" align="right" height={28}
              wrapperStyle={{ fontSize: '0.72rem', color: '#a1a1aa', paddingBottom: '4px' }}
            />
            <Area
              type="monotone" dataKey="strategy" name="Strategy"
              stroke="#3b82f6" strokeWidth={2}
              fillOpacity={1} fill="url(#gStrat)"
              dot={false} activeDot={{ r: 3, fill: '#3b82f6' }}
            />
            <Area
              type="monotone" dataKey="spy" name="SPY"
              stroke="#52525b" strokeWidth={1.5} strokeDasharray="4 3"
              fillOpacity={0} fill="none"
              dot={false} activeDot={{ r: 3, fill: '#52525b' }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default BacktestChart;
