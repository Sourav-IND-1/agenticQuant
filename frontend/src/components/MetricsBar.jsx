import React from 'react';
import { TrendingUp, ShieldAlert, Zap, DollarSign, Award } from 'lucide-react';

const MetricsBar = ({ metrics = {} }) => {
  const defaultMetrics = {
    expectedReturn: metrics.expectedReturn ?? 0.148,
    sharpeRatio: metrics.sharpeRatio ?? 2.14,
    var95: metrics.var95 ?? -0.032,
    maxDrawdown: metrics.maxDrawdown ?? -0.085,
    capital: metrics.capital ?? 100000
  };

  const cards = [
    {
      title: 'Expected Alpha Return',
      value: `+${(defaultMetrics.expectedReturn * 100).toFixed(1)}%`,
      sub: 'Annualized Black-Litterman',
      icon: <TrendingUp size={20} color="var(--bull-green)" />,
      borderGlow: 'rgba(16, 185, 129, 0.3)',
      valueColor: 'var(--bull-green)'
    },
    {
      title: 'Sharpe Ratio',
      value: defaultMetrics.sharpeRatio.toFixed(2),
      sub: 'Risk-Adjusted Efficiency',
      icon: <Award size={20} color="var(--accent-cyan)" />,
      borderGlow: 'rgba(6, 182, 212, 0.3)',
      valueColor: '#ffffff'
    },
    {
      title: 'Value at Risk (95% Daily)',
      value: `${(defaultMetrics.var95 * 100).toFixed(2)}%`,
      sub: 'Parametric Cornish-Fisher',
      icon: <ShieldAlert size={20} color="var(--bear-red)" />,
      borderGlow: 'rgba(244, 63, 94, 0.3)',
      valueColor: 'var(--bear-red)'
    },
    {
      title: 'Max Drawdown Est.',
      value: `${(defaultMetrics.maxDrawdown * 100).toFixed(1)}%`,
      sub: 'Historical Stress Test',
      icon: <Zap size={20} color="var(--neutral-amber)" />,
      borderGlow: 'rgba(245, 158, 11, 0.3)',
      valueColor: 'var(--neutral-amber)'
    },
    {
      title: 'Active Capital Alloc.',
      value: `$${(defaultMetrics.capital / 1000).toFixed(0)}k`,
      sub: 'Fully Deployed Position',
      icon: <DollarSign size={20} color="var(--accent-blue)" />,
      borderGlow: 'rgba(59, 130, 246, 0.3)',
      valueColor: '#ffffff'
    }
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', marginBottom: '24px' }}>
      {cards.map((card, index) => (
        <div
          key={index}
          className="glass-panel"
          style={{
            padding: '18px 20px',
            borderLeft: `4px solid ${card.valueColor}`,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            boxShadow: `0 4px 20px ${card.borderGlow}`
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', fontWeight: 600 }}>{card.title}</span>
            <div style={{ background: 'rgba(255,255,255,0.05)', padding: '8px', borderRadius: '10px' }}>
              {card.icon}
            </div>
          </div>
          <div>
            <div className="font-mono" style={{ fontSize: '1.65rem', fontWeight: 800, color: card.valueColor, letterSpacing: '-0.02em' }}>
              {card.value}
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '4px' }}>
              {card.sub}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default MetricsBar;
