# -*- coding: utf-8 -*-
import sys, os, time, numpy as np, pandas as pd
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import TQ_USER, TQ_PASS, SYMBOL, DURATIONS, KLINE_DIR, RESULT_DIR, SIGNAL_DIR, BACKTEST_TIMEOUT
from tqsdk import TqApi, TqAuth, TqSim, TqBacktest, BacktestFinished

def load_signals(filename='signals_fixed.csv'):
    sp = os.path.join(SIGNAL_DIR, filename)
    if os.path.exists(sp):
        return pd.read_csv(sp)['signal'].values
    return None

def run_backtest(signals, label=''):
    commission_rate = 0.0001
    slippage_ticks = 2
    price_tick = 1.0
    volume_multiple = 10
    initial_capital = 1000000
    
    api = TqApi(
        TqSim(init_balance=initial_capital),
        backtest=TqBacktest(start_dt=date(2026, 7, 1), end_dt=date(2026, 9, 24)),
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
            except Exception:
                break
            
            if api.is_changing(klines.iloc[-1], 'datetime'):
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
                        trades.append({'pnl': pnl})
                        equity_curve.append(equity_curve[-1] + pnl)
                    entry_price = current_price + slippage_ticks * price_tick
                    current_position = 1
                elif current_signal == -1 and current_position >= 0:
                    if current_position == 1:
                        pnl = (current_price - entry_price) * volume_multiple - slippage_ticks * price_tick * volume_multiple
                        pnl -= abs(current_price * volume_multiple * commission_rate)
                        trades.append({'pnl': pnl})
                        equity_curve.append(equity_curve[-1] + pnl)
                    entry_price = current_price - slippage_ticks * price_tick
                    current_position = -1
                elif current_signal == 0 and current_position != 0:
                    if current_position == 1:
                        pnl = (current_price - entry_price) * volume_multiple - slippage_ticks * price_tick * volume_multiple
                    else:
                        pnl = (entry_price - current_price) * volume_multiple - slippage_ticks * price_tick * volume_multiple
                    pnl -= abs(current_price * volume_multiple * commission_rate)
                    trades.append({'pnl': pnl})
                    equity_curve.append(equity_curve[-1] + pnl)
                    current_position = 0
        
        equity_curve = np.array(equity_curve)
        total_return = (equity_curve[-1] / equity_curve[0] - 1) * 100
        wins = [t for t in trades if t['pnl'] > 0]
        losses = [t for t in trades if t['pnl'] <= 0]
        win_rate = len(wins) / len(trades) * 100 if trades else 0
        avg_win = np.mean([t['pnl'] for t in wins]) if wins else 0
        avg_loss = np.mean([t['pnl'] for t in losses]) if losses else 0
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else float('inf')
        peak = np.maximum.accumulate(equity_curve)
        max_dd = np.max((peak - equity_curve) / peak * 100) if len(equity_curve) > 0 else 0
        returns = np.diff(equity_curve) / equity_curve[:-1]
        sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252) if len(returns) > 0 and np.std(returns) > 0 else 0
        
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
            'max_drawdown': max_dd,
            'sharpe': sharpe,
        }
    except BacktestFinished:
        pass
    finally:
        api.close()

if __name__ == '__main__':
    print('=' * 70)
    print('回测对比: 修复版信号 vs 原始信号')
    print('=' * 70)
    
    signals_fixed = load_signals('signals_fixed.csv')
    signals_original = load_signals('signals.csv')
    
    if signals_fixed is not None:
        print('\n>>> 运行修复版信号回测...')
        result_fixed = run_backtest(signals_fixed, '修复版(时间对齐)')
    else:
        print('[错误] 未找到修复版信号文件')
        result_fixed = None
    
    if signals_original is not None:
        print('\n>>> 运行原始信号回测...')
        result_original = run_backtest(signals_original, '原始版(索引对齐)')
    else:
        print('[错误] 未找到原始信号文件')
        result_original = None
    
    if result_fixed and result_original:
        print('\n' + '=' * 70)
        print('回测结果对比')
        print('=' * 70)
        print('{:<20} {:>20} {:>20}'.format('指标', '原始版(索引对齐)', '修复版(时间对齐)'))
        print('-' * 70)
        print('{:<20} {:>19.2f}% {:>19.2f}%'.format('总收益率', result_original['total_return'], result_fixed['total_return']))
        print('{:<20} {:>20} {:>20}'.format('交易次数', result_original['total_trades'], result_fixed['total_trades']))
        print('{:<20} {:>20} {:>20}'.format('盈利次数', result_original['win_trades'], result_fixed['win_trades']))
        print('{:<20} {:>20} {:>20}'.format('亏损次数', result_original['loss_trades'], result_fixed['loss_trades']))
        print('{:<20} {:>19.2f}% {:>19.2f}%'.format('胜率', result_original['win_rate'], result_fixed['win_rate']))
        print('{:<20} {:>20.2f} {:>20.2f}'.format('盈亏比', result_original['profit_factor'], result_fixed['profit_factor']))
        print('{:<20} {:>19.2f}% {:>19.2f}%'.format('最大回撤', result_original['max_drawdown'], result_fixed['max_drawdown']))
        print('{:<20} {:>20.2f} {:>20.2f}'.format('夏普比率', result_original['sharpe'], result_fixed['sharpe']))
        
        print('\n' + '=' * 70)
        print('结论')
        print('=' * 70)
        if result_fixed['total_return'] > result_original['total_return']:
            print('修复版信号表现更好，总收益率提升了 ' + str(round(result_fixed['total_return'] - result_original['total_return'], 2)) + '%')
        else:
            print('修复版信号表现较差，需要进一步优化')