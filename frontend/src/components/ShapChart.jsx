import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { BarChart3, HelpCircle } from 'lucide-react';

const ShapChart = ({ featureImportances = [] }) => {
  const fallbackData = [
    { feature: 'MACD_signal', importance: 0.225 },
    { feature: 'MA20', importance: 0.161 },
    { feature: 'ADX', importance: 0.116 },
    { feature: 'Volume_change', importance: 0.103 },
    { feature: 'MA50', importance: 0.094 },
    { feature: 'RSI', importance: 0.082 }
  ];

  const rawData = featureImportances.length > 0 ? featureImportances : fallbackData;
  const chartData = rawData.slice(0, 6).map(item => ({
    name: item.feature,
    value: Math.round(item.importance * 1000) / 10
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <div className="glass-panel" style={{ padding: '10px 14px', border: '1px solid var(--accent-purple)' }}>
          <p style={{ margin: 0, fontWeight: 700, color: '#ffffff' }}>{payload[0].payload.name}</p>
          <p className="font-mono" style={{ margin: 0, color: 'var(--accent-purple)', fontSize: '0.9rem' }}>
            Contribution: {payload[0].value}%
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="glass-panel" style={{ padding: '20px', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
        <BarChart3 size={18} color="var(--accent-purple)" />
        <h3 style={{ fontSize: '1.05rem', margin: 0 }}>ML Alpha Drivers (SHAP / XGBoost)</h3>
        <span style={{ marginLeft: 'auto', fontSize: '0.75rem', background: 'rgba(139,92,246,0.15)', color: 'var(--accent-purple)', padding: '2px 8px', borderRadius: '12px' }}>
          Explainable AI
        </span>
      </div>

      <div style={{ flex: 1, minHeight: '260px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
            <XAxis type="number" unit="%" stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 12 }} />
            <YAxis dataKey="name" type="category" stroke="#64748b" tick={{ fill: '#f8fafc', fontSize: 12 }} width={90} />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
            <Bar dataKey="value" radius={[0, 6, 6, 0]} barSize={20}>
              {chartData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={index === 0 ? '#8b5cf6' : index === 1 ? '#a855f7' : index === 2 ? '#3b82f6' : '#06b6d4'} 
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default ShapChart;
