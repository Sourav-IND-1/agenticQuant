import React, { useState, useEffect } from 'react';
import PortfolioPie from './PortfolioPie';
import ShapChart from './ShapChart';
import BacktestChart from './BacktestChart';
import { ArrowUpRight, ArrowDownRight, Filter, RefreshCw } from 'lucide-react';

/* Tickers shown in the feed bar (ordered by display preference) */
const FEED_TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'XOM', 'JPM', 'TSLA'];

const Dashboard = ({ briefData, quantResults }) => {
  const [prices, setPrices]     = useState({});
  const [fetchErr, setFetchErr] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);

  const loadPrices = async () => {
    try {
      const res = await fetch('/api/prices');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      if (json.prices) {
        setPrices(json.prices);
        setLastUpdated(new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }));
        setFetchErr(false);
      }
    } catch {
      setFetchErr(true);
    }
  };

  /* Fetch on mount, then every 60 s */
  useEffect(() => {
    loadPrices();
    const id = setInterval(loadPrices, 60_000);
    return () => clearInterval(id);
  }, []);

  const views   = briefData?.views ?? [
    { ticker: 'NVDA', expected_return: 0.18, type: 'absolute' },
    { ticker: 'MSFT', expected_return: 0.12, type: 'absolute' },
    { ticker: 'AAPL', expected_return: 0.09, type: 'absolute' },
  ];
  const capital = briefData?.capital ?? quantResults?.metrics?.capital ?? 100000;

  const hasPrices = Object.keys(prices).length > 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>

      {/* ── Market feed bar ─────────────────────────────────────────────── */}
      <div style={{
        background: '#0e0e10',
        border: '1px solid #1c1c1e',
        borderRadius: '6px',
        padding: '0 16px',
        display: 'flex',
        alignItems: 'center',
        gap: '0',
        overflowX: 'auto',
        height: '38px',
      }}>
        <span style={{ fontSize: '0.68rem', fontWeight: 600, color: '#52525b', textTransform: 'uppercase', letterSpacing: '0.06em', marginRight: '12px', whiteSpace: 'nowrap', flexShrink: 0 }}>
          Live Prices
        </span>

        {/* Error / loading state */}
        {fetchErr && (
          <span style={{ fontSize: '0.72rem', color: '#ef4444', fontFamily: 'var(--font-mono)', marginRight: '12px' }}>
            ⚠ Backend offline — prices unavailable
          </span>
        )}

        {!hasPrices && !fetchErr && (
          <span style={{ fontSize: '0.72rem', color: '#52525b', display: 'flex', alignItems: 'center', gap: '5px' }}>
            <RefreshCw size={11} style={{ animation: 'spin 1s linear infinite' }} /> Fetching…
          </span>
        )}

        {hasPrices && FEED_TICKERS.map((ticker, i) => {
          const d = prices[ticker];
          if (!d) return null;
          return (
            <React.Fragment key={ticker}>
              {i > 0 && (
                <span style={{ width: '1px', height: '14px', background: '#27272a', flexShrink: 0, margin: '0 12px' }} />
              )}
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', whiteSpace: 'nowrap', flexShrink: 0 }}>
                <span style={{ fontSize: '0.78rem', fontWeight: 700, color: '#fafafa' }}>{ticker}</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem', color: '#a1a1aa' }}>
                  ${d.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </span>
                <span style={{
                  fontFamily: 'var(--font-mono)', fontSize: '0.72rem',
                  color: d.up ? '#22c55e' : '#ef4444',
                  display: 'flex', alignItems: 'center', gap: '1px'
                }}>
                  {d.up ? <ArrowUpRight size={11} /> : <ArrowDownRight size={11} />}
                  {d.up ? '+' : ''}{d.change.toFixed(2)}%
                </span>
              </div>
            </React.Fragment>
          );
        })}

        {/* Last updated */}
        {lastUpdated && (
          <span style={{ marginLeft: 'auto', fontSize: '0.68rem', color: '#3f3f46', fontFamily: 'var(--font-mono)', paddingLeft: '12px', flexShrink: 0 }}>
            as of {lastUpdated}
          </span>
        )}
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

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
};

export default Dashboard;
