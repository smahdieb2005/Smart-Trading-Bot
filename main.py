
from okx_data import get_btc_candles
from strategy import generate_signal


def main():
    print("BTC/USDT - OKX")
    print("Getting market data...")

    try:
        # دریافت کندل‌های یک‌ساعته
        df_1h = get_btc_candles("1H")

        # دریافت کندل‌های ۱۵ دقیقه‌ای
        df_15m = get_btc_candles("15m")

        print("1H candles:", len(df_1h))
        print("15M candles:", len(df_15m))

        # تولید سیگنال
        result = generate_signal(df_1h, df_15m)

        print("\nTrading Signal:")
        print("Signal:", result["signal"])

        if result["signal"] in ("BUY", "SELL"):
            print("Entry:", result["entry"])
            print("Stop Loss:", result["stop_loss"])
            print("Take Profit:", result["take_profit"])
            print("Risk/Reward:", result["risk_reward"])
        else:
            print("Reason:", result.get("reason", "No signal"))

    except Exception as error:
        print("Error:", error)


if __name__ == "__main__":
    main()
