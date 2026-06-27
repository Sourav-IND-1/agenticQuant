import React, { useState } from 'react';
import { Send, Loader2, ChevronRight } from 'lucide-react';

const TEMPLATES = [
  { label: 'Tech Growth · $50k · 1yr',       prompt: 'Allocate $50,000 across tech equities over 12 months. Bullish view on NVDA and MSFT.' },
  { label: 'Capital Preservation · $100k',    prompt: 'Conservative $100,000 portfolio. 6-month horizon. Minimize drawdown. Low volatility preference.' },
  { label: 'High-Beta Equities · $25k',        prompt: 'Aggressive allocation of $25,000. Maximize expected return. Bullish on NVDA, GOOGL, TSLA.' },
];

const ChatInput = ({ onSubmit, isLoading }) => {
  const [prompt, setPrompt] = useState('');

  const submit = (text) => {
    const t = text.trim();
    if (!t || isLoading) return;
    onSubmit(t);
  };

  return (
    <div className="card" style={{ padding: '16px 20px', marginBottom: '20px' }}>
      {/* Header row */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
        <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--t-0)' }}>
          Strategy Query
        </span>
        <span style={{ fontSize: '0.72rem', color: 'var(--t-2)' }}>
          Describe capital, horizon, risk tolerance, and asset views
        </span>
      </div>

      {/* Input + Submit */}
      <div style={{ display: 'flex', gap: '8px' }}>
        <input
          className="input"
          style={{ flex: 1, height: '38px' }}
          placeholder="e.g. Allocate $100k, moderate risk, 6-month horizon, bullish on NVDA and MSFT..."
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && submit(prompt)}
          disabled={isLoading}
        />
        <button
          className="btn btn-primary"
          onClick={() => submit(prompt)}
          disabled={!prompt.trim() || isLoading}
          style={{ minWidth: '100px', gap: '6px' }}
        >
          {isLoading ? (
            <><Loader2 size={13} style={{ animation: 'spin 0.8s linear infinite' }} /> Running…</>
          ) : (
            <><Send size={13} /> Analyse</>
          )}
        </button>
      </div>

      {/* Template pills */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '10px', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '0.7rem', color: 'var(--t-2)', marginRight: '2px' }}>Quick templates:</span>
        {TEMPLATES.map((t, i) => (
          <button
            key={i}
            className="pill"
            onClick={() => { setPrompt(t.prompt); submit(t.prompt); }}
            disabled={isLoading}
            style={{ opacity: isLoading ? 0.4 : 1 }}
          >
            {t.label}
            <ChevronRight size={11} />
          </button>
        ))}
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
};

export default ChatInput;
