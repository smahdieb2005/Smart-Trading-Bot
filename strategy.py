
import pandas as pd
import numpy as np


def calculate_indicators(df):
    df = df.copy()
    df.columns = [c.lower() for c in df.columns]

    required = ["open", "high", "low", "close"]

    if not all(c in df.columns for c in required):
        raise ValueError("Missing OHLC columns")

    for col in required:
        df[col] = pd.to_numeric(
            df[col], errors="coerce"
        )

    if df[required].isna().any().any():
        raise ValueError("Invalid candle data")

    if (df["high"] < df["low"]).any():
        raise ValueError("Invalid high/low prices")

    close = df["close"]

    df["ema20"] = close.ewm(
        span=20, adjust=False
    ).mean()

    df["ema50"] = close.ewm(
        span=50, adjust=False
    ).mean()

    df["ema200"] = close.ewm(
        span=200, adjust=False
    ).mean()

    delta = close.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1/14,
        adjust=False,
        min_periods=14
    ).mean()

    avg_loss = loss.ewm(
        alpha=1/14,
        adjust=False,
        min_periods=14
    ).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)

    rsi = 100 - (100 / (1 + rs))

    rsi = rsi.mask(
        (avg_loss == 0) & (avg_gain > 0), 100
    )

    rsi = rsi.mask(
        (avg_loss == 0) & (avg_gain == 0), 50
    )

    df["rsi"] = rsi

    previous_close = close.shift(1)

    tr = pd.concat([
        df["high"] - df["low"],
        (df["high"] - previous_close).abs(),
        (df["low"] - previous_close).abs()
    ], axis=1).max(axis=1)

    df["atr"] = tr.ewm(
        alpha=1/14,
        adjust=False,
        min_periods=14
    ).mean()

    return df


def generate_signal(df_1h, df_15m):

    hourly = calculate_indicators(df_1h)
    entry = calculate_indicators(df_15m)

    if len(hourly) < 210 or len(entry) < 210:
        return {
            "signal": "WAIT",
            "reason": "Not enough candle data"
        }

    # The last row is assumed to be an unfinished candle.
    # Use only fully closed candles.
    h = hourly.iloc[-2]
    previous = entry.iloc[-3]
    current = entry.iloc[-2]

    values = [
        h["ema50"], h["ema200"], h["close"],
        previous["ema20"], current["ema20"],
        current["rsi"], current["atr"],
        current["close"]
    ]

    if not all(np.isfinite(v) for v in values):
        return {
            "signal": "WAIT",
            "reason": "Indicators unavailable"
        }

    entry_price = float(current["close"])
    atr = float(current["atr"])
    rsi = float(current["rsi"])

    if atr <= 0:
        return {
            "signal": "WAIT",
            "reason": "Invalid ATR"
        }

    bullish_trend = (
        h["ema50"] > h["ema200"]
        and h["close"] > h["ema50"]
    )

    bearish_trend = (
        h["ema50"] < h["ema200"]
        and h["close"] < h["ema50"]
    )

    buy_entry = (
        previous["close"] <= previous["ema20"]
        and current["close"] > current["ema20"]
        and 50 < rsi < 70
    )

    sell_entry = (
        previous["close"] >= previous["ema20"]
        and current["close"] < current["ema20"]
        and 30 < rsi < 50
    )

    if bullish_trend and buy_entry:

        stop_loss = entry_price - (1.5 * atr)
        take_profit = entry_price + (3 * atr)

        return {
            "signal": "BUY",
            "entry": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "risk_reward": 2
        }

    if bearish_trend and sell_entry:

        stop_loss = entry_price + (1.5 * atr)
        take_profit = entry_price - (3 * atr)

        return {
            "signal": "SELL",
            "entry": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "risk_reward": 2
        }

    return {
        "signal": "WAIT",
        "reason": "No valid trading setup"
    }
