"""Core logic tests for the cable harness prototype."""

import unittest

from modules.awg import get_awg, get_design_awg
from modules.mapper import (
    build_engineering_note,
    check_voltage_flag,
    generate_wire_list,
    map_attributes,
    process_signals,
)
from modules.output import build_bom_rows, generate_bom


class AwgTests(unittest.TestCase):
    """Verify current-to-AWG selection and length-aware sizing."""

    def test_get_awg_selects_expected_reference_size(self) -> None:
        """The AWG lookup should use the shared reference table thresholds."""
        self.assertEqual(get_awg(4.0), "22 AWG")
        self.assertEqual(get_awg(20.0), "12 AWG")
        self.assertEqual(get_awg(41.0), "8 AWG")

    def test_get_design_awg_bumps_size_for_long_runs(self) -> None:
        """Longer runs should recommend one larger conductor when available."""
        awg, note = get_design_awg(12.0, 20.0)
        self.assertEqual(awg, "14 AWG")
        self.assertEqual(note, "AWG increased for longer cable run")

    def test_get_awg_rejects_non_positive_current(self) -> None:
        """Current inputs must be positive."""
        with self.assertRaises(ValueError):
            get_awg(0)


class MapperTests(unittest.TestCase):
    """Verify wire-list mapping, notes, and flags."""

    def test_process_signals_returns_expected_fields(self) -> None:
        """Processed signals should include mapped AWG and part data."""
        signals = [
            {"signal_name": "DC_PWR", "current": 12.0, "color": "black"},
            {"signal_name": "SENSOR", "current": 3.0},
        ]

        processed = process_signals(signals)

        self.assertEqual(len(processed), 2)
        self.assertEqual(processed[0]["awg"], "16 AWG")
        self.assertEqual(processed[0]["color"], "black")
        self.assertIn("wire_pn", processed[0])
        self.assertEqual(processed[1]["awg"], "22 AWG")

    def test_generate_wire_list_includes_length_and_note(self) -> None:
        """Wire-list rows should include consistent length and engineering note."""
        signals = [{"signal_name": "PUMP_FEED", "current": 12.0}]

        wire_list = generate_wire_list(signals, 20.0)

        self.assertEqual(wire_list[0]["length"], 20.0)
        self.assertEqual(wire_list[0]["awg"], "14 AWG")
        self.assertIn("AWG increased for longer cable run", wire_list[0]["note"])

    def test_map_attributes_respects_manual_color(self) -> None:
        """Color overrides should drive the mapped wire part number."""
        attributes = map_attributes("18 AWG", "blue")
        self.assertEqual(attributes["color"], "blue")
        self.assertEqual(attributes["wire_pn"], "WIRE-18-BLU-001")

    def test_build_engineering_note_combines_relevant_guidance(self) -> None:
        """Engineering notes should combine run-length and load warnings."""
        note = build_engineering_note(
            current=23.0,
            awg="12 AWG",
            length=20.0,
            base_note="AWG increased for longer cable run",
        )
        self.assertIn("AWG increased for longer cable run", note)
        self.assertIn("Long run: review voltage drop", note)
        self.assertIn("Current is close to ampacity limit", note)

    def test_check_voltage_flag_matches_length_thresholds(self) -> None:
        """Voltage warnings should reflect the current prototype thresholds."""
        self.assertEqual(check_voltage_flag(8.0), "")
        self.assertEqual(check_voltage_flag(12.0), "Voltage drop check recommended")
        self.assertEqual(
            check_voltage_flag(20.0),
            "Voltage drop check strongly recommended for this cable length",
        )


class OutputTests(unittest.TestCase):
    """Verify BOM data produced from wire-list rows."""

    def test_generate_bom_counts_wire_lengths(self) -> None:
        """Wire BOM quantities should reflect total required length."""
        wire_list = [
            {
                "signal_name": "A",
                "current": 1.0,
                "awg": "22 AWG",
                "color": "white",
                "wire_pn": "WIRE-22-WHT-001",
                "length": 12.0,
                "note": "",
            },
            {
                "signal_name": "B",
                "current": 1.0,
                "awg": "22 AWG",
                "color": "white",
                "wire_pn": "WIRE-22-WHT-001",
                "length": 12.0,
                "note": "",
            },
        ]

        bom = generate_bom(wire_list)

        self.assertEqual(bom["wire"]["WIRE-22-WHT-001"], 24.0)

    def test_build_bom_rows_includes_find_numbers(self) -> None:
        """BOM rows should be numbered sequentially for display/export."""
        bom = {
            "wire": {"WIRE-18-RED-001": 12.0},
            "sleeve": {"M23053/13-012-0": 13.0},
        }

        rows = build_bom_rows(bom)

        self.assertEqual(rows[0]["FN"], 1)
        self.assertEqual(rows[1]["FN"], 2)
        self.assertEqual(rows[1]["Description"], "Shrink sleeve")


if __name__ == "__main__":
    unittest.main()
