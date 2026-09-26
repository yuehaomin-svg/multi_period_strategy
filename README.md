# Multi-Period Moving Average Resonance Strategy

A quantitative research project exploring multi-period moving average resonance strategy in Chinese futures market.

## Project Structure

`
multi_period_strategy/
|-- README.md                    # This file
|-- research_note.md             # Main research report (English)
|-- multi_period_strategy_report.md  # Detailed technical report (English)
|-- multi_period_strategy_report_cn.md  # Chinese version
|-- code/
|   |-- config.py                # Configuration file
|   |-- signal_v2.py             # Signal generation (final version)
|   |-- multi_tf_signal_fixed.py # Fixed multi-timeframe signal
|   |-- step1_data_check.py      # Data verification
|   |-- step3_backtest.py        # Backtesting framework
|   |-- step1_verify_signal.py   # Signal verification
|   |-- step2_future_function_check.py  # Future function check
|   |-- step3_backtest_fixed.py  # Fixed backtest
|-- charts/
|   |-- deep_analysis.png        # Multi-period analysis
|   |-- parameter_distribution.png  # Parameter distribution
|   |-- rally_analysis_v2.png    # Rally analysis
|   |-- rally_annotation.png     # Rally annotations
|   |-- signal_analysis_v2.png   # Signal analysis
|-- data/                        # Data files (not included)
`

## Quick Start

1. Install dependencies:
`ash
pip install tqsdk pandas numpy matplotlib statsmodels
`

2. Configure your TqSdk account in code/config.py

3. Run signal generation:
`ash
cd code
python signal_v2.py
`

## Strategy Overview

### Entry Conditions

1. **Weekly**: Cumulative decline in [-3.5%, -1.0%]
2. **Daily**: Cumulative gain >= +1%
3. **2hour/1hour**: Stabilized 5-15 bars from low
4. **Small period filter**: No significant decline in 15min/5min

### Stop Loss

1-hour trend stop loss: Price < 1hour EMA AND 1hour slope < 0

## Key Findings

- 11 independent trading opportunities identified
- +2.131% total return without stop loss
- 1-hour trend stop loss is optimal for risk-adjusted returns
- Signal independence is critical at portfolio level

## License

For educational purposes only.

## Contact

BELLA - Research Notes