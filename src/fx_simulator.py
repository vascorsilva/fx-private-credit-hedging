# FX Simulation Module
from typing import Optional, Literal

import pandas as pd
import numpy as np

def _make_rng(
        seed: Optional[int] = None
) -> np.random.Generator:
    return np.random.default_rng(seed)

def estimate_gbm_params(
        spots: pd.Series,
        steps_per_year: int,
        use_zero_mu: bool = True
) -> tuple[float, float]:
    spots = spots.dropna().sort_index()
    log_ret = np.log(spots).diff().dropna()
    dt = 1.0 / steps_per_year

    sigma = log_ret.std(ddof=1) / np.sqrt(dt)
    mu = log_ret.mean() / dt + 0.5 * sigma**2 if not use_zero_mu else 0.0

    return float(mu), float(sigma)

def simulate_gbm_paths(
        s0: float,
        mu: float,
        sigma: float,
        start: pd.Timestamp,
        end: pd.Timestamp,
        n_paths: int,
        steps_per_year: int,
        seed: Optional[int] = None,
        scheme: Literal['exact', 'em', 'milstein'] = 'exact'
) -> tuple[pd.DatetimeIndex, np.ndarray]:
    
    # Value Errors
    if n_paths <= 0:
        raise ValueError('n_paths muse be non-negative.')
    if sigma < 0:
        raise ValueError('sigma must be non-negative')
    if steps_per_year <= 0:
        raise ValueError('steps_per_year must be non-negative')
    
    scheme = scheme.lower() # TODO: check if discretisation necessary.

    rng = _make_rng(seed)

    dates = pd.bdate_range(start=start, end=end)     # Business Days 
    n_steps = len(dates)
    if n_steps < 2:
        raise ValueError('Date range must have at lease 2 business days.')

    dt = 1.0 / steps_per_year                                                   # GBM calibrated using daily samples (business days ~261)
    n_increments = n_steps - 1                                                  # incremenets will rep. this s.t. drift scales with dt and vol with sqrt(dt)
            
    z = rng.standard_normal(size=(n_paths, n_increments))                       # vectorize. generate all z at once

    if scheme == 'exact':
        increments = (mu - 0.5 * sigma **2) * dt + sigma * np.sqrt(dt) * z
        log_s = np.empty((n_paths, n_steps))                                    # avoid python loops, do one .cumsum(), numpy (C) trick from Higham
        log_s[:, 0] = np.log(s0)
        log_s[:, 1:] = log_s[:, [0]] + np.cumsum(increments, axis=1)                    #log_s[:, 1:].shape
        return dates, np.exp(log_s)
    
    paths = np.empty((n_paths, n_steps), dtype=float)

    if scheme == 'em':
        raise NotImplementedError('Eyler-Maruyama scheme not implemented - not needed. Use exact instead')
    
    if scheme == 'milstein':
        raise NotImplementedError('Milstein Scheme not implemented - not needed. Use exact instead.')
    
    