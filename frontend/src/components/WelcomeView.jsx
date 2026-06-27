import React from 'react';
import './WelcomeView.css';

const WelcomeView = () => {
  return (
    <div className="welcome-view">
      <div className="welcome-hero">
        <h2 className="welcome-title">Next-Generation Quantitative Intelligence</h2>
        <p className="welcome-subtitle">
          Leverage institutional-grade algorithms to optimize your portfolio. 
          Powered by XGBoost alpha models, Hidden Markov regime detection, and Black-Litterman optimization.
        </p>
      </div>

      <div className="feature-grid">
        <div className="feature-card glass-panel">
          <div className="feature-icon icon-blue">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
          </div>
          <h3>Machine Learning Alpha</h3>
          <p>Gradient boosting models predict short-term expected returns based on technical and macroeconomic features.</p>
        </div>
        <div className="feature-card glass-panel">
          <div className="feature-icon icon-purple">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 20h.01"></path><path d="M7 20v-4"></path><path d="M12 20v-8"></path><path d="M17 20V8"></path><path d="M22 4v16"></path></svg>
          </div>
          <h3>Regime Detection</h3>
          <p>Hidden Markov Models dynamically adapt the strategy across Bull, Neutral, and Bear market conditions.</p>
        </div>
        <div className="feature-card glass-panel">
          <div className="feature-icon icon-green">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="16"></line><line x1="8" y1="12" x2="16" y2="12"></line></svg>
          </div>
          <h3>Black-Litterman Model</h3>
          <p>Blends algorithmic priors with your custom views to generate mean-variance optimal portfolio weights.</p>
        </div>
      </div>
      
      <div className="tech-stack glass-panel">
        <div className="tech-label">System Architecture Status</div>
        <div className="tech-nodes">
          <div className="node active">Data Pipeline</div>
          <div className="node-connector"></div>
          <div className="node active">Alpha Engine</div>
          <div className="node-connector"></div>
          <div className="node active">LLM Extraction</div>
          <div className="node-connector"></div>
          <div className="node active">Risk Engine</div>
        </div>
      </div>
    </div>
  );
};

export default WelcomeView;
