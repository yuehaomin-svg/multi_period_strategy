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

def gen_signals(kd, up_th=4, down_th=2, sw=5, st=0.0001):
    go = ['week', 'day', '2hour', '1hour', '15min', '5min']
    sd, sl, td = {}, {}, {}
    for n in go:
        if n not in kd: continue
        df = kd[n]
        if len(df) == 0: continue
        td[n] = df['datetime'].values
        c = df['close'].reset_index(drop=True)
        sd[n] = holt_smooth(c)
        sl[n] = sd[n].diff() / sd[n].shift(1)
    if '5min' not in sl: return pd.Series(dtype=int)
    bt = td['5min']
    sig = np.zeros(len(bt), dtype=int)
    for i in range(sw, len(bt)):
        tt = bt[i]
        uc = 0
        for n in go:
            if n not in sl: continue
            ai = get_aligned_idx(tt, td[n])
            if ai == -1 or ai < sw: continue
            sv = sl[n].iloc[ai]
            if not np.isnan(sv) and sv > 0: uc += 1
        s5 = sl['5min'].iloc[i]
        if np.isnan(s5): s5 = 0
        ss = abs(s5) > st
        if uc >= up_th and ss: sig[i] = 1
        elif uc <= down_th and ss: sig[i] = -1
        else: sig[i] = 0
    return pd.Series(sig, index=range(len(bt)))

if __name__ == '__main__':
    print('=' * 60)
    print('多周期信号生成(修复版-时间对齐)')
    print('=' * 60)
    kd = {}
    for n in ['5min', '15min', '1hour', '2hour', 'day', 'week']:
        p = os.path.join(KLINE_DIR, n + '.csv')
        if os.path.exists(p):
            kd[n] = pd.read_csv(p)
            print('加载 ' + n + ': ' + str(len(kd[n])) + ' 根K线')
    print('\n生成信号中...')
    sig = gen_signals(kd)
    lc = int((sig == 1).sum())
    sc = int((sig == -1).sum())
    nc = int((sig == 0).sum())
    t = len(sig)
    print('\n信号统计(共 ' + str(t) + ' 个时间点):')
    print('  做多信号: ' + str(lc) + ' (' + str(round(lc/t*100, 2)) + '%)')
    print('  做空信号: ' + str(sc) + ' (' + str(round(sc/t*100, 2)) + '%)')
    print('  空仓信号: ' + str(nc) + ' (' + str(round(nc/t*100, 2)) + '%)')
    fl = np.where(np.diff(sig) != 0)[0]
    if len(fl) > 1:
        fi = np.diff(fl)
        print('\n信号翻转分析:')
        print('  总翻转次数: ' + str(len(fl)))
        print('  平均翻转间隔: ' + str(round(float(np.mean(fi)), 1)) + ' 根K线')
    pdf = pd.DataFrame({'index': sig.index, 'signal': sig.values})
    os.makedirs(SIGNAL_DIR, exist_ok=True)
    pp = os.path.join(SIGNAL_DIR, 'signals_fixed.csv')
    pdf.to_csv(pp, index=False)
    print('\n信号已保存到: ' + pp)