import React from 'react';
import PortfolioPie from './PortfolioPie';
import ShapChart from './ShapChart';
import BacktestChart from './BacktestChart';
import { Target, ArrowUpRight, ArrowDownRight } from 'lucide-react';

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
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Live Market Ticker Tape */}
      <div className="glass-panel" style={{ padding: '12px 18px', display: 'flex', alignItems: 'center', gap: '24px', overflowX: 'auto', whiteSpace: 'nowrap', backgroundColor: '#111827' }}>
        <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#38bdf8', letterSpacing: '0.05em' }}>MARKET FEED:</span>
        {stockPrices.map((stk, idx) => (
          <div key={idx} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontWeight: 600, fontSize: '0.85rem', color: '#f9fafb' }}>{stk.ticker}</span>
            <span className="font-mono" style={{ color: '#d1d5db', fontSize: '0.85rem' }}>${stk.price}</span>
            <span className="font-mono" style={{ color: stk.up ? '#34d399' : '#f87171', fontSize: '0.8rem', display: 'flex', alignItems: 'center' }}>
              {stk.up ? <ArrowUpRight size={14} /> : <ArrowDownRight size={14} />} {stk.chg}
            </span>
          </div>
        ))}
      </div>

      {/* Extracted Views & Goal Summary Banner */}
      <div className="glass-panel" style={{ padding: '18px 20px', backgroundColor: '#111827' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
          <Target size={16} color="#38bdf8" />
          <h3 style={{ fontSize: '0.95rem', margin: 0, color: '#f9fafb', fontWeight: 600 }}>Active Investor Views (Black-Litterman Q Vector)</h3>
        </div>
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          {views.map((v, i) => (
            <div key={i} style={{ background: '#1f2937', border: '1px solid #374151', padding: '8px 14px', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontWeight: 600, color: '#ffffff', fontSize: '0.85rem' }}>{v.ticker}</span>
              <span className="font-mono" style={{ color: '#38bdf8', fontWeight: 600, fontSize: '0.85rem' }}>
                +{(v.expected_return * 100).toFixed(1)}%
              </span>
              <span style={{ fontSize: '0.7rem', color: '#9ca3af', textTransform: 'uppercase' }}>{v.type}</span>
            </div>
          ))}
          {views.length === 0 && (
            <span style={{ color: '#9ca3af', fontSize: '0.85rem' }}>No explicit subjective views extracted. Defaulting to equilibrium CAPM market priors.</span>
          )}
        </div>
      </div>

      {/* 2-Column Visualizations Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '20px' }}>
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
