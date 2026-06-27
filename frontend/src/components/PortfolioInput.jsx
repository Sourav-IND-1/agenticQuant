import React, { useState } from 'react';
import { Send, Terminal, RefreshCw } from 'lucide-react';

const SUGGESTED_PROMPTS = [
  {
    label: "AI Tech Portfolio",
    prompt: "I hold AAPL 50 shares at $230, TSLA 20 shares at $250. I think AI stocks will boom next year. Aggressive risk. Don't sell more than 30% of my portfolio."
  },
  {
    label: "Diversified US",
    prompt: "I hold MSFT 30 shares at $430, JPM 40 shares at $200, XOM 60 shares at $110, JNJ 25 shares at $155. I want balanced diversification. Moderate risk."
  },
  {
    label: "Indian Market Focus",
    prompt: "I hold RELIANCE 100 shares at 2900, TCS 50 shares at 3800, INFY 80 shares at 1500. Bullish on Indian IT sector. Conservative risk."
  }
];

const PortfolioInput = ({ onSubmit, isLoading }) => {
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
          <Terminal size={16} color="#38bdf8" /> Analyze Existing Portfolio
        </h3>
        <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>
          Natural Language Portfolio Extraction
        </span>
      </div>

      <form onSubmit={handleFormSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <div style={{ position: 'relative', width: '100%' }}>
          <textarea
            className="glass-input"
            style={{ 
              width: '100%', 
              minHeight: '100px', 
              padding: '12px', 
              paddingRight: '40px', 
              fontSize: '0.92rem', 
              resize: 'vertical',
              boxSizing: 'border-box'
            }}
            placeholder="Tell us what you currently hold and what you expect. Example: I hold AAPL 50 shares at $150, TSLA 20 shares at $200. I think AI stocks will boom. Moderate risk."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={isLoading}
          />
          {prompt && !isLoading && (
            <button
              type="button"
              onClick={() => setPrompt('')}
              style={{ position: 'absolute', right: '12px', top: '12px', background: 'none', border: 'none', color: '#9ca3af', cursor: 'pointer', fontSize: '0.75rem' }}
            >
              Clear
            </button>
          )}
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button
            type="submit"
            disabled={!prompt.trim() || isLoading}
            style={{
              background: isLoading ? '#374151' : '#2563eb',
              color: '#ffffff',
              border: 'none',
              borderRadius: '6px',
              padding: '8px 24px',
              fontWeight: 500,
              fontSize: '0.9rem',
              cursor: isLoading || !prompt.trim() ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              transition: 'background 0.15s',
              opacity: !prompt.trim() && !isLoading ? 0.5 : 1
            }}
          >
            {isLoading ? (
              <>
                <RefreshCw size={16} style={{ animation: 'spin 1s linear infinite' }} />
                Extracting & Optimizing...
              </>
            ) : (
              <>
                Analyze & Rebalance
                <Send size={15} />
              </>
            )}
          </button>
        </div>
      </form>

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
              cursor: isLoading ? 'not-allowed' : 'pointer'
            }}
          >
            {item.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default PortfolioInput;
