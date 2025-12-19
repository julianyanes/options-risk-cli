import yfinance as yf
from datetime import datetime, timezone
import argparse

from bs import call_price, put_price, greeks, implied_vol
parser = argparse.ArgumentParser(
    description="Options Risk Card using Black-Scholes (IV + Greeks)"
)

parser.add_argument(
    "--ticker",
    type=str,
    default="SPY",
    help="Underlying ticker symbol (default: SPY)"
)

parser.add_argument(
    "--type",
    type=str,
    choices=["call", "put"],
    default="call",
    help="Option type: call or put (default: call)"
)

args = parser.parse_args()

ticker = args.ticker.upper()
option_type = args.type.lower()

r = 0.05

t = yf.Ticker(ticker)


hist = t.history(period="5d", interval="1d")
if hist.empty:
    raise RuntimeError("Could not fetch underlying price history.")
S = float(hist["Close"].iloc[-1])


exps = t.options
if not exps:
    raise RuntimeError("No options expirations returned.")
expiry = exps[0]

chain = t.option_chain(expiry)
df = chain.calls if option_type == "call" else chain.puts
df = df.copy()

df["dist"] = (df["strike"] - S).abs()
row = df.sort_values("dist").iloc[0]

K = float(row["strike"])
bid = float(row.get("bid", 0.0))
ask = float(row.get("ask", 0.0))
last = float(row.get("lastPrice", 0.0))

if bid > 0 and ask > 0:
    market_price = (bid + ask) / 2
elif last > 0:
    market_price = last
else:
    raise RuntimeError("No usable market price.")


exp_dt = (
    datetime.strptime(expiry, "%Y-%m-%d")
    .replace(tzinfo=timezone.utc, hour=21, minute=0, second=0)
)
now_dt = datetime.now(timezone.utc)

seconds_to_expiry = max((exp_dt - now_dt).total_seconds(), 1.0)

T = seconds_to_expiry / (365.0 * 24 * 3600)  # YEARS (primary)
days_to_expiry = seconds_to_expiry / (24 * 3600)
hours_to_expiry = seconds_to_expiry / 3600


iv = implied_vol(market_price, S, K, T, r, option_type)
g = greeks(S, K, T, r, iv, option_type)

theta_per_day = g["theta"] / 365.0
theta_per_hour = theta_per_day / 24
vega_per_1pct = g["vega"] * 0.01
shares_equiv = g["delta"] * 100

model_price = (
    call_price(S, K, T, r, iv)
    if option_type == "call"
    else put_price(S, K, T, r, iv)
)


print("\n=== OPTIONS RISK CARD ===")
print(f"Ticker: {ticker}")
print(f"Type: {option_type.upper()}")
print(f"Expiry: {expiry}")
print(f"Strike: {K}")
print(f"Underlying (S): {S:.2f}")
print(f"Market Price: {market_price:.2f}")
print(f"Model Price:  {model_price:.2f}")
print(f"Implied Vol:  {iv*100:.2f}%")

print("\nTime to Expiry:")
print(f"  T = {T:.6f} years")
print(f"    = {days_to_expiry:.2f} days")
print(f"    = {hours_to_expiry:.1f} hours")

print("\nGreeks (per 1 contract):")
print(f"  Delta: {g['delta']:.4f}  (~{shares_equiv:.1f} shares)")
print(f"  Gamma: {g['gamma']:.6f}")
print(f"  Theta: {theta_per_day:.4f} per day")
print(f"         {theta_per_hour:.4f} per hour")
print(f"  Vega : {vega_per_1pct:.4f} per +1% IV")
