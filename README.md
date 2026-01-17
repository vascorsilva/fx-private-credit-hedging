# FX-Hedged Private Credit Case Study

## Overview
- Goal:
- Perspective:
- Instruments:
- What is (and isn’t) modelled:

## Repository Structure
- `src/`
  - `global_variables.py`
  - `data_loader.py`
  - `fx_simulator.py`
  - `metrics/`
    - `performance.py`
    - `risk.py`
  - `hedges/`
    - `forwards.py`
    - `options.py`
- `notebooks/`
  - `notebook.ipynb`
- `Figures/`
- `main.py`
- `requirements.txt`
- `REPORT.md`

## Data Inputs
### Market data
- File:
- Columns used:
- Quote conventions:
- Volatility units (%, decimal):

### Cashflows
- EUR contractual schedule:
- Option premium handling:

## Methodology
### FX model
- Model:
- Calibration:
- Simulation grid:

### USD cashflow conversion
- Date alignment:
- Vectorisation approach:

### Hedging strategies
#### Unhedged
- Definition:
- Cashflow construction:

#### Forward hedge
- Definition:
- Forward curve assumption:
- Payoff formula:

#### Put option hedge (ATMF)
- Definition:
- Strike convention:
- Vol surface inputs:
- Pricing model (Garman–Kohlhagen):
- Premium timing and where it is booked:

## Metrics
### Performance metrics
- IRR:
- NPV:
- MOIC:
- Terminal value:

### Risk metrics
- Distribution summary:
- Probabilities:
- VaR / ES conventions:

## Results & Reporting
- Where plots are generated:
- Where tables are generated:
- How to reproduce the figures:

## How to Run
### Notebook
- Steps:

### Script (main)
- Command:
- Expected outputs:

## Assumptions & Limitations
- Deterministic rates:
- Flat rates vs term structure:
- Ignoring cross-currency basis:
- Drift choice:

## Future Work
- Term structures for rates and vols:
- RR/BF smile:
- Cross-currency basis:
- Alternative FX dynamics:
- Additional hedging strategies:

## Notes
- Mistakes:
