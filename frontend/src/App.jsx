import React, { useState } from 'react';
import Navbar from './components/Navbar';
import MetricsBar from './components/MetricsBar';
import PortfolioInput from './components/PortfolioInput';
import Dashboard from './components/Dashboard';
import HistoryPanel from './components/HistoryPanel';
import WelcomeView from './components/WelcomeView';

function App() {
  const [regime, setRegime] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [briefData, setBriefData] = useState(null);
  const [quantResults, setQuantResults] = useState(null);

  const hasResults = quantResults !== null;

  const handlePromptSubmit = async (promptText) => {
    setIsLoading(true);
    
    try {
      const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
      // Try calling live FastAPI backend endpoints if available
      const analyzeRes = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: promptText })
      });
      
      if (analyzeRes.ok) {
        const data = await analyzeRes.json();
        if (data.regime) setRegime(data.regime);
        if (data.brief) setBriefData(data.brief);
        if (data.results) setQuantResults(data.results);
      } else {
        throw new Error("Backend offline fallback");
      }
    } catch (err) {
      // Intelligent mock simulation response for offline UI testing
      setTimeout(() => {
        const text = promptText.toLowerCase();
        const isBear = text.includes('conservative') || text.includes('drop');
        const newRegime = isBear ? 'Neutral' : 'Bull';
        setRegime(newRegime);
        
        // Parse holdings from prompt (e.g. "TCS.NS 50 shares at ₹3500" or "RELIANCE 10 shares")
        const holdingRegex = /([A-Z][A-Z0-9&-]+(?:\.NS)?)\s+(\d+)\s*shares?\s*(?:at|@|bought at)?\s*[₹$]?(\d+(?:\.\d+)?)/gi;
        const parsedHoldings = {};
        const currentWeightsMock = {};
        let totalValue = 0;
        let match;
        while ((match = holdingRegex.exec(promptText)) !== null) {
          const ticker = match[1].toUpperCase();
          const shares = parseInt(match[2]);
          const cost = parseFloat(match[3]);
          parsedHoldings[ticker] = { shares, avg_cost: cost };
          totalValue += shares * cost;
        }

        let cap = totalValue > 0 ? totalValue : 100000;
        const capMatch = promptText.match(/[₹$]?\s*(\d+(?:\.\d+)?)\s*(lakh|L|k|thousand|crore|Cr)?/i);
        if (capMatch && totalValue === 0) {
          let multiplier = 1;
          const unit = (capMatch[2] || '').toLowerCase();
          if (unit === 'lakh' || unit === 'l') multiplier = 100000;
          else if (unit === 'crore' || unit === 'cr') multiplier = 10000000;
          else if (unit === 'k' || unit === 'thousand') multiplier = 1000;
          cap = parseFloat(capMatch[1]) * multiplier;
        }

        // Build current weights from parsed holdings
        if (totalValue > 0) {
          for (const [t, h] of Object.entries(parsedHoldings)) {
            currentWeightsMock[t] = (h.shares * h.avg_cost) / totalValue;
          }
        }

        // Target weights from Black-Litterman mock (expanded universe)
        const targetWeights = text.includes('nvda') || text.includes('ai') ?
          { NVDA: 0.18, MSFT: 0.14, AMZN: 0.12, META: 0.10, GOOGL: 0.08, TSLA: 0.07, AAPL: 0.06, JPM: 0.05, V: 0.04, UNH: 0.04, GS: 0.03, XOM: 0.03, JNJ: 0.02, WMT: 0.02, KO: 0.02 } :
          text.includes('india') || text.includes('reliance') || text.includes('tcs') || text.includes('infy') ?
          { 'RELIANCE.NS': 0.20, 'TCS.NS': 0.15, 'INFY.NS': 0.12, 'HDFCBANK.NS': 0.10, AAPL: 0.08, MSFT: 0.08, GOOGL: 0.07, JPM: 0.05, V: 0.05, UNH: 0.04, XOM: 0.03, JNJ: 0.03 } :
          { AAPL: 0.12, GOOGL: 0.10, MSFT: 0.10, AMZN: 0.09, JPM: 0.08, V: 0.07, UNH: 0.07, META: 0.06, XOM: 0.06, JNJ: 0.05, WMT: 0.05, NVDA: 0.05, KO: 0.04, GS: 0.03, CVX: 0.03 };

        // Generate mock rebalancing actions by comparing weights
        const allTickers = new Set([...Object.keys(currentWeightsMock), ...Object.keys(targetWeights)]);
        const mockActions = [];
        for (const ticker of allTickers) {
          const currW = currentWeightsMock[ticker] || 0;
          const tgtW = targetWeights[ticker] || 0;
          const diffW = tgtW - currW;
          const dollarDiff = Math.abs(diffW * cap);

          if (tgtW < 0.001 && currW > 0) {
            mockActions.push({ ticker, action: 'SELL FULL', dollar_amount: Math.round(currW * cap), reason: 'Not in target portfolio' });
          } else if (diffW < -0.05) {
            mockActions.push({ ticker, action: 'SELL PARTIAL', dollar_amount: Math.round(dollarDiff), reason: `Overweight by ${Math.abs(diffW * 100).toFixed(1)}%` });
          } else if (diffW > 0.05) {
            mockActions.push({ ticker, action: 'BUY MORE', dollar_amount: Math.round(dollarDiff), reason: `Underweight by ${(diffW * 100).toFixed(1)}%` });
          } else if (currW > 0 || tgtW > 0) {
            mockActions.push({ ticker, action: 'HOLD', dollar_amount: Math.round(currW * cap), reason: 'Within 5% of target' });
          }
        }

        // Concentration risk flags
        const concRisk = Object.entries(currentWeightsMock).filter(([_, w]) => w > 0.30).map(([t]) => t);

        setBriefData({
          capital: cap,
          horizon_days: 180,
          risk_tolerance: isBear ? 'conservative' : 'aggressive',
          views: text.includes('nvda') || text.includes('ai') ? [
            { ticker: 'NVDA', expected_return: 0.22, type: 'absolute' },
            { ticker: 'MSFT', expected_return: 0.14, type: 'absolute' },
            { ticker: 'AMZN', expected_return: 0.16, type: 'absolute' },
            { ticker: 'META', expected_return: 0.12, type: 'absolute' }
          ] : text.includes('india') || text.includes('reliance') || text.includes('tcs') ? [
            { ticker: 'RELIANCE.NS', expected_return: 0.15, type: 'absolute' },
            { ticker: 'TCS.NS', expected_return: 0.13, type: 'absolute' },
            { ticker: 'INFY.NS', expected_return: 0.11, type: 'absolute' },
            { ticker: 'HDFCBANK.NS', expected_return: 0.10, type: 'absolute' }
          ] : [
            { ticker: 'AAPL', expected_return: 0.11, type: 'absolute' },
            { ticker: 'GOOGL', expected_return: 0.10, type: 'absolute' },
            { ticker: 'JPM', expected_return: 0.09, type: 'absolute' },
            { ticker: 'UNH', expected_return: 0.08, type: 'absolute' }
          ]
        });

        setQuantResults({
          weights: targetWeights,
          metrics: {
            expectedReturn: isBear ? 0.085 : 0.182,
            sharpeRatio: isBear ? 1.88 : 2.45,
            var95: isBear ? -0.018 : -0.034,
            maxDrawdown: isBear ? -0.045 : -0.088,
            capital: cap
          },
          portfolio_health: {
            health_score: Math.max(1, 10 - concRisk.length * 2),
            current_weights: currentWeightsMock,
            total_value: cap,
            concentration_risk: concRisk,
            correlation_warning: []
          },
          rebalancing_actions: mockActions,
          before_after_metrics: {
            before: { sharpe: 0.82, cvar_95: -0.038, max_drawdown: -0.22, diversification: Object.keys(currentWeightsMock).length > 3 ? 'Moderate' : 'Low' },
            after: { sharpe: isBear ? 1.88 : 2.45, cvar_95: isBear ? -0.018 : -0.021, max_drawdown: isBear ? -0.045 : -0.088, diversification: 'High' }
          },
          featureImportances: [
            { feature: 'MACD_signal', importance: 0.24 },
            { feature: 'MA20', importance: 0.18 },
            { feature: 'ADX', importance: 0.14 },
            { feature: 'Volume_change', importance: 0.11 },
            { feature: 'MA50', importance: 0.09 }
          ]
        });
      }, 800);
    } finally {
      setTimeout(() => setIsLoading(false), 850);
    }
  };

  return (
    <div className="app-container">
      <Navbar 
        regime={regime} 
        onOpenHistory={() => setIsHistoryOpen(true)} 
      />

      <PortfolioInput 
        onSubmit={handlePromptSubmit} 
        isLoading={isLoading} 
      />

      {hasResults ? (
        <>
          <MetricsBar metrics={quantResults.metrics} />

          <Dashboard 
            briefData={briefData} 
            quantResults={quantResults} 
          />
        </>
      ) : (
        <WelcomeView />
      )}

      <HistoryPanel 
        isOpen={isHistoryOpen} 
        onClose={() => setIsHistoryOpen(false)} 
        onSelectHistory={(item) => {
          setRegime(item.regime || 'Bull');
          if (item.expectedReturn) {
            setQuantResults(prev => ({
              ...(prev || {}),
              metrics: { ...(prev?.metrics || {}), expectedReturn: item.expectedReturn, sharpeRatio: item.sharpeRatio }
            }));
          }
        }}
      />
    </div>
  );
}

export default App;
