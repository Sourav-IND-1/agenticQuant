import React from 'react';
import { RefreshCcw } from 'lucide-react';

const RebalancingTable = ({ actions, currentWeights, targetWeights }) => {
  if (!actions || actions.length === 0) return null;

  const getActionColor = (action) => {
    if (action.includes('BUY')) return '#34d399'; // green
    if (action.includes('SELL')) return '#f87171'; // red
    return '#f9fafb'; // white for HOLD
  };

  return (
    <div className="glass-panel" style={{ padding: '18px 20px', backgroundColor: '#111827' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
        <RefreshCcw size={16} color="#38bdf8" />
        <h3 style={{ fontSize: '0.95rem', margin: 0, color: '#f9fafb', fontWeight: 600 }}>Rebalancing Action Plan</h3>
      </div>
      
      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #374151', color: '#9ca3af', textAlign: 'left' }}>
              <th style={{ padding: '10px 8px', fontWeight: 500 }}>Stock</th>
              <th style={{ padding: '10px 8px', fontWeight: 500 }}>Current Weight</th>
              <th style={{ padding: '10px 8px', fontWeight: 500 }}>Target Weight</th>
              <th style={{ padding: '10px 8px', fontWeight: 500 }}>Action</th>
              <th style={{ padding: '10px 8px', fontWeight: 500 }}>Amount (USD)</th>
              <th style={{ padding: '10px 8px', fontWeight: 500 }}>Reason</th>
            </tr>
          </thead>
          <tbody>
            {actions.map((act, idx) => (
              <tr key={idx} style={{ borderBottom: '1px solid #1f2937' }}>
                <td style={{ padding: '12px 8px', color: '#f9fafb', fontWeight: 600 }}>{act.ticker}</td>
                <td style={{ padding: '12px 8px', color: '#d1d5db' }}>
                  {((currentWeights?.[act.ticker] || 0) * 100).toFixed(1)}%
                </td>
                <td style={{ padding: '12px 8px', color: '#d1d5db' }}>
                  {((targetWeights?.[act.ticker] || 0) * 100).toFixed(1)}%
                </td>
                <td style={{ padding: '12px 8px', color: getActionColor(act.action), fontWeight: 600 }}>
                  {act.action}
                </td>
                <td className="font-mono" style={{ padding: '12px 8px', color: '#d1d5db' }}>
                  ${act.dollar_amount.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                </td>
                <td style={{ padding: '12px 8px', color: '#9ca3af', fontSize: '0.8rem' }}>
                  {act.reason}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default RebalancingTable;
