# -*- coding: utf-8 -*-
import sys, os, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import KLINE_DIR, SIGNAL_DIR

def holt_smooth(s, a=0.3, b=0.1):
    n = len(s)
    if n < 2: return s.copy()
    l, t = np.zeros(n), np.zeros(n)
    l[0] = s.iloc[0]
    t[0] = s.iloc[1] - s.iloc[0] if n > 1 else 0
    for i in range(1, n):
        l[i] = a * s.iloc[i] + (1-a) * (l[i-1] + t[i-1])
        t[i] = b * (l[i] - l[i-1]) + (1-b) * t[i-1]
    return pd.Series(l + t, index=s.index)

def get_aligned_idx(target, times):
    m = times <= target
    if not m.any(): return -1
    return int(np.where(m)[0][-1])

def generate_signals_v2(klines_dict):
    smoothed, slopes, times_dict = {}, {}, {}
    for n in klines_dict:
        df = klines_dict[n]
        times_dict[n] = df['datetime'].values
        s = holt_smooth(df['close'].reset_index(drop=True))
        smoothed[n] = s
        slopes[n] = s.diff() / s.shift(1)
    base_times = times_dict['5min']
    base_len = len(base_times)
    signals = np.zeros(base_len, dtype=int)
    N_WEEK, M_DAY = 5, 8
    WEEK_DECLINE_MIN, WEEK_DECLINE_MAX = -0.035, -0.01
    DAY_GAIN_MIN = 0.01
    H2_RECOVERY_MIN, H2_RECOVERY_MAX = 5, 15
    for i in range(max(N_WEEK * 7, M_DAY, 30), base_len):
        tt = base_times[i]
        week_idx = get_aligned_idx(tt, times_dict['week'])
        if week_idx < N_WEEK: continue
        week_ret = (smoothed['week'].iloc[week_idx] - smoothed['week'].iloc[week_idx - N_WEEK]) / smoothed['week'].iloc[week_idx - N_WEEK]
        if not (WEEK_DECLINE_MIN <= week_ret <= WEEK_DECLINE_MAX): continue
        day_idx = get_aligned_idx(tt, times_dict['day'])
        if day_idx < M_DAY: continue
        day_ret = (smoothed['day'].iloc[day_idx] - smoothed['day'].iloc[day_idx - M_DAY]) / smoothed['day'].iloc[day_idx - M_DAY]
        if day_ret < DAY_GAIN_MIN: continue
        h2_idx = get_aligned_idx(tt, times_dict['2hour'])
        if h2_idx < H2_RECOVERY_MAX: continue
        h2_win = smoothed['2hour'].iloc[max(0, h2_idx - 20):h2_idx + 1]
        lowest_local = h2_win.idxmin()
        lowest_global = smoothed['2hour'].index.get_loc(lowest_local)
        h2_rec = h2_idx - lowest_global
        if not (H2_RECOVERY_MIN <= h2_rec <= H2_RECOVERY_MAX): continue
        m15_idx = get_aligned_idx(tt, times_dict['15min'])
        if m15_idx < 3: continue
        if slopes['15min'].iloc[m15_idx] > 0 and slopes['15min'].iloc[m15_idx - 1] <= 0:
            signals[i] = 1
    return pd.Series(signals, index=range(base_len))

if __name__ == '__main__':
    print('=' * 60)
    print('Signal V2: Confirmed Parameters')
    print('=' * 60)
    klines_dict = {}
    for n in ['5min', '15min', '1hour', '2hour', 'day', 'week']:
        p = os.path.join(KLINE_DIR, n + '.csv')
        if os.path.exists(p):
            klines_dict[n] = pd.read_csv(p)
            print('Loaded ' + n + ': ' + str(len(klines_dict[n])) + ' bars')
    print('Generating signals...')
    signals = generate_signals_v2(klines_dict)
    lc = int((signals == 1).sum())
    t = len(signals)
    print('Long signals: ' + str(lc) + ' / ' + str(t))
    pdf = pd.DataFrame({'index': signals.index, 'signal': signals.values})
    os.makedirs(SIGNAL_DIR, exist_ok=True)
    pp = os.path.join(SIGNAL_DIR, 'signals_v2.csv')
    pdf.to_csv(pp, index=False)
    print('Signals saved to: ' + pp)
