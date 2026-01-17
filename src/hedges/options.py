# Hedges/Options

import numpy as np
import pandas as pd
from scipy.stats import norm

from src.metrics.performance import _yearfrac
from src.hedges.forwards import _forward_rates

def _interpolate_atm_vol(
    tau: float,
    vol_1y: float,
    vol_5y: float,
) -> float:
    """
    Inerpolates ATM VOL for date between 1Y and 5Y
    """
    if tau <= 1.0:
        return float(vol_1y)
    if tau >= 5.0:
        return float(vol_5y)
    w = (tau - 1.0) / (5.0 - 1.0)
    return float((1.0 - w) * vol_1y + w * vol_5y)

def _garman_kohlhagen_put(
    s0: float,
    K: float,
    r_domestic: float,
    r_foreign: float,
    tau: float,
    vol: float,
) -> float:
    """
    FX Put Option
    Garman and Kohlhagen Black Scholes adaptation to FX Options.
    """
    if tau <= 0.0:
        return float(max(K - s0, 0.0))

    forward = s0 * np.exp((r_domestic - r_foreign) * tau)
    df_d = np.exp(-r_domestic * tau)

    if vol <= 0.0:
        return float(df_d * max(K - forward, 0.0))

    sqrt_t = np.sqrt(tau)
    d1 = (np.log(forward / K) + 0.5 * vol * vol * tau) / (vol * sqrt_t)
    d2 = d1 - vol * sqrt_t

    put_price = df_d * (K * norm.cdf(-d2) - forward * norm.cdf(-d1))
    return float(put_price)


def put_option_hedge_cashflows_usd(
    spot_paths: np.ndarray,
    path_dates: np.ndarray,
    cashflow_dates: pd.DatetimeIndex,
    cashflow_eur: np.ndarray,
    s0: float,
    r_domestic: float,
    r_foreign: float,
    #n_paths: int,
    #n_steps: int,
    vol_1y: float,
    vol_5y: float,
    hedge_ratio: float,
    start_date: pd.Timestamp = pd.Timestamp('2025-08-01'),
) -> tuple[np.ndarray, float, np.ndarray, np.ndarray]:
    """
    ATMF put hedge (EUR pur / US) for cashflows using interpolated atm vols
    premium payed at start_date
    """ 
    n_paths, n_steps = spot_paths.shape
    n_cashflows = cashflow_eur.size

    path_dates = pd.DatetimeIndex(path_dates)
    cashflow_dates_idx = path_dates.get_indexer(cashflow_dates, method='pad')

    # TODO: WARNING TO CHECK DATES WITHING PERIOD

    # Forward Rates and ATMF Strike
    year_fractions = np.array([_yearfrac(start_date=pd.Timestamp(start_date), end_date=date) for date in cashflow_dates], dtype=float)
    forwards = _forward_rates(
        s0=s0,
        cashflow_dates=np.asarray(cashflow_dates),
        r_domestic=r_domestic,
        r_foreign=r_foreign,
        start_date=pd.Timestamp(start_date)
    )
    strikes = np.full(n_cashflows, np.nan, dtype=float)
    vols_used = np.full(n_cashflows, np.nan, dtype=float)
    hedge_cashflow_usd = np.zeros((n_paths, n_cashflows), dtype=float)
    premium = 0.0

    for i in range(n_cashflows):
        cf_eur = cashflow_eur[i]

        if cf_eur <= 0:
            continue

        notional_eur = hedge_ratio * cf_eur
        
        tau = float(year_fractions[i])
        
        sigma = _interpolate_atm_vol(tau=tau, vol_1y=vol_1y, vol_5y=vol_5y)
        K = float(forwards[i])
        
        strikes[i] = K # <--- ATMF Strikes
        vols_used[i] = sigma

        # Premium per eur_notional in USD 
        premium_per_eur = _garman_kohlhagen_put(
            s0=s0,
            K=K,
            tau=tau,
            r_domestic=r_domestic,
            r_foreign=r_foreign,
            vol=float(sigma)
        )
        premium += notional_eur * premium_per_eur

        spots_i = spot_paths[:, cashflow_dates_idx[i]]
        
        payoffs_i = notional_eur * np.maximum(K - spots_i, 0.0)

        hedge_cashflow_usd[:, i] = payoffs_i

    return hedge_cashflow_usd, float(premium), strikes, vols_used