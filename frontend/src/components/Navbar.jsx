import React from 'react';
import { BarChart2, Clock, History } from 'lucide-react';
import RegimeIndicator from './RegimeIndicator';

const Navbar = ({ regime = 'Bull', onOpenHistory }) => {
  const now = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });

  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      height: '52px',
      padding: '0 24px',
      marginBottom: '20px',
      background: '#0e0e10',
      border: '1px solid #1c1c1e',
      borderRadius: '8px'
    }}>

      {/* Left — Brand */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <BarChart2 size={16} color="#3b82f6" strokeWidth={2} />
        <span style={{ fontSize: '0.875rem', fontWeight: 700, color: '#fafafa', letterSpacing: '-0.01em' }}>
          Portfolio Intelligence
        </span>
        <span style={{ width: '1px', height: '14px', background: '#27272a' }} />
        <span style={{ fontSize: '0.75rem', color: '#71717a', fontWeight: 400 }}>
          Black-Litterman · XGBoost · HMM Regime
        </span>
      </div>

      {/* Center — Regime */}
      <RegimeIndicator regime={regime} />

      {/* Right — Status + Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        {/* Live dot */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px', padding: '4px 10px', background: '#052e16', border: '1px solid #14532d', borderRadius: '4px' }}>
          <span className="dot dot-green" />
          <span style={{ fontSize: '0.72rem', color: '#86efac', fontWeight: 500, fontFamily: 'var(--font-mono)' }}>
            NYSE {now}
          </span>
        </div>

        {/* History */}
        <button
          className="btn btn-ghost"
          onClick={onOpenHistory}
          style={{ height: '30px', fontSize: '0.775rem', gap: '5px' }}
        >
          <History size={13} />
          Runs
        </button>
      </div>
    </header>
  );
};

export default Navbar;
