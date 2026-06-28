# AgenticQuant 📈🤖

> **Autonomous Black-Litterman Quantitative Portfolio Management for the Indian Market.**
> Built for Hackathon Problem Statement 3.

AgenticQuant bridges the gap between natural language and institutional-grade mathematics. It translates plain English investment intent into rigorously optimized, regime-aware portfolios drawn from the **Nifty 50 universe**.

![AgenticQuant Cover](https://via.placeholder.com/1200x600.png?text=AgenticQuant+-+AI+Driven+Portfolio+Optimization)

---

## 🚀 The Solution: A 12-Step Autonomous Pipeline

AgenticQuant is not a chatbot with financial opinions. It is a mathematical engine orchestrated by an AI agent:

1. **User Input:** User states holdings and risk appetite in plain text.
2. **LLM Extraction:** Gemini 1.5 Pro / Groq strict JSON-schema extracts Capital, Risk, and Views.
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

---

*Made with ❤️ for the Hackathon.*
