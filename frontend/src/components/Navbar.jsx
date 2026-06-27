import React from 'react';
import { Activity, ShieldCheck, Zap, Globe } from 'lucide-react';
import RegimeIndicator from './RegimeIndicator';

const Navbar = ({ regime = 'Bull', lastUpdated = 'Just now', onOpenHistory }) => {
  return (
    <header className="glass-panel" style={{ padding: '16px 24px', marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      {/* Brand & Logo */}
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
            <h1 style={{ fontSize: '1.4rem', fontWeight: 800, letterSpacing: '-0.03em', background: 'linear-gradient(to right, #ffffff, #94a3b8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
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

      {/* Center Live Status */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        <RegimeIndicator regime={regime} />
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 14px', background: 'rgba(255,255,255,0.03)', borderRadius: '20px', border: '1px solid rgba(255,255,255,0.05)' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#10b981' }} className="animate-pulse-slow" />
          <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', fontWeight: 500 }}>NYSE Live Feeds Active</span>
        </div>
      </div>

      {/* Right Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
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
