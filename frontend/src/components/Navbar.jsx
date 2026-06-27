import React from 'react';
import { Activity, Zap } from 'lucide-react';
import RegimeIndicator from './RegimeIndicator';

const Navbar = ({ regime = 'Bull', lastUpdated = 'Just now', onOpenHistory }) => {
  return (
    <header className="glass-panel" style={{ padding: '16px 24px', marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      {/* Brand & Logo - Left Side */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{ 
          background: 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))',
          padding: '10px',
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 20px rgba(59, 130, 246, 0.4)'
        }}>
          <Zap size={22} color="#ffffff" />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <h1 style={{ fontSize: '1.4rem', fontWeight: 800, letterSpacing: '-0.03em', background: 'linear-gradient(to right, #ffffff, #94a3b8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', margin: 0 }}>
              IGNITE ROOM
            </h1>
            <span style={{ fontSize: '0.75rem', background: 'rgba(59, 130, 246, 0.2)', color: 'var(--accent-cyan)', padding: '2px 8px', borderRadius: '20px', fontWeight: 600, border: '1px solid rgba(6, 182, 212, 0.3)' }}>
              PS-3 QUANT
            </span>
          </div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', margin: 0 }}>
            Autonomous Black-Litterman Portfolio Intelligence
          </p>
        </div>
      </div>

      {/* Center Macro Regime Badge */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <RegimeIndicator regime={regime} />
      </div>

      {/* Live NYSE Status Indicator & Archives - Right Side */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 14px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '20px', border: '1px solid rgba(16, 185, 129, 0.3)', boxShadow: '0 0 12px rgba(16, 185, 129, 0.15)' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#10b981' }} className="animate-pulse-slow" />
          <span style={{ fontSize: '0.8rem', color: '#10b981', fontWeight: 600 }}>NYSE Live Feeds Active</span>
        </div>

        <button 
          onClick={onOpenHistory}
          style={{
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(255,255,255,0.1)',
            color: 'var(--text-primary)',
            padding: '10px 16px',
            borderRadius: '10px',
            fontSize: '0.85rem',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'all 0.2s'
          }}
          onMouseOver={(e) => { e.currentTarget.style.background = 'rgba(255,255,255,0.1)'; }}
          onMouseOut={(e) => { e.currentTarget.style.background = 'rgba(255,255,255,0.05)'; }}
        >
          <Activity size={16} color="var(--accent-cyan)" />
          Strategy Archives
        </button>
      </div>
    </header>
  );
};

export default Navbar;
