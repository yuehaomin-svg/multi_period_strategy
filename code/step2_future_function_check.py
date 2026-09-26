# -*- coding: utf-8 -*-
"""
Step 2: 未来函数排查 + 信号分布统计
"""
import sys
import os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import KLINE_DIR


def analyze_future_function():
    """分析信号生成代码中的未来函数问题"""
    print("=" * 70)
    print("Step 2: 未来函数排查")
    print("=" * 70)
    
    # 加载各粒度数据
    klines_dict = {}
    for name in ['5min', '15min', '1hour', '2hour', 'day', 'week']:
        csv_path = os.path.join(KLINE_DIR, f"{name}.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            klines_dict[name] = df
    
    # 打印各粒度数据长度和时间范围
    print("\n各粒度数据长度和时间范围:")
    print("-" * 70)
    for name, df in klines_dict.items():
        if len(df) > 0 and 'datetime' in df.columns:
            df_valid = df[df['datetime'] > 0].copy()
            if len(df_valid) > 0:
                first_time = pd.to_datetime(df_valid.iloc[0]['datetime'], unit='ns')
                last_time = pd.to_datetime(df_valid.iloc[-1]['datetime'], unit='ns')
                print(f"{name:>6}: {len(df_valid):>5} 根K线, 从 {first_time} 到 {last_time}")
    
    # 分析信号生成代码的问题
    print("\n" + "=" * 70)
    print("未来函数分析")
    print("=" * 70)
    
    print("""
【问题发现】信号生成代码存在严重的对齐错误！

代码位置：multi_tf_signal.py -> generate_signals() 函数

错误代码：
    base_len = len(slope_dict[base_name])  # base_len = 1000（5分钟数据长度）
    for i in range(slope_window + 1, base_len):
        for name in granularity_order:
            if name in slope_dict and i < len(slope_dict[name]):
                # 这里用同一个索引 i 访问不同粒度的数据！
                slope = slope_dict[name].iloc[i]

【问题本质】
- 5分钟数据：索引 0-999 对应 1000 个5分钟时间点
- 日线数据：索引 0-999 对应 1000 个日线时间点
- 周线数据：索引 0-547 对应 548 个周线时间点

但这些索引代表的是完全不同的时间！例如：
- 5分钟索引 100 对应的时间 ≈ 2026-07-04
- 日线索引 100 对应的时间 ≈ 2026-11-18（未来数据！）
- 周线索引 100 对应的时间 ≈ 2028-08-03（更远的未来！）

【结论】
当前代码在生成第 i 根5分钟K线的信号时，使用的是第 i 根日线/周线的数据，
而这些数据在那个时间点根本不存在！这是典型的未来函数。
""")


def analyze_signal_distribution():
    """分析信号分布"""
    print("\n" + "=" * 70)
    print("Step 3: 信号分布统计")
    print("=" * 70)
    
    signal_path = os.path.join(KLINE_DIR, '..', 'signals', 'signals.csv')
    if not os.path.exists(signal_path):
        print("[错误] 未找到信号文件")
        return
    
    df = pd.read_csv(signal_path)
    signals = df['signal'].values
    
    # 基本统计
    long_count = int((signals == 1).sum())
    short_count = int((signals == -1).sum())
    neutral_count = int((signals == 0).sum())
    total = len(signals)
    
    print(f"\n信号基本统计（共 {total} 个时间点）:")
    print(f"  做多信号(1): {long_count} ({long_count/total*100:.2f}%)")
    print(f"  做空信号(-1): {short_count} ({short_count/total*100:.2f}%)")
    print(f"  空仓信号(0): {neutral_count} ({neutral_count/total*100:.2f}%)")
    
    # 计算信号翻转频率
    print(f"\n信号翻转分析:")
    
    # 找出所有翻转点
    flips = []
    for i in range(1, len(signals)):
        if signals[i] != signals[i-1] and signals[i] != 0:
            flips.append(i)
    
    print(f"  总翻转次数: {len(flips)}")
    
    if len(flips) > 1:
        flip_intervals = np.diff(flips)
        print(f"  平均翻转间隔: {np.mean(flip_intervals):.1f} 根K线")
        print(f"  最短翻转间隔: {np.min(flip_intervals)} 根K线")
        print(f"  最长翻转间隔: {np.max(flip_intervals)} 根K线")
        
        # 统计短间隔翻转（小于10根K线）
        short_flips = sum(1 for x in flip_intervals if x < 10)
        print(f"  短间隔翻转(<10根): {short_flips} 次 ({short_flips/len(flip_intervals)*100:.1f}%)")
    
    # 连续信号长度分析
    print(f"\n连续信号长度分析:")
    current_signal = signals[0]
    current_length = 1
    signal_lengths = {1: [], -1: [], 0: []}
    
    for i in range(1, len(signals)):
        if signals[i] == current_signal:
            current_length += 1
        else:
            signal_lengths[current_signal].append(current_length)
            current_signal = signals[i]
            current_length = 1
    signal_lengths[current_signal].append(current_length)
    
    for sig, lengths in signal_lengths.items():
        if lengths:
            label = {1: "做多", -1: "做空", 0: "空仓"}[sig]
            print(f"  {label}信号: 平均持续 {np.mean(lengths):.1f} 根, 最长 {np.max(lengths)} 根")


if __name__ == "__main__":
    analyze_future_function()
    analyze_signal_distribution()
