
import unittest

from okx_data import get_btc_candles


class TestOKXConnection(unittest.TestCase):

    def test_btc_15m_candles(self):
        df = get_btc_candles("15m")

        self.assertGreater(len(df), 0)
        self.assertIn("close", df.columns)
        self.assertIn("timestamp", df.columns)

    def test_btc_1h_candles(self):
        df = get_btc_candles("1H")

        self.assertGreater(len(df), 0)
        self.assertIn("close", df.columns)
        self.assertIn("timestamp", df.columns)


if __name__ == "__main__":
    unittest.main()
