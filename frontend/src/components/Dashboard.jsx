import React from 'react';
import PortfolioPie from './PortfolioPie';
import ShapChart from './ShapChart';
import BacktestChart from './BacktestChart';
import { ArrowUpRight, ArrowDownRight, Filter } from 'lucide-react';

const FEED = [
  { t: 'AAPL',  p: '224.50', chg: '+1.42',  up: true  },
  { t: 'MSFT',  p: '452.10', chg: '+0.85',  up: true  },
  { t: 'GOOGL', p: '182.30', chg: '−0.34',  up: false },
  { t: 'NVDA',  p: '135.80', chg: '+3.65',  up: true  },
  { t: 'XOM',   p: '114.20', chg: '−0.12',  up: false },
  { t: 'JPM',   p: '202.40', chg: '+0.45',  up: true  },
  { t: 'TSLA',  p: '176.90', chg: '+1.20',  up: true  },
];

const Dashboard = ({ briefData, quantResults }) => {
  const views = briefData?.views ?? [
    { ticker: 'NVDA', expected_return: 0.18, type: 'absolute' },
    { ticker: 'MSFT', expected_return: 0.12, type: 'absolute' },
    { ticker: 'AAPL', expected_return: 0.09, type: 'absolute' },
  ];
  const capital = briefData?.capital ?? quantResults?.metrics?.capital ?? 100000;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>

      {/* ── Market feed bar ─────────────────────────────────────────────── */}
      <div style={{
        background: '#0e0e10',
        border: '1px solid #1c1c1e',
        borderRadius: '6px',
        padding: '8px 16px',
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
        overflowX: 'auto',
      }}>
        <span style={{ fontSize: '0.68rem', fontWeight: 600, color: 'var(--t-2)', textTransform: 'uppercase', letterSpacing: '0.06em', marginRight: '8px', whiteSpace: 'nowrap' }}>
          Live Universe
        </span>
        {FEED.map((s, i) => (
          <React.Fragment key={i}>
            {i > 0 && <span style={{ width: '1px', height: '14px', background: '#27272a', flexShrink: 0, margin: '0 8px' }} />}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', whiteSpace: 'nowrap' }}>
              <span style={{ fontSize: '0.78rem', fontWeight: 700, color: '#fafafa' }}>{s.t}</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem', color: 'var(--t-1)' }}>${s.p}</span>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem', color: s.up ? 'var(--green)' : 'var(--red)', display: 'flex', alignItems: 'center', gap: '1px' }}>
                {s.up ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />}{s.chg}%
              </span>
            </div>
          </React.Fragment>
        ))}
      </div>

      {/* ── Extracted investor views ─────────────────────────────────────── */}
      <div className="card" style={{ padding: '14px 16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
          <Filter size={13} color="var(--t-2)" />
          <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--t-0)' }}>
            Black-Litterman Views (Q Vector)
          </span>
          <span style={{ fontSize: '0.7rem', color: 'var(--t-2)', marginLeft: 'auto' }}>
            {views.length} subjective view{views.length !== 1 ? 's' : ''} extracted via NLP
          </span>
        </div>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {views.length === 0 && (
            <span style={{ fontSize: '0.8rem', color: 'var(--t-2)' }}>
              No explicit views extracted — defaulting to equilibrium CAPM priors.
            </span>
          )}
          {views.map((v, i) => {
            const pos = v.expected_return >= 0;
            return (
              <div key={i} style={{
                display: 'flex', alignItems: 'center', gap: '8px',
                padding: '5px 12px',
                background: 'var(--bg-2)',
                border: `1px solid ${pos ? 'var(--green-bd)' : 'var(--red-bd)'}`,
                borderRadius: '5px',
              }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', fontWeight: 700, color: '#fafafa' }}>{v.ticker}</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: pos ? 'var(--green)' : 'var(--red)' }}>
                  {pos ? '+' : ''}{(v.expected_return * 100).toFixed(1)}%
                </span>
                <span style={{ fontSize: '0.65rem', color: 'var(--t-2)', textTransform: 'uppercase' }}>{v.type}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── 2-col charts ─────────────────────────────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div style={{ minHeight: '320px' }}>
          <PortfolioPie weights={quantResults?.weights} capital={capital} />
        </div>
        <div style={{ minHeight: '320px' }}>
          <ShapChart featureImportances={quantResults?.featureImportances} />
        </div>
      </div>

      {/* ── Full-width backtest ───────────────────────────────────────────── */}
      <div style={{ minHeight: '320px' }}>
        <BacktestChart backtestData={quantResults?.backtest} />
      </div>
    </div>
  );
};

export default Dashboard;
