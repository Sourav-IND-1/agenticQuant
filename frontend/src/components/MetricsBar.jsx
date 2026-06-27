import React from 'react';
import { TrendingUp, AlertTriangle, Activity, Wallet, Award } from 'lucide-react';

const MetricsBar = ({ metrics = {} }) => {
  const m = {
    expectedReturn: metrics.expectedReturn ?? 0.148,
    sharpeRatio:    metrics.sharpeRatio    ?? 2.14,
    var95:          metrics.var95          ?? -0.032,
    maxDrawdown:    metrics.maxDrawdown    ?? -0.085,
    capital:        metrics.capital        ?? 100000,
  };

  const cards = [
    {
      label: 'Expected Return',
      value: `+${(m.expectedReturn * 100).toFixed(2)}%`,
      sub: 'Annualized BL posterior',
      icon: <TrendingUp size={14} color="var(--green)" />,
      accentColor: 'var(--green)',
    },
    {
      label: 'Sharpe Ratio',
      value: m.sharpeRatio.toFixed(2),
      sub: 'Risk-adj. α / σ (Rf=4%)',
      icon: <Award size={14} color="#60a5fa" />,
      accentColor: '#60a5fa',
    },
    {
      label: 'CVaR 95%',
      value: `${(m.var95 * 100).toFixed(2)}%`,
      sub: 'Expected tail loss',
      icon: <AlertTriangle size={14} color="var(--red)" />,
      accentColor: 'var(--red)',
    },
    {
      label: 'Max Drawdown',
      value: `${(m.maxDrawdown * 100).toFixed(2)}%`,
      sub: 'Peak-to-trough historical',
      icon: <Activity size={14} color="var(--amber)" />,
      accentColor: 'var(--amber)',
    },
    {
      label: 'Deployed Capital',
      value: m.capital.toLocaleString('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }),
      sub: 'Total position size',
      icon: <Wallet size={14} color="#a78bfa" />,
      accentColor: '#a78bfa',
    },
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '10px', marginBottom: '20px' }}>
      {cards.map((c, i) => (
        <div key={i} className="kpi-card" style={{ borderTop: `2px solid ${c.accentColor}` }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span className="kpi-label">{c.label}</span>
            {c.icon}
          </div>
          <div className="kpi-value mono">{c.value}</div>
          <div className="kpi-sub">{c.sub}</div>
        </div>
      ))}
    </div>
  );
};

export default MetricsBar;
