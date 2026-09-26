# -*- coding: utf-8 -*-
"""
Step 3: 回测框架
将多周期信号接入 TqSdk 回测模式，输出收益曲线、胜率、最大回撤、夏普比率。
"""
import sys
import os
import time
import numpy as np
import pandas as pd
from datetime import date, datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (TQ_USER, TQ_PASS, SYMBOL, DURATIONS, 
                    KLINE_DIR, RESULT_DIR, BACKTEST_TIMEOUT)
from tqsdk import TqApi, TqAuth, TqSim, TqBacktest, BacktestFinished
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def load_signals():
    """加载 Step 2 生成的信号"""
    signal_path = os.path.join(RESULT_DIR, '..', 'signals', 'signals.csv')
    if not os.path.exists(signal_path):
        signal_path = os.path.join(KLINE_DIR, '..', 'signals', 'signals.csv')
    
    if os.path.exists(signal_path):
        df = pd.read_csv(signal_path)
        return df['signal'].values
    return None


def calculate_metrics(equity_curve, trades):
    """计算绩效指标"""
    metrics = {}
    
    # 总收益
    total_return = (equity_curve[-1] / equity_curve[0] - 1) * 100
    metrics['total_return'] = total_return
    
    # 交易统计
    if trades:
        wins = [t for t in trades if t['pnl'] > 0]
        losses = [t for t in trades if t['pnl'] <= 0]
        metrics['total_trades'] = len(trades)
        metrics['win_trades'] = len(wins)
        metrics['loss_trades'] = len(losses)
        metrics['win_rate'] = len(wins) / len(trades) * 100 if trades else 0
        
        # 平均盈亏
        metrics['avg_win'] = np.mean([t['pnl'] for t in wins]) if wins else 0
        metrics['avg_loss'] = np.mean([t['pnl'] for t in losses]) if losses else 0
        
        # 盈亏比
        metrics['profit_factor'] = abs(metrics['avg_win'] / metrics['avg_loss']) if metrics['avg_loss'] != 0 else float('inf')
    else:
        metrics['total_trades'] = 0
        metrics['win_trades'] = 0
        metrics['loss_trades'] = 0
        metrics['win_rate'] = 0
        metrics['avg_win'] = 0
        metrics['avg_loss'] = 0
        metrics['profit_factor'] = 0
    
    # 最大回撤
    peak = np.maximum.accumulate(equity_curve)
    drawdown = (peak - equity_curve) / peak * 100
    metrics['max_drawdown'] = np.max(drawdown) if len(drawdown) > 0 else 0
    
    # 夏普比率（假设无风险利率3%，年化）
    returns = np.diff(equity_curve) / equity_curve[:-1]
    if len(returns) > 0 and np.std(returns) > 0:
        daily_sharpe = np.mean(returns) / np.std(returns)
        metrics['sharpe_ratio'] = daily_sharpe * np.sqrt(252)  # 年化
    else:
        metrics['sharpe_ratio'] = 0
    
    return metrics


def plot_results(equity_curve, signals, trades, metrics):
    """绘制回测结果图表"""
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    
    # 1. 净值曲线
    ax1 = axes[0]
    ax1.plot(equity_curve, label='Equity', color='blue', linewidth=1)
    ax1.set_title('Equity Curve')
    ax1.set_ylabel('Equity')
    ax1.legend()
    ax1.grid(True)
    
    # 2. 信号分布
    ax2 = axes[1]
    signal_colors = {1: 'green', -1: 'red', 0: 'gray'}
    for i, s in enumerate(signals):
        if s != 0:
            ax2.axvline(x=i, color=signal_colors.get(s, 'gray'), alpha=0.3, linewidth=0.5)
    ax2.set_title('Trading Signals (Green=Long, Red=Short)')
    ax2.set_ylabel('Signal')
    ax2.set_yticks([])
    
    # 3. 回撤曲线
    ax3 = axes[2]
    peak = np.maximum.accumulate(equity_curve)
    drawdown = (peak - equity_curve) / peak * 100
    ax3.fill_between(range(len(drawdown)), 0, -drawdown, color='red', alpha=0.3)
    ax3.set_title('Drawdown')
    ax3.set_ylabel('Drawdown %')
    ax3.set_xlabel('Bar Index')
    ax3.grid(True)
    
    plt.tight_layout()
    
    # 保存图表
    chart_path = os.path.join(RESULT_DIR, 'backtest_result.png')
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"图表已保存: {chart_path}")
    
    return chart_path


def run_backtest():
    """运行回测"""
    print("=" * 60)
    print("Step 3: 多周期均线策略回测")
    print("=" * 60)
    
    # 加载信号
    signals = load_signals()
    if signals is None:
        print("[错误] 未找到信号文件，请先运行 Step 2")
        return
    
    print(f"加载信号: {len(signals)} 个时间点")
    
    # 回测参数
    commission_rate = 0.0001  # 手续费率 0.01%
    slippage_ticks = 2  # 滑点 2 个 tick
    price_tick = 1.0  # 螺纹钢最小价格变动
    volume_multiple = 10  # 合约乘数
    initial_capital = 1000000  # 初始资金 100万
    
    # 回测日期范围（根据数据量调整）
    # 5分钟数据有1000根，约覆盖42个交易日
    start_dt = date(2026, 7, 1)
    end_dt = date(2026, 9, 24)
    
    print(f"回测区间: {start_dt} ~ {end_dt}")
    print(f"标的: {SYMBOL}")
    print(f"手续费率: {commission_rate*100:.3f}%")
    print(f"滑点: {slippage_ticks} ticks")
    print("-" * 60)
    
    # 创建 TqSdk 回测环境
    api = TqApi(
        TqSim(init_balance=initial_capital),
        backtest=TqBacktest(start_dt=start_dt, end_dt=end_dt),
        auth=TqAuth(TQ_USER, TQ_PASS)
    )
    
    try:
        # 获取5分钟K线
        klines = api.get_kline_serial(SYMBOL, DURATIONS['5min'], data_length=1000)
        
        # 状态变量
        equity_curve = [initial_capital]
        trades = []
        current_position = 0  # 1=多头, -1=空头, 0=无仓位
        entry_price = 0
        signal_idx = 0
        
        bar_count = 0
        
        while True:
            try:
                api.wait_update(deadline=time.time() + BACKTEST_TIMEOUT)
            except Exception as e:
                print(f"[警告] wait_update 超时: {e}")
                break
            
            # 检查是否有新的K线
            if api.is_changing(klines.iloc[-1], "datetime"):
                bar_count += 1
                
                # 获取当前信号
                if signal_idx < len(signals):
                    current_signal = signals[signal_idx]
                    signal_idx += 1
                else:
                    current_signal = 0
                
                current_price = klines.iloc[-1]['close']
                
                # 交易逻辑
                if current_signal == 1 and current_position <= 0:
                    # 做多信号，平空开多
                    if current_position == -1:
                        # 平空
                        pnl = (entry_price - current_price) * volume_multiple - slippage_ticks * price_tick * volume_multiple
                        pnl -= abs(current_price * volume_multiple * commission_rate)
                        trades.append({'type': 'close_short', 'pnl': pnl})
                        equity_curve.append(equity_curve[-1] + pnl)
                    
                    # 开多
                    entry_price = current_price + slippage_ticks * price_tick
                    current_position = 1
                    
                elif current_signal == -1 and current_position >= 0:
                    # 做空信号，平多开空
                    if current_position == 1:
                        # 平多
                        pnl = (current_price - entry_price) * volume_multiple - slippage_ticks * price_tick * volume_multiple
                        pnl -= abs(current_price * volume_multiple * commission_rate)
                        trades.append({'type': 'close_long', 'pnl': pnl})
                        equity_curve.append(equity_curve[-1] + pnl)
                    
                    # 开空
                    entry_price = current_price - slippage_ticks * price_tick
                    current_position = -1
                    
                elif current_signal == 0 and current_position != 0:
                    # 平仓信号
                    if current_position == 1:
                        pnl = (current_price - entry_price) * volume_multiple - slippage_ticks * price_tick * volume_multiple
                        pnl -= abs(current_price * volume_multiple * commission_rate)
                        trades.append({'type': 'close_long', 'pnl': pnl})
                    else:
                        pnl = (entry_price - current_price) * volume_multiple - slippage_ticks * price_tick * volume_multiple
                        pnl -= abs(current_price * volume_multiple * commission_rate)
                        trades.append({'type': 'close_short', 'pnl': pnl})
                    
                    equity_curve.append(equity_curve[-1] + pnl)
                    current_position = 0
                
                # 记录净值（包含浮动盈亏）
                if current_position == 1:
                    unrealized = (current_price - entry_price) * volume_multiple
                elif current_position == -1:
                    unrealized = (entry_price - current_price) * volume_multiple
                else:
                    unrealized = 0
                
                equity_curve[-1] = equity_curve[-1]  # 更新净值
        
        # 平仓处理
        if current_position != 0:
            final_price = klines.iloc[-1]['close']
            if current_position == 1:
                pnl = (final_price - entry_price) * volume_multiple
            else:
                pnl = (entry_price - final_price) * volume_multiple
            equity_curve[-1] += pnl
        
        equity_curve = np.array(equity_curve)
        
        print(f"\n回测完成，共处理 {bar_count} 根K线")
        print(f"交易次数: {len(trades)}")
        
        # 计算绩效指标
        metrics = calculate_metrics(equity_curve, trades)
        
        print("\n" + "=" * 60)
        print("回测绩效报告")
        print("=" * 60)
        print(f"总收益率: {metrics['total_return']:.2f}%")
        print(f"总交易次数: {metrics['total_trades']}")
        print(f"盈利次数: {metrics['win_trades']}")
        print(f"亏损次数: {metrics['loss_trades']}")
        print(f"胜率: {metrics['win_rate']:.2f}%")
        print(f"平均盈利: {metrics['avg_win']:.2f}")
        print(f"平均亏损: {metrics['avg_loss']:.2f}")
        print(f"盈亏比: {metrics['profit_factor']:.2f}")
        print(f"最大回撤: {metrics['max_drawdown']:.2f}%")
        print(f"夏普比率: {metrics['sharpe_ratio']:.2f}")
        
        # 绘制结果
        chart_path = plot_results(equity_curve, signals[:len(equity_curve)], trades, metrics)
        
        # 保存绩效报告
        report_path = os.path.join(RESULT_DIR, 'backtest_report.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("多周期均线策略回测报告\n")
            f.write("=" * 40 + "\n")
            f.write(f"回测区间: {start_dt} ~ {end_dt}\n")
            f.write(f"标的: {SYMBOL}\n")
            f.write(f"初始资金: {initial_capital}\n\n")
            f.write("绩效指标:\n")
            for k, v in metrics.items():
                f.write(f"  {k}: {v}\n")
        print(f"\n报告已保存: {report_path}")
        
    except BacktestFinished:
        print("\n回测结束")
    finally:
        api.close()


if __name__ == "__main__":
    run_backtest()
