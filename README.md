# Multi-Period Moving Average Resonance Strategy

A quantitative research project exploring multi-period moving average resonance strategy in Chinese futures market.

## Project Structure

`
multi_period_strategy/
|-- README.md                        # This file
|-- research_note_en.md              # Research note (English) - Updated Sep 2026
|-- research_note_cn.md              # Research note (Chinese) - Updated Sep 2026
|-- research_note.md                 # Detailed research report (English)
|-- multi_period_strategy_report.md  # Technical report (English)
|-- multi_period_strategy_report_cn.md  # Technical report (Chinese)
|-- code/
|   |-- config.py                    # Configuration file
|   |-- signal_v2.py                 # Signal generation (final version)
|   |-- multi_tf_signal_fixed.py     # Fixed multi-timeframe signal
|   |-- step1_data_check.py          # Data verification
|   |-- step3_backtest.py            # Backtesting framework
|-- charts/
|   |-- deep_analysis.png            # Multi-period analysis
|   |-- parameter_distribution.png   # Parameter distribution
|   |-- rally_analysis_v2.png        # Rally analysis
|   |-- rally_annotation.png         # Rally annotations
|   |-- signal_analysis_v2.png       # Signal analysis
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

## Research Highlights

- 11 independent trading opportunities identified across 8 futures contracts
- +2.131% total return without stop loss
- 1-hour trend stop loss found optimal for risk-adjusted returns
- Signal independence analysis reveals sector correlations
- Case-level analysis identifies profit/loss patterns

## License

For educational purposes only.

## Contact

BELLA - Research Notes