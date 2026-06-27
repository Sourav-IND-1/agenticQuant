import React from 'react';
import PortfolioPie from './PortfolioPie';
import ShapChart from './ShapChart';
import BacktestChart from './BacktestChart';
import RebalancingTable from './RebalancingTable';
import BeforeAfterMetrics from './BeforeAfterMetrics';
import { Target, ArrowUpRight, ArrowDownRight, HeartPulse, AlertTriangle } from 'lucide-react';

const Dashboard = ({ briefData, quantResults }) => {
  const views = briefData?.views || [];
  
  const health = quantResults?.portfolio_health || { health_score: 10, concentration_risk: [], correlation_warning: [] };
  const currentWeights = health.current_weights || {};
  const recommendedWeights = quantResults?.weights || {};
  const capital = health.total_value || quantResults?.metrics?.capital || 100000;

  const getHealthColor = (score) => {
    if (score >= 8) return '#34d399'; // green
    if (score >= 5) return '#fbbf24'; // yellow
    return '#f87171'; // red
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Portfolio Health Score Card */}
      <div className="glass-panel" style={{ padding: '18px 20px', backgroundColor: '#111827', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ 
            width: '48px', height: '48px', borderRadius: '50%', 
            border: `3px solid ${getHealthColor(health.health_score)}`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: getHealthColor(health.health_score), fontWeight: 'bold', fontSize: '1.2rem'
          }}>
            {health.health_score}
          </div>
          <div>
            <h3 style={{ margin: '0 0 4px 0', color: '#f9fafb', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <HeartPulse size={18} color={getHealthColor(health.health_score)} />
              Current Portfolio Health
            </h3>
            <p style={{ margin: 0, color: '#9ca3af', fontSize: '0.85rem' }}>
              Score out of 10 based on concentration and correlation risks.
            </p>
          </div>
        </div>
        
        {/* Warnings */}
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', maxWidth: '50%' }}>
          {health.concentration_risk?.map((t, i) => (
            <span key={`conc-${i}`} style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem', color: '#fbbf24', background: '#451a03', padding: '4px 8px', borderRadius: '4px' }}>
              <AlertTriangle size={12} /> {t} Concentration > 30%
            </span>
          ))}
          {health.correlation_warning?.map((pair, i) => (
            <span key={`corr-${i}`} style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.75rem', color: '#fbbf24', background: '#451a03', padding: '4px 8px', borderRadius: '4px' }}>
              <AlertTriangle size={12} /> {pair} High Correlation
            </span>
          ))}
        </div>
      </div>

      {/* Current vs Recommended Pie Charts */}
      <div style={{ minHeight: '340px' }}>
        <PortfolioPie 
          currentWeights={currentWeights} 
          recommendedWeights={recommendedWeights} 
          capital={capital} 
        />
      </div>

      {/* Rebalancing Recommendations Table */}
      <RebalancingTable 
        actions={quantResults?.rebalancing_actions} 
        currentWeights={currentWeights} 
        targetWeights={recommendedWeights} 
      />

      {/* Before vs After Metrics Cards */}
      <BeforeAfterMetrics 
        beforeMetrics={quantResults?.before_after_metrics?.before} 
        afterMetrics={quantResults?.before_after_metrics?.after} 
      />

      {/* 2-Column Visualizations Grid for SHAP & Market Views */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '20px' }}>
        <div style={{ minHeight: '340px' }}>
          <ShapChart featureImportances={quantResults?.featureImportances} />
        </div>
        
        <div className="glass-panel" style={{ padding: '18px 20px', backgroundColor: '#111827' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
            <Target size={16} color="#38bdf8" />
            <h3 style={{ fontSize: '0.95rem', margin: 0, color: '#f9fafb', fontWeight: 600 }}>Active Investor Views</h3>
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
      </div>

      {/* Full Width Backtest Simulation */}
      <div style={{ minHeight: '360px' }}>
        <BacktestChart backtestData={quantResults?.backtest} />
      </div>
    </div>
  );
};

export default Dashboard;
