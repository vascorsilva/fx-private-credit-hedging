# Performance Metrics Module
import warnings

import numpy as np
import pandas as pd
from scipy.optimize import brentq

def _yearfrac(start_date: pd.Timestamp,
              end_date: pd.Timestamp
) -> float:
    """
    Insteaf of weight factors (Bacon et al.) we'll us yearfrac borrowed from MatLab.
    basis = 12 -> actual/365 (ISDA).
    https://www.mathworks.com/help/finance/yearfrac.html
    """
    return (end_date - start_date).days / 365.0

# Terminal Value
def terminal_value(cashflows: np.ndarray) -> float:
    cfs = np.asarray(cashflows)
    return float(cfs.sum())

# Internal Rate of Return
def irr(cashflow_dates: np.ndarray,
        cashflows: np.ndarray,
        start_date: pd.Timestamp = pd.Timestamp('2025-10-01'),
        brent_lims: tuple[float, float] = (-0.999, 10.0),
) -> np.ndarray:
    """
    Internal Rate of Return gives us the annualised rate, r, where NPV = 0.
    Akin to an annualised compound rate you would find in your bank account.
    If your funding rate falls below this value, then its not a good investment.
    """
    year_fractions = np.asarray([_yearfrac(start_date=pd.Timestamp(start_date), end_date=pd.Timestamp(date)) for date in cashflow_dates])

    def _npv(r: float
    ) -> float:
        return np.sum(cashflows / (1 + r) ** year_fractions)
    
    a, b = brent_lims
    
    # Condition for brent
    if np.sign(_npv(a)) == np.sign(_npv(b)):
        warnings.warn("No root found, brent condition f(a)•f(b) < 0 not satisfied.",
        category=UserWarning,
        stacklevel=2
        )
        return np.NaN
    
    return float(brentq(_npv, a, b))  

# Net Present Value
def npv(cashflow_dates: np.ndarray,
        cashflows: np.ndarray,
        r: float,
        start_date: pd.Timestamp = pd.Timestamp('2025-08-01')
) -> float:
    """
    Net Present Value created at start_date (2025-08-01 by default) vs. a given discount rate r.
    If negative then loosing money.
    """
    year_fractions = np.asarray([_yearfrac(start_date=start_date, end_date=date) for date in cashflow_dates])
    return np.sum(cashflows / (1 + r) ** year_fractions)

# Multiple on Invested Capital
def moic(cashflows: np.ndarray) -> float:
    """
    Multiple on Invest Capital is time agnostic, gives ratio of how much goes out and how much comes in.
    """
    inflows=cashflows[cashflows>0]
    outflows=cashflows[cashflows<0]
    return np.sum(inflows) / np.sum(np.abs(outflows))

#def dscr(cashflow_dates: pd.DatetimeIndex,
#        cashflows: np.ndarray,
#         origination_date: pd.Timestamp = pd.Timestamp('2025-10-01'),
#         maturity_date: pd.Timestamp = pd.Timestamp('2030-10-01')
#) -> np.ndarray:
#    """
#    Cushion coverin full debt payments each period. Assumes bullet like loan where interest payments
#    are made at irregular time periods and finalised withe a principal + interest payment at maturity.
#    """
#    principal = np.abs(cfs[pd.DatetimeIndex(cashflow_dates).get_indexer([pd.Timestamp(origination_date)])]).item()