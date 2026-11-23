"""Resolution classification tests for returned N=14 FT-TC data."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ft_tc_32gb_return_analyze import classify_result  # noqa: E402


def payload(depth, n14_minus_n12, n14_minus_nlce):
    return {
        "parameters": {
            "Delta": 0.4001,
            "T": 0.1256,
            "h": 0.02,
            "N": 14,
            "g_local": 0.5477,
            "predicted_depth_below_g_local": 2e-9,
        },
        "values": {
            "g_equal": 0.5477 - depth,
            "observed_depth_below_g_local": depth,
            "observed_to_sixth_order_depth_ratio": depth / 2e-9,
        },
        "finite_size_differences": {
            "N14_minus_N12": n14_minus_n12,
            "N14_minus_NLCE_Aitken": n14_minus_nlce,
        },
        "existing_reference": {
            "ed_g_equal": {"12": 0.5477},
            "nlce_g_equal_aitken": 0.5477,
        },
        "runtime": {
            "elapsed_seconds": 200,
            "peak_process_memory_gib": 4,
            "python": "3.13.14 test",
            "numpy": "2.5.5",
            "platform": "test",
            "thread_environment": {"OPENBLAS_NUM_THREADS": "8"},
        },
    }


class ClassificationTests(unittest.TestCase):
    def test_resolved(self):
        row = classify_result(payload(2e-9, 5e-12, -2e-11))
        self.assertEqual(row["resolution_status"],
                         "resolved_by_n14_and_nlce_spread")
        self.assertAlmostEqual(row["signal_to_resolution_ratio"], 100)

    def test_marginal(self):
        row = classify_result(payload(2e-10, 5e-12, -1.5e-10))
        self.assertEqual(row["resolution_status"],
                         "marginal_against_n14_and_nlce_spread")

    def test_sign_flip_is_unresolved(self):
        row = classify_result(payload(-5e-11, 1e-10, -3e-10))
        self.assertEqual(
            row["resolution_status"],
            "unresolved_sign_flip_or_no_finite_field_advantage")


if __name__ == "__main__":
    unittest.main()
