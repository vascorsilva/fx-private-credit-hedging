# Set Up Global Variables
# Clean, Dataiku-style dataclass instead of JSON TOML

from dataclasses import dataclass, fields
import pandas as pd

@dataclass(frozen=True)
class GlobalVariables:

    # Data
    market_data_path: str = 'QuantResearch-CaseStudy-MarketData-25.xlsx'
    discount_rate: float = 0.05

    r_domestic: float = 0.0439 # SOFR as of 2025-08-01
    r_foreign: float = 0.01827 # €SRT as of 2025-08-01

    # Dates
    analysis_start_date: pd.Timestamp = pd.Timestamp('2025-08-01')
    
    # Stochastic Model
    spot_rate_model: str = 'GBM'
    use_zero_mu: bool = True
    use_implied_sigma: bool = False

    # Discretisation
    discretization_method: str = 'exact'          # TODO: tractable, no need for em or milstein

    # Simulations
    n_paths: int = 50000
    steps_per_year: int = 252                  # Historical data has 260-262 spot samples per year.
                                               # We use business days for ease (bdate_range)
    
    # Hedging
    hedging_ratio: float = 1.0
    premium: float = 0.0

    # Risk
    alpha: float = 0.95 # Quantile

    # Visualisations
    #colors: dict = dict('c1': '#659999',
    #                    'c2': '#f4791f')

    # TODO: transaciton costs
    
    def print_fields(self) -> None:
        for f in fields(self):
            value = getattr(self, f.name)
            print(f'{f.name}: {value}')