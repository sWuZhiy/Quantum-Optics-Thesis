"""Fast non-diagonalization tests for the 32-GiB ED handoff."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ft_tc_32gb_reentrant_ed import (  # noqa: E402
    dense_ed_memory_estimate,
    output_filename,
    select_direct_reference,
    select_preflight_case,
)


class MemoryEstimateTests(unittest.TestCase):
    def test_n14_dense_matrix_is_two_gib(self):
        estimate = dense_ed_memory_estimate(14)
        self.assertEqual(estimate["hilbert_dimension"], 16384)
        self.assertEqual(estimate["dense_matrix_gib"], 2.0)
        self.assertEqual(estimate["estimated_peak_gib"], 10.0)

    def test_rejects_size_unsafe_for_32_gib_handoff(self):
        with self.assertRaises(ValueError):
            dense_ed_memory_estimate(15)


class PayloadTests(unittest.TestCase):
    def setUp(self):
        self.payload = {"values": [{
            "J": -0.2,
            "Delta": 0.4001,
            "omega": 1.0,
            "status": "two_root_slice_analyzed",
            "probes": {"inside_at_minimum_a4": {
                "T": 0.1256,
                "predicted_h_star": 0.0201,
                "g_local": 0.5477,
                "predicted_depth_below_g_local": 1.9e-9,
                "direct_crosscheck": {
                    "h": 0.0201,
                    "ed_g_equal": {"12": 0.547699998},
                    "nlce": {"g_equal_aitken": 0.547699999},
                },
            }},
        }]}

    def test_selects_pre_registered_case(self):
        case = select_preflight_case(self.payload, 0.4001)
        self.assertEqual(case["Delta"], 0.4001)
        self.assertEqual(case["h"], 0.0201)

    def test_selects_direct_reference(self):
        reference = select_direct_reference(self.payload, 0.4001)
        self.assertEqual(reference["ed_g_equal"]["12"], 0.547699998)

    def test_stable_output_filename(self):
        self.assertEqual(output_filename(0.4001, 14),
                         "ed-N14-Delta0.4001.json")


if __name__ == "__main__":
    unittest.main()
