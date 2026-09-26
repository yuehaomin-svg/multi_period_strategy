# -*- coding: utf-8 -*-
"""
信号方向验证：将信号取反后再回测，对比结果
"""
import sys
import os
import time
import numpy as np
import pandas as pd
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (TQ_USER, TQ_PASS, SYMBOL, DURATIONS, 
                    KLINE_DIR, RESULT_DIR, BACKTEST_TIMEOUT)
from tqsdk import TqApi, TqAuth, TqSim, TqBacktest, BacktestFinished


def load_signals():
    """加载信号"""
    signal_path = os.path.join(KLINE_DIR, '..', 'signals', 'signals.csv')
    if os.path.exists(signal_path):
        df = pd.read_csv(signal_path)
        return df['signal'].values
    return None


def run_backtest_with_signals(signals, label=""):
    """使用给定信号运行回测"""
    commission_rate = 0.0001
    slippage_ticks = 2
    price_tick = 1.0
    volume_multiple = 10
    initial_capital = 1000000
    
    start_dt = date(2026, 7, 1)
    end_dt = date(2026, 9, 24)
    
    api = TqApi(
        TqSim(init_balance=initial_capital),
        backtest=TqBacktest(start_dt=start_dt, end_dt=end_dt),
        auth=TqAuth(TQ_USER, TQ_PASS)
    )
    
    try:
        klines = api.get_kline_serial(SYMBOL, DURATIONS['5min'], data_length=1000)
        
        equity_curve = [initial_capital]
        trades = []
        current_position = 0
        entry_price = 0
        signal_idx = 0
        
        while True:
            try:
                api.wait_update(deadline=time.time() + BACKTEST_TIMEOUT)
            except Exception as e:
                break
            
            if api.is_changing(klines.iloc[-1], "datetime"):
                if signal_idx < len(signals):
                    current_signal = signals[signal_idx]
                    signal_idx += 1
                else:
                    current_signal = 0
                
                current_price = klines.iloc[-1]['close']
                
                if current_signal == 1 and current_position <= 0:
                    if current_position == -1:
                        pnl = (entry_price - current_price) * volume_multiple - slippage_ticks * price_tick * volume_multiple
                        pnl -= abs(current_price * volume_multiple * commission_rate)
                        trades.append({'type': 'close_short', 'pnl': pnl})
                        equity_curve.append(equity_curve[-1] + pnl)
                    entry_price = current_price + slippage_ticks * price_tick
                    current_position = 1
                    
                elif current_signal == -1 and current_position >= 0:
                    if current_position == 1:
                        pnl = (current_price - entry_price) * volume_multiple - slippage_ticks * price_tick * volume_multiple
                        pnl -= abs(current_price * volume_multiple * commission_rate)
                        trades.append({'type': 'close_long', 'pnl': pnl})
                        equity_curve.append(equity_curve[-1] + pnl)
                    entry_price = current_price - slippage_ticks * price_tick
                    current_position = -1
                    
                elif current_signal == 0 and current_position != 0:
                    if current_position == 1:
                        pnl = (current_price - entry_price) * volume_multiple - slippage_ticks * price_tick * volume_multiple
                    else:
                        pnl = (entry_price - current_price) * volume_multiple - slippage_ticks * price_tick * volume_multiple
                    pnl -= abs(current_price * volume_multiple * commission_rate)
                    trades.append({'type': 'close', 'pnl': pnl})
                    equity_curve.append(equity_curve[-1] + pnl)
                    current_position = 0
        
        equity_curve = np.array(equity_curve)
        
        # 计算指标
        total_return = (equity_curve[-1] / equity_curve[0] - 1) * 100
        wins = [t for t in trades if t['pnl'] > 0]
        losses = [t for t in trades if t['pnl'] <= 0]
        win_rate = len(wins) / len(trades) * 100 if trades else 0
        avg_win = np.mean([t['pnl'] for t in wins]) if wins else 0
        avg_loss = np.mean([t['pnl'] for t in losses]) if losses else 0
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
        
        return {
            'label': label,
            'total_return': total_return,
            'total_trades': len(trades),
            'win_trades': len(wins),
            'loss_trades': len(losses),
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
        }
        
    except BacktestFinished:
        pass
    finally:
        api.close()


def main():
    print("=" * 70)
    print("Step 1: 信号方向验证")
    print("=" * 70)
    
    # 加载原始信号
    signals = load_signals()
    if signals is None:
        print("[错误] 未找到信号文件")
        return
    
    print(f"加载信号: {len(signals)} 个时间点")
    
    # 运行原始信号回测
    print("\n>>> 运行原始信号回测...")
    result_original = run_backtest_with_signals(signals, "原始信号")
    
    # 生成取反信号
    inverted_signals = -signals  # 1变-1，-1变1，0变0
    
    # 运行取反信号回测
    print("\n>>> 运行取反信号回测...")
    result_inverted = run_backtest_with_signals(inverted_signals, "取反信号")
    
    # 打印对比结果
    print("\n" + "=" * 70)
    print("信号方向验证结果对比")
    print("=" * 70)
    print(f"{'指标':<15} {'原始信号':>15} {'取反信号':>15}")
    print("-" * 70)
    print(f"{'总收益率':<15} {result_original['total_return']:>14.2f}% {result_inverted['total_return']:>14.2f}%")
    print(f"{'交易次数':<15} {result_original['total_trades']:>15} {result_inverted['total_trades']:>15}")
    print(f"{'盈利次数':<15} {result_original['win_trades']:>15} {result_inverted['win_trades']:>15}")
    print(f"{'亏损次数':<15} {result_original['loss_trades']:>15} {result_inverted['loss_trades']:>15}")
    print(f"{'胜率':<15} {result_original['win_rate']:>14.2f}% {result_inverted['win_rate']:>14.2f}%")
    print(f"{'盈亏比':<15} {result_original['profit_factor']:>15.2f} {result_inverted['profit_factor']:>15.2f}")
    
    # 判断
    print("\n" + "=" * 70)
    print("结论")
    print("=" * 70)
    if result_inverted['total_return'] > result_original['total_return']:
        print("取反后收益变好，说明原始信号方向可能映射有误。")
    elif result_inverted['total_return'] < result_original['total_return']:
        print("取反后收益变差，说明原始信号方向基本正确。")
    else:
        print("取反后收益不变，需要进一步分析。")


if __name__ == "__main__":
    main()
