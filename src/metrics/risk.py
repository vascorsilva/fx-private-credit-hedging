# Risk Metrics Module
import numpy as np

def _clean_1d(
    x: np.ndarray
) -> np.ndarray:
    x = np.asarray(x, dtype=float).ravel()
    x = x[np.isfinite(x)]
    return x

def summarise_distribution(
    x: np.ndarray
) -> dict:
    x = _clean_1d(x)
    if x.size == 0:
        return {'n': 0, 'mean': np.nan, 'std': np.nan, 'p05': np.nan, 'p50': np.nan, 'p95': np.nan}
    return {
        'n': int(x.size),
        'mean': float(np.mean(x)),
        'std': float(np.std(x, ddof=1)) if x.size > 1 else 0.0,
        'p05': float(np.quantile(x, 0.05)),
        'p50': float(np.quantile(x, 0.50)),
        'p95': float(np.quantile(x, 0.95)),
    }

def var_es(
    losses: np.ndarray,
    alpha: float = 0.95
) -> tuple[float, float]:
    """
    VaR and ES for losses.
    losses: higher = worse.
    """
    L = _clean_1d(losses)
    if L.size == 0:
        return np.nan, np.nan
    q = float(np.quantile(L, alpha))
    tail = L[L >= q]
    es = float(tail.mean()) if tail.size else float('nan')
    return q, es

def prob_below(
    x: np.ndarray,
    threshold: float = 0.0
) -> float:
    x = _clean_1d(x)
    return float((x < threshold).mean()) if x.size else float('nan')

def prob_above(
    x: np.ndarray,
    threshold: float = 0.0
) -> float:
    x = _clean_1d(x)
    return float((x > threshold).mean()) if x.size else float('nan')

def risk_summary_for_metric(
    metric: np.ndarray,
    alpha: float = 0.95,
    loss: str = 'negate'
) -> dict:
    """
    Returns distribution stats in metric space + VaR/ES on a well-defined LOSS variable.

    loss modes:
      - 'npv_shortfall'  : L = max(0, -NPV)      (USD downside only)
      - 'irr_shortfall'  : L = max(0, -IRR)      (rate downside only)
      - 'moic_shortfall' : L = max(0, 1 - MOIC)  (capital shortfall only)
      - 'none'           : do not compute VaR/ES (set to NaN)

    Notes:
      - VaR/ES are reported on L, and are always >= 0 for the *_shortfall modes.
      - Histogram vertical lines should use p05/p50/p95 from metric space, not VaR_loss.
    """
    m = _clean_1d(metric)
    out = summarise_distribution(m)

    # Default: no loss VaR/ES
    var_a = np.nan
    es_a = np.nan

    if m.size == 0:
        out.update({f'VaR{int(alpha*100)}_loss': var_a, f'ES{int(alpha*100)}_loss': es_a})
        return out

    if loss == 'npv_shortfall':
        L = np.maximum(0.0, -m)
        var_a, es_a = var_es(L, alpha=alpha)

    elif loss == 'irr_shortfall':
        L = np.maximum(0.0, -m)
        var_a, es_a = var_es(L, alpha=alpha)

    elif loss == 'moic_shortfall':
        L = np.maximum(0.0, 1.0 - m)
        var_a, es_a = var_es(L, alpha=alpha)

    elif loss == 'none':
        pass

    else:
        raise ValueError('loss must be one of: npv_shortfall, irr_shortfall, moic_shortfall, none')

    out.update({
        f'VaR{int(alpha*100)}_loss': float(var_a) if np.isfinite(var_a) else np.nan,
        f'ES{int(alpha*100)}_loss': float(es_a) if np.isfinite(es_a) else np.nan,
    })
    return out