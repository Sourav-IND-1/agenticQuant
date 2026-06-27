import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { BarChart3 } from 'lucide-react';

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
        <div className="glass-panel" style={{ padding: '10px 14px', border: '1px solid #3b82f6', backgroundColor: '#1f2937' }}>
          <p style={{ margin: 0, fontWeight: 600, color: '#ffffff', fontSize: '0.9rem' }}>{payload[0].payload.name}</p>
          <p className="font-mono" style={{ margin: '4px 0 0 0', color: '#60a5fa', fontSize: '0.95rem' }}>
            Attribution Weight: {payload[0].value}%
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="glass-panel" style={{ padding: '20px', height: '100%', display: 'flex', flexDirection: 'column', backgroundColor: '#111827' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
        <BarChart3 size={18} color="#38bdf8" />
        <h3 style={{ fontSize: '1rem', margin: 0, color: '#f9fafb', fontWeight: 600 }}>Model Feature Attribution (XGBoost SHAP)</h3>
        <span style={{ marginLeft: 'auto', fontSize: '0.75rem', background: '#1e293b', color: '#93c5fd', padding: '2px 8px', borderRadius: '4px', border: '1px solid #334155' }}>
          Tree Shapley
        </span>
      </div>

      <div style={{ flex: 1, minHeight: '260px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
            <XAxis type="number" unit="%" stroke="#4b5563" tick={{ fill: '#9ca3af', fontSize: 12 }} />
            <YAxis dataKey="name" type="category" stroke="#4b5563" tick={{ fill: '#e5e7eb', fontSize: 12 }} width={100} />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.02)' }} />
            <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={18}>
              {chartData.map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={index === 0 ? '#2563eb' : index === 1 ? '#3b82f6' : index === 2 ? '#60a5fa' : '#93c5fd'} 
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
