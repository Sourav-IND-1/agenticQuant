import React, { useState } from 'react';
import { Send, Sparkles, Terminal, RefreshCw } from 'lucide-react';

const SUGGESTED_PROMPTS = [
  {
    label: "🔥 Tech Growth Focus ($50k)",
    prompt: "Tech growth focus portfolio with $50k capital over 1 year. Bullish on NVDA and MSFT."
  },
  {
    label: "🛡️ Conservative Balanced ($100k)",
    prompt: "Conservative balanced portfolio with $100k capital preservation over 6 months with low volatility."
  },
  {
    label: "⚡ Aggressive AI Stocks ($25k)",
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
      <div style={{ marginTop: '16px', display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginRight: '4px', fontWeight: 600 }}>Suggested prompts:</span>
        {SUGGESTED_PROMPTS.map((item, index) => (
          <button
            key={index}
            type="button"
            onClick={() => handlePillClick(item)}
            disabled={isLoading}
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              color: 'var(--text-primary)',
              padding: '8px 16px',
              borderRadius: '24px',
              fontSize: '0.82rem',
              fontWeight: 500,
              cursor: isLoading ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s',
              boxShadow: '0 2px 10px rgba(0,0,0,0.2)',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
            onMouseOver={(e) => {
              if (!isLoading) {
                e.currentTarget.style.background = 'rgba(59, 130, 246, 0.2)';
                e.currentTarget.style.borderColor = 'var(--accent-cyan)';
                e.currentTarget.style.transform = 'translateY(-1px)';
              }
            }}
            onMouseOut={(e) => {
              if (!isLoading) {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                e.currentTarget.style.transform = 'translateY(0)';
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
