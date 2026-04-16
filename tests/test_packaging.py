"""Tests for packaging calculations and edge-case handling."""

import unittest

from modules.mapper import generate_wire_list
from modules.output import generate_bom
from modules.packaging import calculate_sleeve_length, get_packaging_data


class PackagingTests(unittest.TestCase):
    """Verify sleeve sizing and fallback packaging behavior."""

    def test_sleeve_length_uses_margin_tolerance_and_rounding(self) -> None:
        """Sleeve length should follow the spreadsheet-style rule."""
        result = calculate_sleeve_length(21 / 12)

        self.assertAlmostEqual(result["sleeve_length_in"], 27.63, places=2)
        self.assertEqual(result["sleeve_length_ft"], 2.5)

    def test_no_fit_sleeve_returns_warning_instead_of_crashing(self) -> None:
        """Out-of-range bundle diameters should return a warning state."""
        signals = [
            {"signal_name": f"PWR_{index}", "current": 115.0}
            for index in range(1, 40)
        ]
        wire_list = generate_wire_list(signals, 12.0)

        packaging_data = get_packaging_data(wire_list)

        self.assertFalse(packaging_data["has_valid_sleeve"])
        self.assertEqual(packaging_data["recommended_sleeve_pn"], "No matching sleeve")
        self.assertIn("No sleeve range found", packaging_data["packaging_warning"])

    def test_bom_omits_sleeve_when_no_fit_exists(self) -> None:
        """No sleeve BOM line should be added when no sleeve is available."""
        signals = [
            {"signal_name": f"PWR_{index}", "current": 115.0}
            for index in range(1, 40)
        ]
        wire_list = generate_wire_list(signals, 12.0)
        packaging_data = get_packaging_data(wire_list)

        bom = generate_bom(wire_list, packaging_data)

        self.assertEqual(bom["sleeve"], {})


if __name__ == "__main__":
    unittest.main()
