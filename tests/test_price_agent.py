"""
Unit tests for price_agent.py enriched alert logic.
"""

import unittest
import pandas as pd
from agents.price_agent import compute_deltas, check_alert_enriched

class TestPriceAgent(unittest.TestCase):
    def setUp(self):
        # Build mock price data (5 periods + 1 latest for testing)
        self.mock_data = pd.DataFrame([
            {'Open': 100, 'Close': 101, 'High': 102, 'Low': 99},
            {'Open': 100, 'Close': 100.5, 'High': 101, 'Low': 99.5},
            {'Open': 100, 'Close': 99.8, 'High': 100.5, 'Low': 98},
            {'Open': 100, 'Close': 100.2, 'High': 101, 'Low': 99},
            {'Open': 100, 'Close': 100.1, 'High': 100.8, 'Low': 99.2},
            # Latest entry to test alert
            {'Open': 100, 'Close': 110, 'High': 111, 'Low': 99}
        ])

    def test_compute_deltas(self):
        data_with_deltas = compute_deltas(self.mock_data)
        self.assertIn('Delta_OC', data_with_deltas.columns)
        self.assertIn('Delta_HL', data_with_deltas.columns)
        self.assertAlmostEqual(data_with_deltas['Delta_OC'].iloc[-1], 10.0, places=1)
        self.assertAlmostEqual(data_with_deltas['Delta_HL'].iloc[-1], 12.0, places=1)

    def test_check_alert_static_trigger(self):
        alert = check_alert_enriched(self.mock_data)
        self.assertTrue(alert)

    def test_check_alert_dynamic_trigger(self):
        alert = check_alert_enriched(self.mock_data, static_oc=20.0, static_hl=20.0, dynamic_window=3, std_multiplier=1.0)
        self.assertTrue(alert)

    def test_no_alert_on_normal_data(self):
        # Build a normal dataset where the last row is within dynamic baseline
        normal_data = self.mock_data.copy()
        normal_data.iloc[-1] = {'Open': 100, 'Close': 100.1, 'High': 100.2, 'Low': 99.9}
        print("[DEBUG] Last row of normal_data for verification:\n", normal_data.tail())
        alert = check_alert_enriched(normal_data, static_oc=20.0, static_hl=20.0, std_multiplier=3.0)
        self.assertFalse(alert)

if __name__ == "__main__":
    unittest.main(verbosity=2)
