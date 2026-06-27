import React from 'react';
import { X, Clock, ArrowRight, ShieldCheck, Database } from 'lucide-react';

const HistoryPanel = ({ isOpen, onClose, history = [], onSelectHistory }) => {
  if (!isOpen) return null;

  const dummyHistory = [
    {
      id: '1',
      timestamp: '2026-06-27 14:30',
      prompt: 'Aggressive $100k tech growth portfolio focusing on NVDA and MSFT',
      regime: 'Bull',
      expectedReturn: 0.165,
      sharpeRatio: 2.34
    },
    {
      id: '2',
      timestamp: '2026-06-27 12:15',
      prompt: 'Conservative $250k capital preservation for 3 months',
      regime: 'Neutral',
      expectedReturn: 0.072,
      sharpeRatio: 1.85
    },
    {
      id: '3',
      timestamp: '2026-06-26 16:45',
      prompt: 'Balanced $50k portfolio expecting AAPL bounce',
      regime: 'Bull',
      expectedReturn: 0.118,
      sharpeRatio: 1.95
    }
  ];

  const displayList = history.length > 0 ? history : dummyHistory;

  return (
    <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)', zIndex: 100, display: 'flex', justifyContent: 'flex-end' }}>
      <div className="glass-panel" style={{ width: '100%', maxWidth: '480px', height: '100%', borderRadius: '16px 0 0 16px', display: 'flex', flexDirection: 'column', overflow: 'hidden', borderLeft: '1px solid var(--accent-blue)' }}>
        {/* Header */}
        <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Database size={20} color="var(--accent-cyan)" />
            <h3 style={{ fontSize: '1.2rem', margin: 0 }}>Strategy Archives</h3>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'rgba(255,255,255,0.05)', border: 'none', color: 'var(--text-secondary)', padding: '8px', borderRadius: '8px', cursor: 'pointer' }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '20px 24px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
            Click any past quantitative run to restore weights, Black-Litterman views, and walk-forward simulations.
          </p>

          {displayList.map((item, idx) => (
            <div
              key={item.id || idx}
              onClick={() => {
                if (onSelectHistory) onSelectHistory(item);
                onClose();
              }}
              className="glass-panel"
              style={{ padding: '16px', cursor: 'pointer', border: '1px solid rgba(255,255,255,0.06)', transition: 'all 0.2s' }}
              onMouseOver={(e) => { e.currentTarget.style.borderColor = 'var(--accent-blue)'; }}
              onMouseOut={(e) => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.06)'; }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600 }}>
                  <Clock size={12} /> {item.timestamp}
                </span>
                <span className={item.regime === 'Bull' ? 'badge-bull' : item.regime === 'Bear' ? 'badge-bear' : 'badge-neutral'} style={{ fontSize: '0.7rem', padding: '2px 8px', borderRadius: '12px', fontWeight: 700 }}>
                  {item.regime?.toUpperCase()}
                </span>
              </div>

              <p style={{ fontSize: '0.9rem', color: '#ffffff', margin: '0 0 12px 0', lineHeight: '1.4' }}>
                "{item.prompt}"
              </p>

              <div style={{ display: 'flex', alignItems: 'center', gap: '16px', borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: '10px' }}>
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Return: </span>
                  <span className="font-mono" style={{ fontSize: '0.85rem', color: 'var(--bull-green)', fontWeight: 700 }}>
                    +{(item.expectedReturn * 100).toFixed(1)}%
                  </span>
                </div>
                <div>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Sharpe: </span>
                  <span className="font-mono" style={{ fontSize: '0.85rem', color: '#ffffff', fontWeight: 700 }}>
                    {item.sharpeRatio.toFixed(2)}
                  </span>
                </div>
                <ArrowRight size={14} color="var(--accent-blue)" style={{ marginLeft: 'auto' }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default HistoryPanel;
