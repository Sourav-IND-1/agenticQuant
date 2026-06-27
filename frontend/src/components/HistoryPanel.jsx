import React from 'react';
import { X, Clock, ArrowRight, Database } from 'lucide-react';

const DUMMY = [
  { id: '1', timestamp: '2026-06-27 14:30', prompt: 'Aggressive $100k tech growth portfolio focusing on NVDA and MSFT', regime: 'Bull',    expectedReturn: 0.165, sharpeRatio: 2.34 },
  { id: '2', timestamp: '2026-06-27 12:15', prompt: 'Conservative $250k capital preservation for 3 months',             regime: 'Neutral', expectedReturn: 0.072, sharpeRatio: 1.85 },
  { id: '3', timestamp: '2026-06-26 16:45', prompt: 'Balanced $50k portfolio expecting AAPL bounce',                    regime: 'Bull',    expectedReturn: 0.118, sharpeRatio: 1.95 },
];

const regimeBadge = (r) => {
  if (r === 'Bull')    return 'badge badge-green';
  if (r === 'Bear')    return 'badge badge-red';
  return 'badge badge-amber';
};

const HistoryPanel = ({ isOpen, onClose, history = [], onSelectHistory }) => {
  if (!isOpen) return null;
  const list = history.length ? history : DUMMY;

  return (
    <div className="drawer-overlay" onClick={onClose}>
      <div className="drawer" onClick={e => e.stopPropagation()}>

        {/* Header */}
        <div style={{ padding: '14px 20px', borderBottom: '1px solid var(--line-0)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Database size={14} color="var(--t-2)" />
            <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--t-0)' }}>Execution History</span>
            <span className="badge badge-zinc">{list.length} runs</span>
          </div>
          <button className="btn-icon btn" onClick={onClose}>
            <X size={15} />
          </button>
        </div>

        {/* Subtext */}
        <div style={{ padding: '10px 20px', borderBottom: '1px solid var(--line-0)' }}>
          <p style={{ fontSize: '0.75rem', color: 'var(--t-2)', lineHeight: '1.4' }}>
            Select a past run to restore portfolio weights, BL views, and backtest results.
          </p>
        </div>

        {/* List */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '12px 16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {list.map((item, idx) => (
            <div
              key={item.id ?? idx}
              onClick={() => { onSelectHistory?.(item); onClose(); }}
              style={{
                background: 'var(--bg-2)',
                border: '1px solid var(--line-1)',
                borderRadius: '6px',
                padding: '12px 14px',
                cursor: 'pointer',
                transition: 'border-color 0.12s, background 0.12s',
              }}
              onMouseOver={e => { e.currentTarget.style.borderColor = 'var(--line-2)'; e.currentTarget.style.background = '#202024'; }}
              onMouseOut={e  => { e.currentTarget.style.borderColor = 'var(--line-1)'; e.currentTarget.style.background = 'var(--bg-2)'; }}
            >
              {/* Top row */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.7rem', color: 'var(--t-2)', fontFamily: 'var(--font-mono)' }}>
                  <Clock size={11} /> {item.timestamp}
                </span>
                <span className={regimeBadge(item.regime)}>{item.regime}</span>
              </div>

              {/* Prompt */}
              <p style={{ fontSize: '0.8rem', color: 'var(--t-0)', margin: '0 0 10px 0', lineHeight: '1.45' }}>
                {item.prompt}
              </p>

              {/* Metrics */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px', borderTop: '1px solid var(--line-0)', paddingTop: '8px' }}>
                <div>
                  <span style={{ fontSize: '0.68rem', color: 'var(--t-2)', textTransform: 'uppercase' }}>Return </span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', fontWeight: 600, color: 'var(--green)' }}>
                    +{(item.expectedReturn * 100).toFixed(1)}%
                  </span>
                </div>
                <div>
                  <span style={{ fontSize: '0.68rem', color: 'var(--t-2)', textTransform: 'uppercase' }}>Sharpe </span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', fontWeight: 600, color: 'var(--t-0)' }}>
                    {item.sharpeRatio.toFixed(2)}
                  </span>
                </div>
                <ArrowRight size={13} color="var(--t-2)" style={{ marginLeft: 'auto' }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default HistoryPanel;
