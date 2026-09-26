# -*- coding: utf-8 -*-
"""
Step 1: 验证 TqSdk 数据获取与时间对齐
拉取螺纹钢六个时间粒度的最近数据，打印每个序列的长度和最后几根K线的时间戳。
"""
import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import TQ_USER, TQ_PASS, SYMBOL, DURATIONS, KLINE_DIR, FETCH_TIMEOUT
from tqsdk import TqApi, TqAuth
import pandas as pd


def fetch_klines(api, symbol, dur, name, timeout=FETCH_TIMEOUT):
    """
    拉取K线数据，带超时控制。
    
    get_kline_serial() 返回持续更新的引用，需要多次 wait_update() 等待数据填充。
    通过检测 datetime 字段是否非零来判断数据是否就绪。
    """
    klines = api.get_kline_serial(symbol, dur, data_length=1000)
    
    deadline = time.time() + timeout
    data_ready = False
    
    while time.time() < deadline:
        api.wait_update(deadline=deadline)
        # 检查最后一根K线的datetime是否有效（非零）
        if len(klines) > 0 and klines.iloc[-1]['datetime'] > 0:
            data_ready = True
            break
    
    if not data_ready:
        print(f"  [警告] {name} 拉取数据超时 ({timeout}秒)，数据未就绪")
        return klines, False
    
    return klines, True


def main():
    print(f"标的合约: {SYMBOL}")
    print(f"数据存储目录: {KLINE_DIR}")
    print(f"时间粒度: {list(DURATIONS.keys())}")
    print(f"拉取超时: {FETCH_TIMEOUT}秒/次")
    print("-" * 60)
    
    api = TqApi(auth=TqAuth(TQ_USER, TQ_PASS))
    
    try:
        results = {}
        
        for name, dur in DURATIONS.items():
            print(f"\n正在拉取 {name} K线 (dur={dur}s)...")
            
            klines, success = fetch_klines(api, SYMBOL, dur, name)
            
            if not success:
                print(f"  跳过 {name}，数据可能为空")
                results[name] = {'length': 0, 'last5_times': [], 'df': pd.DataFrame()}
                continue
            
            df = pd.DataFrame({
                'datetime': klines['datetime'],
                'open': klines['open'],
                'high': klines['high'],
                'low': klines['low'],
                'close': klines['close'],
                'volume': klines['volume'],
                'open_oi': klines['open_oi'],
            })
            
            df = df[df['datetime'] > 0].copy()
            df['datetime_str'] = pd.to_datetime(df['datetime'], unit='ns')
            
            length = len(df)
            
            last5 = df.tail(5)
            last5_times = last5['datetime_str'].dt.strftime('%Y-%m-%d %H:%M:%S').tolist()
            
            results[name] = {
                'length': length,
                'last5_times': last5_times,
                'df': df,
            }
            
            csv_path = os.path.join(KLINE_DIR, f"{name}.csv")
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"  已保存: {csv_path}")
            print(f"  数据长度: {length} 根K线")
        
        print("\n" + "=" * 60)
        print("数据验证结果汇总")
        print("=" * 60)
        
        for name, data in results.items():
            print(f"\n{name} (dur={DURATIONS[name]}s):")
            print(f"  数据长度: {data['length']} 根K线")
            print(f"  最后5根K线时间戳:")
            for t in data['last5_times']:
                print(f"    {t}")
        
        print("\n" + "=" * 60)
        print("时间对齐检查（以5分钟为基准）")
        print("=" * 60)
        
        if '5min' in results and results['5min']['length'] > 0:
            last_5min_time = results['5min']['last5_times'][-1]
            print(f"\n5分钟最后一根K线时间: {last_5min_time}")
            
            for name in ['15min', '1hour', '2hour', 'day', 'week']:
                if name in results and results[name]['length'] > 0:
                    last_time = results[name]['last5_times'][-1]
                    print(f"{name:>6}最后一根K线时间: {last_time}")
        
        print("\n" + "=" * 60)
        print(f"所有CSV文件已保存到: {KLINE_DIR}")
        print("=" * 60)
        
    finally:
        api.close()


if __name__ == "__main__":
    main()
