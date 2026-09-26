# Multi-Period Moving Average Resonance Strategy: A Research Note

> **Author**: BELLA
> **Date**: September 2026
> **Purpose**: Document the research process, findings, and limitations

---

## 1. Research Background and Problem

### 1.1 From Intuition to Quantification

During my internship, I observed that experienced traders look at multiple timeframes. When large timeframes show stable or slightly declining trend, medium timeframes stabilize, and small timeframes turn upward, it often precedes a significant move.

The question: Can this intuitive observation be quantified into a backtestable signal?

### 1.2 What I Did Not Know

- How to properly align data across different timeframes
- How to avoid look-ahead bias in multi-period strategies
- How to measure signal independence in a portfolio context
- Difference between state exists and state changes in signal generation

---

## 2. Method

### 2.1 Data

- 8 futures variants: Rebar, Copper, Soybean, Methanol, Aluminum, Iron Ore, Sugar, PTA
- 6 timeframes: 5min, 15min, 1hour, 2hour, Daily, Weekly
- Time range: Feb-Sep 2026 (7 months)
- Data source: TqSdk free API

### 2.2 Smoothing Method

Holt Double Exponential Smoothing chosen because:
- Captures both level and trend (unlike SES)
- Does not require seasonality parameter (unlike Holt-Winters)
- Suitable for futures prices with trending behavior

### 2.3 Four-Condition Signal Logic

1. **Weekly**: Cumulative decline in [-3.5%, -1.0%]
2. **Daily**: Cumulative gain >= +1%
3. **2hour/1hour**: Stabilized 5-15 bars from low
4. **Small period filter**: No significant decline in 15min/5min

### 2.4 Portfolio Construction

- Equal risk allocation: Each variant gets 100,000 CNY notional
- Fractional lots allowed for backtesting
- 30-bar holding period with various stop loss methods tested

---

## 3. Key Findings (Iterative, with Sample Sizes)

### 3.1 Finding 1: Future Function Bug (n=1000 bars per variant)

**Problem**: Original code used index alignment instead of timestamp alignment.

When generating signal for 5min bar at index i, the code accessed daily/weekly data at same index i. But index 100 in 5min = 2026-09-04, while index 100 in daily = 2022-12-19 (4 years earlier!).

**Fix**: Changed to timestamp-based alignment.

**Verification**: After fix, daily aligned to yesterday, weekly aligned to last Friday.

**Impact**: Win rate changed from 7.83% (original) to 4.38% (fixed). This confirms signal logic itself was ineffective, not a data problem.

### 3.2 Finding 2: Signal Definition Evolution (n=174 raw signals)

**Initial approach**: Signal triggered when all conditions True (state exists).

**Result**: 174 raw signals, only 4 independent segments after deduplication.

**Correction**: Changed to trigger only when conditions flip from False to True (state changes).

**Result**: 12 signals from 4 variants, all truly independent.

### 3.3 Finding 3: Multi-Variant Expansion (n=21 signals from 8 variants)

Expanded from 4 to 8 variants to increase independent opportunities.

**Result**:
- 4 variants: 12 signals, 5 independent opportunities
- 8 variants: 21 signals, 9 independent opportunities

**Key discovery**: Black sector variants (rb and i) show high correlation, signals often overlap within 5 days.

### 3.4 Finding 4: Case Deep Analysis (n=11 independent cases)

| Case | Variant | Pre-Trend | 50-Bar Return | Result |
|------|---------|-----------|---------------|--------|
| 1 | rb | Downtrend | -0.13% | Loss |
| 2 | i | Sideways | -0.51% | Loss |
| 3 | TA | Downtrend | +0.03% | Small Win |
| 4 | MA | Sideways | +2.10% | Big Win |
| 5 | m | Sideways | -0.67% | Loss |
| 6 | cu | Uptrend | -0.10% | Loss |
| 7 | i | Uptrend | -0.80% | Loss |
| 8 | al | Uptrend | +0.06% | Small Win |
| 9 | SR | Downtrend | +0.25% | Win |
| 10 | rb | Uptrend | +0.58% | Win |
| 11 | i | Uptrend | +0.62% | Win |

**Patterns**: Wins from sideways breakout and oversold rebound. Losses from trend chasing and downtrend continuation.

### 3.5 Finding 5: Stop Loss Period Matching (n=11 cases)

| Method | Trigger Rate | Win Rate | Max Drawdown |
|--------|--------------|----------|--------------|
| 5min Trend SL | 90.9% | 18.2% | -1.03% |
| 1hour Trend SL | 27.3% | 36.4% | -1.292% |
| 2hour Trend SL | 27.3% | 36.4% | -1.509% |

**Key insight**: Stop loss period must match entry logic period.

---

## 4. Conclusions (Restrained)

1. Multi-period resonance signals showed +2.131% total return without stop loss across 11 independent cases, but sample size is insufficient for statistical significance.

2. 1-hour trend stop loss performed most evenly, but this is post-hoc selection, not robust conclusion.

3. Signal independence is critical. Multi-variant signals highly synchronized under macro drivers (8 variants yielded only 9 independent opportunities).

4. Strategy logic is sound, but implementation required fixing critical future function bug.

---

## 5. Limitations

1. **11 independent cases is too small for statistical judgment.** Any patterns could be random.

2. **1-hour stop loss was selected based on 11 cases.** Likely overfitted to this sample.

3. **Time range only Feb-Sep 2026.** Need at least 3 years to assess robustness.

4. **No out-of-sample testing.** All analysis on same dataset.

5. **Transaction costs underestimated.** Real slippage not fully modeled.

---

## 6. Next Steps

1. Extend to 3-year data to verify robustness
2. Expand to 15-20 variants for more independent opportunities
3. Academic-style case studies with proper methodology
4. Out-of-sample testing: training (2024-2025) and test (2026)

---

## 7. Tech Stack and References

### Tech Stack

- Data: TqSdk
- Processing: Python, Pandas, NumPy
- Indicators: Holt Double Exponential Smoothing
- Backtesting: TqBacktest + TqSim
- Visualization: Matplotlib

### References

- TqSdk Official Documentation
- Python for Finance (Yves Hilpisch)
- Quantitative Trading (Ernest Chan)

---

> **Disclaimer**: Learning exercise only, not investment advice.