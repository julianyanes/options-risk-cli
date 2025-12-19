# Options Risk Card (Black–Scholes IV + Greeks)

A small Python tool that pulls live option chain data for **SPY/QQQ** and prints a clean “risk card”:
market mid price, implied volatility (solved), and Black–Scholes Greeks (delta/gamma/theta/vega).

This is **not a trading bot** and does not predict price. It’s a risk/exposure tool to understand what you’re actually holding.

## What it does
- Fetches underlying price + option chain (via `yfinance`)
- Selects the **nearest expiration** and the **ATM strike** (closest strike to spot)
- Uses market **mid price** (bid/ask) when available
- Solves **implied volatility** by inverting Black–Scholes
- Computes Greeks and prints trader-friendly units (years + days/hours to expiry)

## Files
- `options_risk.py` — main script (data fetch + risk card output)
- `bs.py` — Black–Scholes pricing + Greeks + implied volatility solver
- `requirements.txt` — dependencies

## Setup (Windows)
```bat
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
