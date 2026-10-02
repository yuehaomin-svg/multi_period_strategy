# Multi-Period Trend Strategy: A Quantitative Exploration

*Individual Research / Course Project | Sep 2026*

## Motivation

During a quant internship, I was exposed to a multi-period pyramid trading method (weekly / daily / 2h / 1h / 15min / 5min exponential smoothing) used by the team for discretionary futures and options trading. I attempted to translate this discretionary method into a backtestable signal and test whether it holds up on data.

## Method

- **Data**: TqSdk (free tier), 8 futures contracts (rb / cu / m / MA / al / i / SR / TA), periods from 5min to weekly, Feb-Sep 2026.
- **Smoothing**: Holt double exponential smoothing to generate trend lines.
- **Signal logic**: weekly cumulative decline in [-3.5%, -1.0%] + daily cumulative gain >= +1% + 2h/1h stabilizing 5-15 bars from local low + small-period filter (no significant decline).
- **Trigger**: signal fires only on state change (condition flips from False to True), not on state existence.

## Key Findings

1. **Look-ahead bias**: The original signal generation used index-based alignment, which misaligned daily/weekly data to time points several years in the past. After fixing to timestamp-based alignment, win rate dropped from 7.83% to 4.38%, confirming the signal logic itself was ineffective, not a data issue.

2. **Signal definition**: Replacing state existence with state change compressed 174 raw signals into 4 independent segments.

3. **Signal independence**: After expanding to 8 contracts, 12 signals compressed into 9 independent opportunities, revealing high correlation within the ferrous metals sector.

4. **Case-level analysis**: Across 11 independent cases, profits came from range breakouts and oversold rebounds, while losses came from trend chasing and continuation of downtrends.

5. **Stop-loss logic**:

| Stop-loss method | Trigger rate | Win rate | Max drawdown |
|------------------|--------------|----------|--------------|
| 5min trend stop | 90.9% | 18.2% | -1.03% |
| 1h trend stop | 27.3% | 36.4% | -1.292% |
| 2h trend stop | 27.3% | 36.4% | -1.509% |

Stop-loss horizon must match the entry horizon.

## Current Understanding

The signal shows a low win rate but high payoff ratio (4.38% win rate after alignment; +2.131% overall return), with profits driven by a few large one-sided moves. This suggests the signal is better suited to amplifying tail payoffs via options leverage rather than linear futures exposure, consistent with how the team actually used this method.

## Next Steps

1. Quantitatively validate the payoff structure of low win-rate signal + options leverage, comparing futures vs. options risk-return profiles.
2. Build aggregated step-wise multi-period curves from high-frequency data to better visualize turning points.
3. Extend to a broader universe (equities, equity index) to test whether the signal generalizes to markets with more frequent large moves.
4. Port the signal formula to a trading platform (e.g., Pyramid) for visual inspection.

## Limitations

- 11 independent cases; insufficient sample size for statistical inference.
- 1h stop-loss was selected ex post on 11 cases; potential overfitting.
- Time range limited to Feb-Sep 2026; needs extension to 3 years.

## Tech Stack

Python, TqSdk, Pandas, NumPy, Statsmodels (Holt smoothing), Matplotlib