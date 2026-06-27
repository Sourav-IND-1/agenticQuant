import React from 'react';
import { TrendingUp, TrendingDown, Activity } from 'lucide-react';

const RegimeIndicator = ({ regime = 'Bull' }) => {
  const getRegimeConfig = (r) => {
    switch (r?.toLowerCase()) {
      case 'bull':
      case 'bullish':
        return {
          label: 'Macro Regime: Bull',
          bg: '#064e3b',
          border: '#065f46',
          color: '#6ee7b7',
          icon: <TrendingUp size={15} color="#6ee7b7" />
        };
      case 'bear':
      case 'bearish':
        return {
          label: 'Macro Regime: Bear',
          bg: '#7f1d1d',
          border: '#991b1b',
          color: '#fca5a5',
          icon: <TrendingDown size={15} color="#fca5a5" />
        };
      default:
        return {
          label: 'Macro Regime: Neutral',
          bg: '#78350f',
          border: '#92400e',
          color: '#fde68a',
          icon: <Activity size={15} color="#fde68a" />
        };
    }
  };

  const cfg = getRegimeConfig(regime);

  return (
    <div style={{ 
      background: cfg.bg, 
      border: `1px solid ${cfg.border}`, 
      color: cfg.color,
      padding: '6px 12px', 
      borderRadius: '6px', 
      display: 'flex', 
      alignItems: 'center', 
      gap: '8px',
      fontSize: '0.8rem',
      fontWeight: 600
    }}>
      {cfg.icon}
      <span>{cfg.label}</span>
    </div>
  );
};

export default RegimeIndicator;
