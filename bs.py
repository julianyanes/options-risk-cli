import math
from scipy.stats import norm

def _d1_d2(S, K, T, r, sigma):
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return d1, d2

def call_price(S, K, T, r, sigma):
    d1, d2 = _d1_d2(S, K, T, r, sigma)
    return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)

def put_price(S, K, T, r, sigma):
    d1, d2 = _d1_d2(S, K, T, r, sigma)
    return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

def greeks(S, K, T, r, sigma, option_type="call"):
    d1, _ = _d1_d2(S, K, T, r, sigma)
    pdf = norm.pdf(d1)

    delta = norm.cdf(d1) if option_type == "call" else norm.cdf(d1) - 1
    gamma = pdf / (S * sigma * math.sqrt(T))
    theta = -(S * pdf * sigma) / (2 * math.sqrt(T))
    vega = S * pdf * math.sqrt(T)

    return {
        "delta": delta,
        "gamma": gamma,
        "theta": theta,
        "vega": vega
    }

def implied_vol(price, S, K, T, r, option_type="call"):
    lo, hi = 1e-6, 5.0
    for _ in range(200):
        mid = (lo + hi) / 2
        model = call_price(S, K, T, r, mid) if option_type == "call" else put_price(S, K, T, r, mid)
        if model > price:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2
