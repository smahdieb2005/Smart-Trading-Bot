
import unittest
import pandas as pd

from strategy import calculate_indicators, generate_signal


class TestTradingStrategy(unittest.TestCase):

    def make_candles(self, count=220):
        prices = [100 + i * 0.1 for i in range(count)]

        return pd.DataFrame({
            "open": prices,
            "high": [p + 1 for p in prices],
            "low": [p - 1 for p in prices],
            "close": prices
        })

    def test_indicators_are_created(self):
        data = self.make_candles()
        result = calculate_indicators(data)

        self.assertIn("ema20", result.columns)
        self.assertIn("ema50", result.columns)
        self.assertIn("ema200", result.columns)
        self.assertIn("rsi", result.columns)
        self.assertIn("atr", result.columns)

    def test_missing_columns_raise_error(self):
        data = pd.DataFrame({
            "open": [100],
            "close": [101]
        })

        with self.assertRaises(ValueError):
            calculate_indicators(data)

    def test_insufficient_data_returns_wait(self):
        hourly = self.make_candles(50)
        fifteen = self.make_candles(50)

        result = generate_signal(hourly, fifteen)

        self.assertEqual(result["signal"], "WAIT")


if __name__ == "__main__":
    unittest.main()

