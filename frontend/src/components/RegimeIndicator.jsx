import React from 'react';
import { TrendingUp, TrendingDown, MinusCircle, ShieldAlert } from 'lucide-react';

const RegimeIndicator = ({ regime = 'Bull' }) => {
  const getRegimeConfig = (r) => {
    switch (r?.toLowerCase()) {
      case 'bull':
      case 'bullish':
        return {
          label: 'HMM REGIME: BULL MARKET',
          badgeClass: 'badge-bull',
          icon: <TrendingUp size={16} />,
          desc: 'Low Volatility / Expansionary'
        };
      case 'bear':
      case 'bearish':
        return {
          label: 'HMM REGIME: BEAR MARKET',
          badgeClass: 'badge-bear',
          icon: <TrendingDown size={16} />,
          desc: 'High Volatility / Contraction'
        };
      default:
        return {
          label: 'HMM REGIME: NEUTRAL',
          badgeClass: 'badge-neutral',
          icon: <MinusCircle size={16} />,
          desc: 'Range-bound Transition'
        };
    }
  };

  const cfg = getRegimeConfig(regime);

  return (
    <div className={`glass-panel ${cfg.badgeClass}`} style={{ padding: '8px 16px', borderRadius: '30px', display: 'flex', alignItems: 'center', gap: '10px' }}>
      {cfg.icon}
      <div>
        <div style={{ fontSize: '0.75rem', fontWeight: 800, letterSpacing: '0.05em' }}>
          {cfg.label}
        </div>
      </div>
    </div>
  );
};

export default RegimeIndicator;
