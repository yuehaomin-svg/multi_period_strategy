# Multi-Period Moving Average Resonance Strategy Research Report

> **Author**: BELLA
> **Date**: 2026-09-25
> **Research Direction**: Futures Multi-Period Technical Analysis and Quantitative Strategy

---

## 1. Research Background and Objectives

### 1.1 Research Background

Multi-period analysis is an important method in technical analysis. The core idea is: **when the trend directions of multiple time periods are consistent, the market movement is more reliable**. This study aims to explore how to quantify this idea into an executable trading strategy.

### 1.2 Research Objectives

1. **Verify the effectiveness of multi-period resonance**: Test whether the consistency of moving average directions across six time periods can generate effective signals
2. **Explore the application of exponential smoothing**: Use Holt double exponential smoothing instead of simple moving average to better capture trends
3. **Establish a complete backtesting framework**: Implement the complete process from data acquisition, signal generation to performance evaluation

---

## 2. Research Methods

### 2.1 Technical Route

Data Acquisition -> Data Preprocessing -> Exponential Smoothing Calculation -> Signal Generation -> Backtesting -> Result Analysis

### 2.2 Data Source

- **Target**: Rebar Main Continuous Contract (SHFE.rb)
- **Data Source**: TqSdk Free Version API
- **Time Granularities**: 5-minute, 15-minute, 1-hour, 2-hour, Daily, Weekly

### 2.3 Exponential Smoothing Method

**Holt Double Exponential Smoothing** (Holt Linear Trend) was chosen:

| Method | Applicable Scenario | This Study |
|--------|---------------------|-------------|
| SES | Horizontal series | Not suitable |
| **Holt** | Series with trends | **Suitable** |
| Holt-Winters | Trend + seasonality | Weak seasonality |

### 2.4 Signal Generation Logic (Three-Dimensional Judgment)

**Dimension 1: Direction Consistency**
- Count the number of smoothed moving averages with upward slopes
- >=4 upward: Bullish environment
- <=2 upward: Bearish environment
- Otherwise: Oscillation/Wait

**Dimension 2: Slope Strength**
- Whether the absolute value of the shortest period (5-minute) slope exceeds threshold

**Dimension 3: Divergence Degree**
- Distance change between weekly and 5-minute moving averages

---

## 3. Data Processing

### 3.1 Data Statistics by Period

| Period | K-line Count | Time Range | Close Mean | Close Std |
|--------|--------------|------------|------------|----------|
| week | 548 | 2016-01-03 ~ 2026-09-20 | 3639.92 | 714.19 |
| day | 1000 | 2022-08-11 ~ 2026-09-23 | 3464.30 | 355.44 |
| 2hour | 1000 | 2026-01-16 ~ 2026-09-24 | 3116.44 | 60.16 |
| 1hour | 1000 | 2026-02-27 ~ 2026-09-24 | 3119.21 | 62.82 |
| 15min | 1000 | 2026-07-24 ~ 2026-09-24 | 3073.56 | 58.34 |
| 5min | 1000 | 2026-09-03 ~ 2026-09-24 | 3128.66 | 24.06 |
### 3.2 Time Alignment Processing

**Key Issue**: Different periods have different K-line time granularities.

**Solution**: Use 5-minute time axis as baseline. For each 5-minute time point T, use the most recent completed K-line from each period before T.

### 3.3 Future Function Issue

**Problem**: Signal generation code used index alignment instead of time alignment.

**Example**:
- 5-minute index 100 -> 2026-09-04
- Daily index 100 -> 2022-12-19 (4 years earlier!)
- Weekly index 100 -> 2017-11-05 (9 years earlier!)

---

## 4. Signal Generation and Backtesting

### 4.1 Signal Distribution Statistics

| Signal Type | Count | Percentage |
|-------------|-------|------------|
| Long (1) | 259 | 25.90% |
| Short (-1) | 403 | 40.30% |
| Neutral (0) | 332 | 33.20% |

**Signal Flip Analysis**:
- Total flip count: 171
- Average flip interval: 5.8 K-lines
- 88.8% of flips have intervals < 10 K-lines (very unstable)

### 4.2 Backtesting Configuration

| Parameter | Setting |
|-----------|---------|
| Backtest Period | 2026-07-01 ~ 2026-09-24 |
| Initial Capital | 1,000,000 CNY |
| Commission Rate | 0.01% |
| Slippage | 2 ticks |
| Contract Multiplier | 10 |

### 4.3 Backtesting Results

| Metric | Value | Evaluation |
|--------|-------|------------|
| Total Return | -0.76% | Loss |
| Trade Count | 166 | Too Frequent |
| Win Rate | 7.83% | Extremely Low |
| Profit Factor | 0.43 | Insufficient |
| Max Drawdown | 0.76% | Small |
| Sharpe Ratio | -18.67 | Negative |

---

## 5. Problem Analysis

### 5.1 Root Cause

**Future Function Problem**: Signal generation code used index alignment instead of time alignment.

| Period | Data Time Range | Time at Index 100 |
|--------|-----------------|-------------------|
| 5-minute | 2026-09-03 ~ 2026-09-24 | 2026-09-04 |
| Daily | 2022-08-11 ~ 2026-09-23 | 2022-12-19 |
| Weekly | 2016-01-03 ~ 2026-09-20 | 2017-11-05 |

### 5.2 Signal Quality Analysis

1. **Signal flips too frequently**: Average 5.8 K-lines between flips
2. **Direction judgment basically random**: Inverted signal win rate (8.43%) similar to original (7.83%)
3. **Lack of trend filtering**: No distinction between trending and ranging markets

### 5.3 Code Implementation Issues

`python
# Current code assumes same length for all periods
base_len = len(slope_dict[base_name])  # 1000
for i in range(slope_window + 1, base_len):
    # Different periods have different actual time ranges!
`

---

## 6. Improvement Directions

### 6.1 Fix Future Functions

Correct time alignment: find the most recent completed K-line before each time point.

### 6.2 Add Trend Filter

Only trade when market shows clear trend (volatility above median).

### 6.3 Optimize Signal Generation

1. Add confirmation mechanism
2. Introduce volatility adjustment
3. Add stop-loss logic

---

## 7. Conclusions and Outlook

### 7.1 Main Conclusions

1. Multi-period analysis idea is effective in theory
2. Current implementation has critical future function bugs
3. Need to redesign signal generation based on proper time alignment

### 7.2 Technical Gains

- Complete quantitative strategy development process
- Importance of time series data alignment
- Detection methods for future functions
- Implementation of exponential smoothing indicators

### 7.3 Future Plans

1. **Short-term**: Fix future function issues, re-backtest
2. **Medium-term**: Add volume, volatility, sentiment indicators
3. **Long-term**: Explore machine learning applications

---

## 8. Tech Stack

- **Data Acquisition**: TqSdk (TianQin Quantitative)
- **Data Processing**: Python, Pandas, NumPy
- **Technical Indicators**: Statsmodels (Holt Smoothing)
- **Backtesting Framework**: TqBacktest + TqSim
- **Visualization**: Matplotlib

---

## 9. Reference Resources

1. TqSdk Official Documentation
2. Python for Finance - Yves Hilpisch
3. Quantitative Trading - Ernest Chan
4. Pyramid Decision Trading System Official Forum

---

> **Disclaimer**: This report is for learning and research purposes only and does not constitute investment advice. Futures trading carries high risks.
