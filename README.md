# AgenticQuant 📈🤖

> **Autonomous Black-Litterman Quantitative Portfolio Management for the Indian Market.**
> Built for Hackathon Problem Statement 3.

AgenticQuant bridges the gap between natural language and institutional-grade mathematics. It translates plain English investment intent into rigorously optimized, regime-aware portfolios drawn from the **Nifty 50 universe**.

---

## 🚀 The Solution: A 12-Step Autonomous Pipeline

AgenticQuant is not a chatbot with financial opinions. It is a mathematical engine orchestrated by an AI agent:

1. **User Input:** User states holdings and risk appetite in plain text.
2. **LLM Extraction:** A GroqAPI strict JSON-schema extracts Capital, Risk, and Views.
3. **Live Data Fetch:** Connects to Yahoo Finance (`yfinance`) for live Nifty 50 prices.
4. **Quant Context:** Calculates 60-day rolling correlation, Beta, and CAPM expected returns.
5. **XGBoost Inference:** 49 individual XGBoost Classifiers predict 10-day directional movement.
6. **Meta-Model Filtering:** A secondary layer filters out low-signal predictions to prevent AI hallucinations.
7. **HMM Regime Detection:** Hidden Markov Models analyze the `^NSEI` benchmark to classify the market (Bull/Neutral/Bear).
8. **Mathematical Validation:** Caps unrealistic user views based on historical asset volatility.
9. **Black-Litterman Optimization:** Blends CAPM market equilibrium + User Views + XGBoost Signals.
10. **Regime Constraints:** HMM restricts max weight (e.g., Bear market forces extreme diversification).
11. **Risk Profiling:** Computes Sharpe Ratio, Volatility, and CAGR instantaneously.
12. **Rebalancer Math:** Compares current holdings vs. target weights, generating precise ₹ Buy/Sell actions.

---

## 🧮 The Core Mathematics

AgenticQuant is driven by institutional-grade quantitative formulas at every step of the pipeline.

### 1. Capital Asset Pricing Model (CAPM)
Used to establish the baseline market equilibrium expected returns before any AI views are injected.
```math
E(R_i) = R_f + \beta_i(E(R_m) - R_f)
```
*Where `R_f` is the Risk-free rate (6.5% RBI repo) and `β_i` is the asset's volatility relative to the Nifty 50.*

### 2. Black-Litterman Posterior Expected Returns
Blends the CAPM market equilibrium with the XGBoost ML signals and User Views to create a mathematically sound posterior return vector.
```math
E[R] = [(\tau \Sigma)^{-1} + P^T \Omega^{-1} P]^{-1} [(\tau \Sigma)^{-1} \Pi + P^T \Omega^{-1} Q]
```
*Where `Π` is the CAPM prior, `P` is the view mapping matrix, `Q` is the view returns (XGBoost + LLM), and `Ω` represents the confidence (error term) of the views.*

### 3. Sharpe Ratio Optimization (Efficient Frontier)
Finds the exact portfolio weights that maximize risk-adjusted returns subject to HMM regime constraints.
```math
\max_w \frac{w^T E[R] - R_f}{\sqrt{w^T \Sigma w}}
```
*Subject to: `∑ w_i = 1` and regime-dynamic bounds `w_min ≤ w_i ≤ w_max` (e.g., Bear market forces extreme diversification by capping max weight).*

### 4. Hidden Markov Model (Regime Detection)
Dynamically detects the current market state using a Gaussian emission probability on the Nifty 50 variance.
```math
P(x_t | z_t = k) = \mathcal{N}(x_t | \mu_k, \Sigma_k)
```

### 5. XGBoost Objective Function (Log Loss)
The gradient-boosted trees predict the 10-day directional movement by minimizing the log-loss error, regularized by `Ω(f)` to prevent overfitting.
```math
\mathcal{L} = \sum [y_i \ln(p_i) + (1-y_i) \ln(1-p_i)] + \Omega(f)
```

---

## 🛠️ Technology Stack

**Frontend (UI/UX)**
- React.js + Vite (Blazing fast HMR)
- Custom CSS Glassmorphism aesthetic
- Recharts for interactive data visualization

**Backend (API & Logic)**
- FastAPI (Python) for asynchronous endpoints
- Supabase (PostgreSQL) for state management & history logging

**Quantitative Mathematics**
- PyPortfolioOpt (Black-Litterman & Efficient Frontier)
- NumPy & Pandas (Covariance matrices & heavy matrix operations)

**Machine Learning Engine**
- XGBoost (Gradient-boosted decision trees)
- hmmlearn (Hidden Markov Models)
- SHAP (TreeExplainer for Feature Attribution)

---

## ⚙️ Local Development Setup

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
Create a `.env` file in the `backend` directory:
```env
GROQ_API_KEY=your_key_here
SUPABASE_URL=your_url_here
SUPABASE_KEY=your_key_here
```
Run the server:
```bash
uvicorn main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 📊 Rigorous Validation (The Math Doesn't Lie)

Our predictive models are validated using **5-Fold Combinatorial Purged Cross-Validation (CPCV)** to eliminate look-ahead bias and temporal leakage.
- **16 Years of Data:** Trained on Nifty 50 data (2008–2024).
- **53%+ Directional Accuracy:** Statistically significant alpha relative to a random walk.
- **49 Independent Models:** Each stock has its own dedicated XGBoost classifier.
