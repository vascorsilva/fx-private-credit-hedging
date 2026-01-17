# Hedges/Forwards
import numpy as np
import pandas as pd

from src.metrics.performance import _yearfrac

def _forward_rates(
    s0: float,
    cashflow_dates: np.ndarray,
    r_domestic: float,
    r_foreign: float,
    start_date: pd.Timestamp = pd.Timestamp('2025-08-01'),
) -> np.ndarray:
    """
    Calculates forward rates for cashflow dates. Assumes a flat rate meaning that we don't use different 'r' for 
    different maturities. We reuse _yearfrac for different T.
    HULL Pg. 140

    FX Quote is EURUSD: how many USD per one unit of EUR
    r_domestic = USD
    r_foreign = EUR 
    """
    year_fractions = np.asarray([_yearfrac(start_date=pd.Timestamp(start_date), end_date=pd.Timestamp(date)) for date in cashflow_dates])
    
    forwards = s0 * np.exp((r_domestic - r_foreign) * year_fractions)

    return forwards

def forward_hedge_cashflows_usd(
        spot_paths: np.ndarray,
        path_dates: np.ndarray,
        cashflow_dates: pd.DatetimeIndex,
        cashflow_eur: np.ndarray,
        s0: float,
        r_domestic: float,
        r_foreign: float,
        hedge_ratio: float = 1.0,
        #n_paths: int,
        #n_steps: int,
        start_date: pd.Timestamp =  pd.Timestamp('2025-08-01')
) -> tuple[np.ndarray, np.ndarray]:
    """
    Uses Forward rates calculated at start_date ('2025-08-01' by default).
    Opted for returning payoffs along with forward rate used. i.e. payoff_i = CF_i x (F(0, T_i). - S_{T_i}).
    This only calculates forward rates for the positive cashdlows (i.e. the inital outflow isn't covered.)
    """
    forwards = _forward_rates(
        s0=s0,
        start_date=start_date,
        cashflow_dates=np.asarray(cashflow_dates),
        r_domestic=r_domestic,
        r_foreign=r_foreign)

    n_paths, n_steps = spot_paths.shape
    n_cashflows = cashflow_eur.size

    cashflow_dates_idx = path_dates.get_indexer(cashflow_dates, method='pad')
    hedge_cashflows_usd = np.zeros((n_paths, n_cashflows), dtype=float)


    for i in range(n_cashflows):
        cf_eur = cashflow_eur[i]

        # Skipping Initial Outflow
        if cf_eur <= 0:
            continue

        notional_eur = hedge_ratio * cf_eur

        spots_i = spot_paths[:, cashflow_dates_idx[i]]              # cashflow_dates_idx[i] is the index on the index array corresponding to the cashflow dates
                                                    # in the simulation path grid. spot_T has shape (n_paths, )

        forward_i = forwards[i]                     # scalar

        payoffs_i = notional_eur * (forward_i - spots_i)

        hedge_cashflows_usd[:, i] = payoffs_i

    return hedge_cashflows_usd, forwards



    
