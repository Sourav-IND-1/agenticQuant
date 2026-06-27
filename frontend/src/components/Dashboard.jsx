import React from 'react';
import PortfolioPie from './PortfolioPie';
import ShapChart from './ShapChart';
import BacktestChart from './BacktestChart';
import { Target, Layers, ArrowUpRight, ArrowDownRight } from 'lucide-react';

const Dashboard = ({ briefData, quantResults }) => {
  const views = briefData?.views || [
    { ticker: 'NVDA', expected_return: 0.18, type: 'absolute' },
    { ticker: 'MSFT', expected_return: 0.12, type: 'absolute' },
    { ticker: 'AAPL', expected_return: 0.09, type: 'absolute' }
  ];

  const stockPrices = [
    { ticker: 'AAPL', price: '224.50', chg: '+1.42%', up: true },
    { ticker: 'MSFT', price: '452.10', chg: '+0.85%', up: true },
    { ticker: 'GOOGL', price: '182.30', chg: '-0.34%', up: false },
    { ticker: 'NVDA', price: '135.80', chg: '+3.65%', up: true },
    { ticker: 'XOM', price: '114.20', chg: '-0.12%', up: false },
    { ticker: 'JPM', price: '202.40', chg: '+0.45%', up: true }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Live Market Ticker Tape */}
      <div className="glass-panel" style={{ padding: '12px 20px', display: 'flex', alignItems: 'center', gap: '24px', overflowX: 'auto', whiteSpace: 'nowrap' }}>
        <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-cyan)', letterSpacing: '0.05em' }}>UNIVERSE PRICES:</span>
        {stockPrices.map((stk, idx) => (
          <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontWeight: 700, fontSize: '0.88rem' }}>{stk.ticker}</span>
            <span className="font-mono" style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>${stk.price}</span>
            <span className="font-mono" style={{ color: stk.up ? 'var(--bull-green)' : 'var(--bear-red)', fontSize: '0.8rem', display: 'flex', alignItems: 'center' }}>
              {stk.up ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />} {stk.chg}
            </span>
          </div>
        ))}
      </div>

      {/* Extracted Views & Goal Summary Banner */}
      <div className="glass-panel" style={{ padding: '20px 24px', background: 'linear-gradient(135deg, rgba(16,23,38,0.8), rgba(30,41,59,0.4))' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '14px' }}>
          <Target size={18} color="var(--accent-blue)" />
          <h3 style={{ fontSize: '1.05rem', margin: 0 }}>Extracted Black-Litterman Views (Q Vector)</h3>
        </div>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
          {views.map((v, i) => (
            <div key={i} style={{ background: 'rgba(59,130,246,0.1)', border: '1px solid rgba(59,130,246,0.3)', padding: '10px 16px', borderRadius: '12px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontWeight: 800, color: '#ffffff' }}>{v.ticker}</span>
              <span className="font-mono" style={{ color: 'var(--accent-cyan)', fontWeight: 700 }}>
                +{(v.expected_return * 100).toFixed(1)}%
              </span>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>{v.type}</span>
            </div>
          ))}
          {views.length === 0 && (
            <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No explicit subjective views extracted. Using CAPM prior equilibrium returns.</span>
          )}
        </div>
      </div>

      {/* 3-Column Visualizations Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px' }}>
        <div style={{ minHeight: '340px' }}>
          <PortfolioPie weights={quantResults?.weights} capital={briefData?.capital || quantResults?.metrics?.capital || 100000} />
        </div>
        <div style={{ minHeight: '340px' }}>
          <ShapChart featureImportances={quantResults?.featureImportances} />
        </div>
      </div>

      {/* Full Width Backtest Simulation */}
      <div style={{ minHeight: '360px' }}>
        <BacktestChart backtestData={quantResults?.backtest} />
      </div>
    </div>
  );
};

export default Dashboard;
