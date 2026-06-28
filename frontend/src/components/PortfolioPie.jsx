import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { PieChart as PieIcon, IndianRupee } from 'lucide-react';

const COLORS = ['#2563eb', '#38bdf8', '#6366f1', '#10b981', '#f59e0b', '#ec4899', '#64748b'];

const PortfolioPie = ({ currentWeights = {}, recommendedWeights = {}, capital = 100000 }) => {
  const formatData = (weightsObj) => {
    return Object.entries(weightsObj)
      .filter(([_, weight]) => weight > 0.001)
      .map(([key, weight]) => {
        const exactAmount = Math.round(weight * capital);
        return {
          name: key,
          value: exactAmount,
          weightPct: (weight * 100).toFixed(1),
          formattedAmount: exactAmount.toLocaleString('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 })
        };
      })
      .sort((a, b) => b.value - a.value);
  };

  const currentData = formatData(currentWeights);
  const recommendedData = formatData(recommendedWeights);

  const totalAllocated = currentData.reduce((sum, item) => sum + item.value, 0) || recommendedData.reduce((sum, item) => sum + item.value, 0);
  const totalFormatted = totalAllocated.toLocaleString('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 });

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="glass-panel" style={{ padding: '10px 14px', border: '1px solid #2563eb', backgroundColor: '#1f2937' }}>
          <p style={{ margin: 0, fontWeight: 600, color: '#ffffff', fontSize: '0.9rem' }}>{item.name}</p>
          <p className="font-mono" style={{ margin: '4px 0 2px 0', color: '#38bdf8', fontSize: '1rem', fontWeight: 600 }}>
            Allocation: {item.formattedAmount}
          </p>
          <span style={{ fontSize: '0.75rem', color: '#9ca3af' }}>{item.weightPct}% of total budget</span>
        </div>
      );
    }
    return null;
  };

  const renderPie = (data, title) => (
    <div style={{ flex: '1 1 50%', minWidth: '300px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
      <h4 style={{ color: '#9ca3af', margin: '0 0 8px 0', fontSize: '0.85rem', textTransform: 'uppercase' }}>{title}</h4>
      <div style={{ width: '100%', height: '220px', position: 'relative' }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data.length > 0 ? data : [{name: 'Cash', value: capital, weightPct: '100.0', formattedAmount: capital}]}
              cx="50%"
              cy="50%"
              innerRadius={50}
              outerRadius={80}
              paddingAngle={3}
              dataKey="value"
            >
              {(data.length > 0 ? data : [{name: 'Cash'}]).map((entry, index) => (
                <Cell key={`cell-${index}`} fill={data.length > 0 ? COLORS[index % COLORS.length] : '#374151'} stroke="#111827" strokeWidth={2} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center', pointerEvents: 'none' }}>
          <div style={{ fontSize: '0.7rem', color: '#9ca3af', textTransform: 'uppercase' }}>Assets</div>
          <div className="font-mono" style={{ fontSize: '1.25rem', fontWeight: 700, color: '#ffffff' }}>{data.length || 0}</div>
        </div>
      </div>
      <div style={{ width: '100%', display: 'flex', gap: '4px', flexWrap: 'wrap', justifyContent: 'center', marginTop: '8px' }}>
        {data.map((item, idx) => (
          <div key={idx} style={{ fontSize: '0.75rem', color: '#d1d5db', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: COLORS[idx % COLORS.length] }}></div>
            {item.name} ({item.weightPct}%)
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="glass-panel" style={{ padding: '20px', height: '100%', display: 'flex', flexDirection: 'column', backgroundColor: '#111827' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
        <PieIcon size={18} color="#38bdf8" />
        <h3 style={{ fontSize: '1rem', margin: 0, color: '#f9fafb', fontWeight: 600 }}>Allocation Comparison</h3>
        <span style={{ marginLeft: 'auto', fontSize: '0.75rem', background: '#1e293b', color: '#93c5fd', padding: '4px 10px', borderRadius: '4px', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 500, border: '1px solid #334155' }}>
          <IndianRupee size={12} /> Total: {totalFormatted}
        </span>
      </div>

      <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', minHeight: '280px' }}>
        {renderPie(currentData, "Current Portfolio")}
        {renderPie(recommendedData, "Recommended Portfolio")}
      </div>
    </div>
  );
};

export default PortfolioPie;
