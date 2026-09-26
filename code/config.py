# -*- coding: utf-8 -*-
import os

DATA_ROOT = "D:/tqsdk_data"
KLINE_DIR = os.path.join(DATA_ROOT, "kline")
RESULT_DIR = os.path.join(DATA_ROOT, "results")
SIGNAL_DIR = os.path.join(DATA_ROOT, "signals")

TQ_USER = "BELLA11"
TQ_PASS = "040318yhm"

VARIANTS = {
    "rb": {"name": "Rebar", "commission": 0.0001, "slippage_ticks": 2, "volume_multiple": 10, "price_tick": 1.0},
    "cu": {"name": "Copper", "commission": 0.00005, "slippage_ticks": 2, "volume_multiple": 5, "price_tick": 10.0},
    "m": {"name": "Soybean", "commission": 0.0001, "slippage_ticks": 2, "volume_multiple": 10, "price_tick": 1.0},
    "MA": {"name": "Methanol", "commission": 0.0001, "slippage_ticks": 2, "volume_multiple": 10, "price_tick": 1.0},
    "al": {"name": "Aluminum", "commission": 0.0001, "slippage_ticks": 2, "volume_multiple": 5, "price_tick": 5.0},
    "i": {"name": "Iron Ore", "commission": 0.0001, "slippage_ticks": 2, "volume_multiple": 100, "price_tick": 0.5},
    "SR": {"name": "Sugar", "commission": 0.0001, "slippage_ticks": 2, "volume_multiple": 10, "price_tick": 1.0},
    "TA": {"name": "PTA", "commission": 0.0001, "slippage_ticks": 2, "volume_multiple": 5, "price_tick": 2.0},
}

DURATIONS = {
    "5min": 300, "15min": 900, "1hour": 3600, "2hour": 7200, "day": 86400, "week": 86400 * 7,
}

FETCH_TIMEOUT = 10
BACKTEST_TIMEOUT = 5

for d in [DATA_ROOT, KLINE_DIR, RESULT_DIR, SIGNAL_DIR]:
    os.makedirs(d, exist_ok=True)