# Data Loader Module
from typing import Optional
import warnings

import numpy as np
import pandas as pd

def _clean_level_one_col(
        column: str
) -> str:
        col = column.lower()
        for _old, _new in [('eurusd', ''),
                           ('δ', ''),
                           ('risk reveral', 'rr'),
                           ('butterfly', 'bf'),
                           ('implied vol', 'vol'),
                           ('spot rate', 'spot'),
                           (' ', '_')]:
                col = col.replace(_old, _new)
        col = col.strip('_')
        return col

def _clean_level_two_col(
        column: str
) -> str:
        col = column.lower()
        col = col.replace('px_', '')
        return col
        
def market_data_loader(
        path: str,
        sheet_name: Optional[str] = 'Sheet1'
) -> pd.DataFrame:
        df = pd.read_excel(
                path,
                header=[0, 2],
                sheet_name=sheet_name)
        df.set_index(df.columns[0], inplace=True)
        
        df.index.rename('dates', inplace=True)
        
        df.columns = [
                f'{_clean_level_one_col(level_1_col)}_{_clean_level_two_col(level_2_col)}'
                for level_1_col, level_2_col in df.columns
        ]

        df = df.dropna(subset=[f'spot_{px}' for px in ('ask', 'mid', 'bid')])
        df = df.dropna(subset=[f'spot_mid'])
        return df

def cashflows_loader(
        *,
        premium_usd: Optional[float] = None,
        analysis_date: Optional[pd.Timestamp] = None,
) -> pd.DataFrame:
        """
        Generates private credit cashflows.
        if premium_usd is provided, then preprends the upfront USD payments (for Option)
        """
        # Cashflows as is
        df = pd.DataFrame(
                index=pd.DatetimeIndex(['2025-10-01', '2026-10-01', '2027-10-01', '2029-10-01', '2030-10-01']),
                data=np.array([-10.0, 1.0, 1.0, 1.0, 11.0])*10**6,
                columns=['cf_eur'])
        df.index.rename('date', inplace=True)
        
        # Augmented Cashflows
        if premium_usd is not None:
                if analysis_date is None:
                        raise ValueError('analysis_date must be provided.')

                premium_row = pd.DataFrame(
                        index=pd.DatetimeIndex([analysis_date]),
                        data={'cf_usd': [-float(premium_usd)]},
                )

                df = (df.assign(cf_usd=np.nan)
                        .pipe(lambda x: pd.concat([premium_row, x]))
                        .sort_index()
                )
        
        return df

def get_spot_prices(
        market_data: pd.DataFrame,
        price: str = 'mid'
) -> pd.Series:
        """
        Returns spot prices. Mid by default.
        """
        df = market_data
        return df[f'spot_{price}']

def get_latest_quote(
        market_data: pd.DataFrame,
        price: Optional[str] = None,
        analysis_start_date: Optional[pd.Timestamp] = None,
        ticker: Optional[str] = None
) -> pd.Series:
        """
        Returns latest spot rates or latest possible before analysis start date.
        """
        df = market_data

        if analysis_start_date:
               df = market_data[:analysis_start_date]

        if ticker is not None and price is None:
                warnings.warn("You passed `ticker` without specifying the `price`."
                              "you should also pass `price` ('bid', 'mid', or 'ask') to select a specific quote.",
            category=UserWarning,
            stacklevel=2,
        )
        
        if ticker is not None:
                cols = [col for col in df.columns if str(col).startswith(ticker.lower())]
                df = df[cols]

                # TODO: raise ValueError if ticker not allowed.

        if price is not None:
                cols = [col for col in df.columns if str(col).endswith(price.lower())]
                df = df[cols]

        return df.iloc[-1]

