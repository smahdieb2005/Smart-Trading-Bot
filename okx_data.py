
import requests
import pandas as pd


OKX_URL = "https://www.okx.com/api/v5/market/candles"


def get_btc_candles(timeframe="15m", limit=300):

    params = {
        "instId": "BTC-USDT",
        "bar": timeframe,
        "limit": str(limit)
    }

    response = requests.get(
        OKX_URL,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    result = response.json()

    if result.get("code") != "0":
        raise RuntimeError(
            f"OKX error: {result.get('msg')}"
        )

    candles = result["data"]

    df = pd.DataFrame(
        candles,
        columns=[
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "volCcy",
            "volCcyQuote",
            "confirm"
        ]
    )

    for column in ["open", "high", "low", "close"]:
        df[column] = pd.to_numeric(df[column])

    df["timestamp"] = pd.to_datetime(
        pd.to_numeric(df["timestamp"]),
        unit="ms",
        utc=True
    )

    df["confirm"] = df["confirm"].astype(int)

    df = df.sort_values("timestamp").reset_index(drop=True)

    return df


if __name__ == "__main__":

    data = get_btc_candles("15m")

    print("BTC/USDT - OKX")
    print(data.tail(5).to_string(index=False))
