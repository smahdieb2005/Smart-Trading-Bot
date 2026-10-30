
import argparse
import pandas as pd

from strategy import generate_signal


def load_candles(file_path):
    """Load candle data from a CSV file."""
    df = pd.read_csv(file_path)

    required = ["open", "high", "low", "close"]

    if not all(col in df.columns for col in required):
        raise ValueError(
            f"{file_path} must contain: {required}"
        )

    return df


def main():
    parser = argparse.ArgumentParser(
        description="Smart Trading Bot - Safe Test Mode"
    )

    parser.add_argument(
        "--hourly",
        required=True,
        help="Path to 1-hour candle CSV file"
    )

    parser.add_argument(
        "--fifteen",
        required=True,
        help="Path to 15-minute candle CSV file"
    )

    args = parser.parse_args()

    hourly_data = load_candles(args.hourly)
    fifteen_data = load_candles(args.fifteen)

    result = generate_signal(
        hourly_data,
        fifteen_data
    )

    print("\n===== SMART TRADING BOT =====")
    print("Mode: TEST ONLY")
    print("Signal:", result["signal"])

    for key, value in result.items():
        if key != "signal":
            print(f"{key}: {value}")

    print("=============================")


if __name__ == "__main__":
    main()

