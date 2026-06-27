import React from 'react';
import { Activity, BarChart2 } from 'lucide-react';
import RegimeIndicator from './RegimeIndicator';

const Navbar = ({ regime, onOpenHistory }) => {
  return (
    <header className="glass-panel" style={{ padding: '16px 24px', marginBottom: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', backgroundColor: '#111827' }}>
      {/* Brand & Logo - Left Side */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{ 
          background: '#1e293b',
          border: '1px solid #334155',
          padding: '10px',
          borderRadius: '6px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <BarChart2 size={20} color="#38bdf8" />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#f9fafb', margin: 0 }}>
              Quantitative Portfolio Analytics
            </h1>
            <span style={{ fontSize: '0.75rem', background: '#1e293b', color: '#93c5fd', padding: '2px 8px', borderRadius: '4px', fontWeight: 500, border: '1px solid #334155' }}>
              Institutional v2.4
            </span>
          </div>
          <p style={{ fontSize: '0.8rem', color: '#9ca3af', margin: 0 }}>
            Black-Litterman Optimization & Multi-Regime XGBoost Signals
          </p>
        </div>
      </div>

      {/* Center Macro Regime Badge */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {regime ? <RegimeIndicator regime={regime} /> : (
          <span style={{ fontSize: '0.8rem', color: '#6b7280', fontStyle: 'italic' }}>Awaiting Analysis...</span>
        )}
      </div>

      {/* Live NYSE Status Indicator & Archives - Right Side */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 12px', background: '#132a24', borderRadius: '4px', border: '1px solid #1f4e3d' }}>
          <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#34d399' }} />
          <span style={{ fontSize: '0.75rem', color: '#34d399', fontWeight: 500 }}>NSE Live Feed Connected</span>
        </div>

        <button 
          onClick={onOpenHistory}
          style={{
            background: '#1f2937',
            border: '1px solid #374151',
            color: '#f9fafb',
            padding: '8px 14px',
            borderRadius: '6px',
            fontSize: '0.85rem',
            fontWeight: 500,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'background 0.15s'
          }}
          onMouseOver={(e) => { e.currentTarget.style.background = '#374151'; }}
          onMouseOut={(e) => { e.currentTarget.style.background = '#1f2937'; }}
        >
          <Activity size={16} color="#38bdf8" />
          Execution Logs
        </button>
      </div>
    </header>
  );
};

export default Navbar;
