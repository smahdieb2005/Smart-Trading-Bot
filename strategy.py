import pandas as pd


def calculate_indicators(df):
    df = df.copy()

    df.columns = [c.lower() for c in df.columns]

    required = ["open", "high", "low", "close"]
    if not all(c in df.columns for c in required):
        raise ValueError("OHLC columns are required")

    for col in required:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["ema20"] = df["close"].ewm(
        span=20, adjust=False
    ).mean()

    df["ema50"] = df["close"].ewm(
        span=50, adjust=False
    ).mean()

    df["ema200"] = df["close"].ewm(
        span=200, adjust=False
    ).mean()

    delta = df["close"].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(
        alpha=1/14, adjust=False, min_periods=14
    ).mean()

    avg_loss = loss.ewm(
        alpha=1/14, adjust=False, min_periods=14
    ).mean()

    rs = avg_gain / avg_loss.replace(0, float("nan"))

    df["rsi"] = 100 - (100 / (1 + rs))

    previous_close = df["close"].shift(1)

    tr = pd.concat([
        df["high"] - df["low"],
        (df["high"] - previous_close).abs(),
        (df["low"] - previous_close).abs()
    ], axis=1).max(axis=1)

    df["atr"] = tr.ewm(
        alpha=1/14, adjust=False, min_periods=14
    ).mean()

    return df


def generate_signal(df_1h, df_15m):

    hourly = calculate_indicators(df_1h)
    entry = calculate_indicators(df_15m)

    if len(hourly) < 210 or len(entry) < 210:
        return {"signal": "WAIT", "reason": "Not enough data"}

    h = hourly.iloc[-1]
    previous = entry.iloc[-2]
    current = entry.iloc[-1]

    if pd.isna(h["ema200"]) or pd.isna(current["atr"]):
        return {"signal": "WAIT", "reason": "Indicators unavailable"}

    entry_price = float(current["close"])
    atr = float(current["atr"])

    if atr <= 0:
        return {"signal": "WAIT", "reason": "Invalid ATR"}

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
        and 50 < current["rsi"] < 70
    )

    sell_entry = (
        previous["close"] >= previous["ema20"]
        and current["close"] < current["ema20"]
        and 30 < current["rsi"] < 50
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
