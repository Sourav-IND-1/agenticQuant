import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const RegimeIndicator = ({ regime = 'Bull' }) => {
  const cfg = {
    bull:    { label: 'Bull Market',  dot: 'dot-green', badge: 'badge-green', Icon: TrendingUp   },
    bear:    { label: 'Bear Market',  dot: 'dot-red',   badge: 'badge-red',   Icon: TrendingDown },
    neutral: { label: 'Neutral',      dot: 'dot-amber', badge: 'badge-amber', Icon: Minus        },
  }[regime?.toLowerCase()] || { label: 'Neutral', dot: 'dot-amber', badge: 'badge-amber', Icon: Minus };

  return (
    <div className={`badge ${cfg.badge}`} style={{ fontSize: '0.72rem', gap: '5px', padding: '4px 10px' }}>
      <span className={`dot ${cfg.dot}`} />
      HMM Regime · <strong>{cfg.label}</strong>
    </div>
  );
};

export default RegimeIndicator;
