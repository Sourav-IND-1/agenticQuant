import React, { useState } from 'react';
import { Send, Terminal, RefreshCw } from 'lucide-react';

const SUGGESTED_PROMPTS = [
  {
    label: "Tech Growth Strategy ($50k)",
    prompt: "Tech growth focus portfolio with $50k capital over 1 year. Bullish on NVDA and MSFT."
  },
  {
    label: "Capital Preservation ($100k)",
    prompt: "Conservative balanced portfolio with $100k capital preservation over 6 months with low volatility."
  },
  {
    label: "High-Beta Equities ($25k)",
    prompt: "Aggressive AI stocks portfolio with $25k capital targeting massive growth in NVDA and GOOGL."
  }
];

const ChatInput = ({ onSubmit, isLoading }) => {
  const [prompt, setPrompt] = useState('');

  const handleFormSubmit = (e) => {
    e.preventDefault();
    if (!prompt.trim() || isLoading) return;
    onSubmit(prompt);
  };

  const handlePillClick = (item) => {
    setPrompt(item.prompt);
    if (!isLoading) {
      onSubmit(item.prompt);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '20px', marginBottom: '20px', backgroundColor: '#111827' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
        <h3 style={{ fontSize: '0.95rem', color: '#f9fafb', fontWeight: 600, margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Terminal size={16} color="#38bdf8" /> Strategy Allocation Parameters
        </h3>
        <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>
          Natural Language Query Processing
        </span>
      </div>

      <form onSubmit={handleFormSubmit} style={{ display: 'flex', gap: '10px', alignItems: 'stretch' }}>
        <div style={{ position: 'relative', flex: 1 }}>
          <input
            type="text"
            className="glass-input"
            style={{ paddingRight: '70px', fontSize: '0.92rem' }}
            placeholder="Enter capital constraints, risk tolerance, and asset views (e.g., '$100k budget, conservative risk, bullish on NVDA')..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={isLoading}
          />
          {prompt && !isLoading && (
            <button
              type="button"
              onClick={() => setPrompt('')}
              style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: '#9ca3af', cursor: 'pointer', fontSize: '0.75rem' }}
            >
              Clear
            </button>
          )}
        </div>

        <button
          type="submit"
          disabled={!prompt.trim() || isLoading}
          style={{
            background: isLoading ? '#374151' : '#2563eb',
            color: '#ffffff',
            border: 'none',
            borderRadius: '6px',
            padding: '0 20px',
            fontWeight: 500,
            fontSize: '0.9rem',
            cursor: isLoading || !prompt.trim() ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'background 0.15s',
            opacity: !prompt.trim() && !isLoading ? 0.5 : 1
          }}
          onMouseOver={(e) => { if (!isLoading && prompt.trim()) e.currentTarget.style.background = '#1d4ed8'; }}
          onMouseOut={(e) => { if (!isLoading && prompt.trim()) e.currentTarget.style.background = '#2563eb'; }}
        >
          {isLoading ? (
            <>
              <RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} />
              Running...
            </>
          ) : (
            <>
              Run Model
              <Send size={15} />
            </>
          )}
        </button>
      </form>

      {/* Suggested Pills */}
      <div style={{ marginTop: '14px', display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '0.75rem', color: '#6b7280', marginRight: '4px' }}>Templates:</span>
        {SUGGESTED_PROMPTS.map((item, index) => (
          <button
            key={index}
            type="button"
            onClick={() => handlePillClick(item)}
            disabled={isLoading}
            style={{
              background: '#1f2937',
              border: '1px solid #374151',
              color: '#d1d5db',
              padding: '6px 12px',
              borderRadius: '6px',
              fontSize: '0.8rem',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              transition: 'all 0.15s'
            }}
            onMouseOver={(e) => {
              if (!isLoading) {
                e.currentTarget.style.background = '#374151';
                e.currentTarget.style.color = '#ffffff';
              }
            }}
            onMouseOut={(e) => {
              if (!isLoading) {
                e.currentTarget.style.background = '#1f2937';
                e.currentTarget.style.color = '#d1d5db';
              }
            }}
          >
            {item.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default ChatInput;
