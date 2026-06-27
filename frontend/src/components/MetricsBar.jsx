import React from 'react';
import { TrendingUp, AlertTriangle, Activity, DollarSign, Award } from 'lucide-react';

const MetricsBar = ({ metrics }) => {
  if (!metrics) return null;

  // Backend sends snake_case, mock sends camelCase — handle both
  const defaultMetrics = {
    expectedReturn: metrics.expectedReturn ?? metrics.annualized_return ?? metrics.cagr ?? 0,
    sharpeRatio: metrics.sharpeRatio ?? metrics.sharpe ?? 0,
    var95: metrics.var95 ?? metrics.cvar_95 ?? 0,
    maxDrawdown: metrics.maxDrawdown ?? metrics.max_drawdown ?? 0,
    capital: metrics.capital ?? 0
  };

  const cards = [
    {
      title: 'Expected Annual Return',
      value: `+${(defaultMetrics.expectedReturn * 100).toFixed(1)}%`,
      sub: 'Post-Optimization Posterior',
      icon: <TrendingUp size={18} color="#34d399" />,
      borderTop: '#059669',
      valueColor: '#34d399'
    },
    {
      title: 'Sharpe Ratio',
      value: defaultMetrics.sharpeRatio.toFixed(2),
      sub: 'Annualized (Rf = 4.0%)',
      icon: <Award size={18} color="#38bdf8" />,
      borderTop: '#0284c7',
      valueColor: '#f9fafb'
    },
    {
      title: 'Daily Value at Risk (95%)',
      value: `${(defaultMetrics.var95 * 100).toFixed(2)}%`,
      sub: 'Historical Cornisher-Fisher',
      icon: <AlertTriangle size={18} color="#f87171" />,
      borderTop: '#dc2626',
      valueColor: '#f87171'
    },
    {
      title: 'Est. Max Drawdown',
      value: `${(defaultMetrics.maxDrawdown * 100).toFixed(1)}%`,
      sub: 'Peak-to-Trough Stress Test',
      icon: <Activity size={18} color="#fbbf24" />,
      borderTop: '#d97706',
      valueColor: '#fbbf24'
    },
    {
      title: 'Deployed Capital',
      value: defaultMetrics.capital.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }),
      sub: 'Total Active Allocation',
      icon: <DollarSign size={18} color="#60a5fa" />,
      borderTop: '#2563eb',
      valueColor: '#f9fafb'
    }
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '20px' }}>
      {cards.map((card, index) => (
        <div
          key={index}
          className="glass-panel"
          style={{
            padding: '16px 18px',
            borderTop: `3px solid ${card.borderTop}`,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            backgroundColor: '#111827'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
            <span style={{ fontSize: '0.8rem', color: '#9ca3af', fontWeight: 500 }}>{card.title}</span>
            <div style={{ background: '#1f2937', padding: '6px', borderRadius: '6px' }}>
              {card.icon}
            </div>
          </div>
          <div>
            <div className="font-mono" style={{ fontSize: '1.5rem', fontWeight: 600, color: card.valueColor }}>
              {card.value}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '2px' }}>
              {card.sub}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default MetricsBar;
