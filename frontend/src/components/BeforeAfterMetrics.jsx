import React from 'react';
import { Activity, ShieldAlert, ArrowDownRight, Layers } from 'lucide-react';

const MetricCard = ({ title, icon: Icon, beforeValue, afterValue, betterIsHigher }) => {
  let isBetter = false;
  if (typeof beforeValue === 'number' && typeof afterValue === 'number') {
    isBetter = betterIsHigher ? afterValue > beforeValue : afterValue < beforeValue;
  } else if (typeof beforeValue === 'string') {
    // Basic logic for Diversification
    const ranks = { "Low": 1, "Moderate": 2, "High": 3 };
    isBetter = (ranks[afterValue] || 0) >= (ranks[beforeValue] || 0);
  }

  const formatValue = (val) => {
    if (typeof val === 'number') {
      if (title.includes('Ratio')) return val.toFixed(2);
      if (title.includes('CVaR') || title.includes('Drawdown')) return (val * 100).toFixed(1) + '%';
      return val.toFixed(2);
    }
    return val;
  };

  return (
    <div style={{ background: '#1f2937', padding: '16px', borderRadius: '8px', border: '1px solid #374151', display: 'flex', flexDirection: 'column', gap: '8px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#9ca3af' }}>
        <Icon size={16} />
        <span style={{ fontSize: '0.85rem', fontWeight: 500 }}>{title}</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <span style={{ color: '#d1d5db', fontSize: '1.1rem', textDecoration: 'line-through', opacity: 0.7 }}>
          {formatValue(beforeValue)}
        </span>
        <span style={{ color: '#6b7280' }}>→</span>
        <span style={{ color: isBetter ? '#34d399' : '#f87171', fontSize: '1.25rem', fontWeight: 600 }}>
          {formatValue(afterValue)}
        </span>
      </div>
    </div>
  );
};

const BeforeAfterMetrics = ({ beforeMetrics, afterMetrics }) => {
  if (!beforeMetrics || !afterMetrics) return null;

  return (
    <div className="glass-panel" style={{ padding: '18px 20px', backgroundColor: '#111827' }}>
      <h3 style={{ fontSize: '0.95rem', margin: '0 0 16px 0', color: '#f9fafb', fontWeight: 600 }}>Portfolio Improvement Metrics</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
        <MetricCard 
          title="Sharpe Ratio" 
          icon={Activity} 
          beforeValue={beforeMetrics.sharpe} 
          afterValue={afterMetrics.sharpe} 
          betterIsHigher={true}
        />
        <MetricCard 
          title="CVaR (95%)" 
          icon={ShieldAlert} 
          beforeValue={beforeMetrics.cvar_95} 
          afterValue={afterMetrics.cvar_95} 
          betterIsHigher={true} // CVaR is usually negative, so a higher (closer to 0) number is better
        />
        <MetricCard 
          title="Max Drawdown" 
          icon={ArrowDownRight} 
          beforeValue={beforeMetrics.max_drawdown} 
          afterValue={afterMetrics.max_drawdown} 
          betterIsHigher={true} // Also negative, higher is better
        />
        <MetricCard 
          title="Diversification" 
          icon={Layers} 
          beforeValue={beforeMetrics.diversification || 'Low'} 
          afterValue={afterMetrics.diversification || 'High'} 
          betterIsHigher={true}
        />
      </div>
    </div>
  );
};

export default BeforeAfterMetrics;
