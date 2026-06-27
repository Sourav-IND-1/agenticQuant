import React, { useState } from 'react';
import { Send, Sparkles, Terminal, RefreshCw } from 'lucide-react';

const SUGGESTED_PROMPTS = [
  "I have $100k for 6 months. Aggressive risk tolerance, very bullish on NVDA and MSFT.",
  "Invest $50k over 1 year with moderate risk. Expecting AAPL and GOOGL to outperform.",
  "Conservative $200k capital preservation portfolio for 3 months with low volatility.",
  "Aggressive $75k portfolio targeting tech surge in NVDA and JPM."
];

const ChatInput = ({ onSubmit, isLoading }) => {
  const [prompt, setPrompt] = useState('');

  const handleFormSubmit = (e) => {
    e.preventDefault();
    if (!prompt.trim() || isLoading) return;
    onSubmit(prompt);
  };

  const handlePillClick = (text) => {
    setPrompt(text);
    if (!isLoading) {
      onSubmit(text);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '24px', marginBottom: '24px', position: 'relative', overflow: 'hidden' }}>
      {/* Background glow effect */}
      <div style={{ position: 'absolute', top: '-50%', right: '-10%', width: '300px', height: '300px', background: 'radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%)', pointerEvents: 'none' }} />

      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
        <Sparkles size={18} color="var(--accent-cyan)" />
        <h3 style={{ fontSize: '1rem', color: 'var(--text-primary)', margin: 0 }}>
          Natural Language Investment Brief & NLP Extraction
        </h3>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Terminal size={14} /> Powered by Gemini AI & Black-Litterman
        </span>
      </div>

      <form onSubmit={handleFormSubmit} style={{ display: 'flex', gap: '12px', alignItems: 'stretch' }}>
        <div style={{ position: 'relative', flex: 1 }}>
          <input
            type="text"
            className="glass-input"
            style={{ paddingRight: '100px', fontSize: '1rem', background: 'rgba(6,9,17,0.7)' }}
            placeholder="Describe your capital, timeline, risk preference, and market views..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            disabled={isLoading}
          />
          {prompt && !isLoading && (
            <button
              type="button"
              onClick={() => setPrompt('')}
              style={{ position: 'absolute', right: '14px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '0.8rem' }}
            >
              Clear
            </button>
          )}
        </div>

        <button
          type="submit"
          disabled={!prompt.trim() || isLoading}
          style={{
            background: isLoading ? 'var(--bg-glass)' : 'linear-gradient(135deg, var(--accent-blue), var(--accent-cyan))',
            color: '#ffffff',
            border: 'none',
            borderRadius: '12px',
            padding: '0 28px',
            fontWeight: 700,
            fontSize: '0.95rem',
            cursor: isLoading || !prompt.trim() ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            boxShadow: isLoading ? 'none' : '0 0 20px rgba(6, 182, 212, 0.4)',
            transition: 'all 0.2s',
            opacity: !prompt.trim() && !isLoading ? 0.6 : 1
          }}
        >
          {isLoading ? (
            <>
              <RefreshCw size={18} className="animate-pulse-slow" style={{ animation: 'spin 1s linear infinite' }} />
              Optimizing...
            </>
          ) : (
            <>
              Execute Quant
              <Send size={16} />
            </>
          )}
        </button>
      </form>

      {/* Suggested Pills */}
      <div style={{ marginTop: '16px', display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginRight: '4px' }}>Suggested briefs:</span>
        {SUGGESTED_PROMPTS.map((pill, index) => (
          <button
            key={index}
            type="button"
            onClick={() => handlePillClick(pill)}
            disabled={isLoading}
            style={{
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              color: 'var(--text-secondary)',
              padding: '6px 12px',
              borderRadius: '20px',
              fontSize: '0.78rem',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s',
              textAlign: 'left',
              maxWidth: '350px',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis'
            }}
            onMouseOver={(e) => {
              if (!isLoading) {
                e.currentTarget.style.background = 'rgba(59, 130, 246, 0.15)';
                e.currentTarget.style.borderColor = 'var(--accent-blue)';
                e.currentTarget.style.color = '#ffffff';
              }
            }}
            onMouseOut={(e) => {
              if (!isLoading) {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.04)';
                e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.08)';
                e.currentTarget.style.color = 'var(--text-secondary)';
              }
            }}
          >
            {index === 0 && "🔥 "}
            {index === 1 && "📈 "}
            {index === 2 && "🛡️ "}
            {index === 3 && "⚡ "}
            {pill}
          </button>
        ))}
      </div>
    </div>
  );
};

export default ChatInput;
