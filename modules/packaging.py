"""Packaging calculations for bundle diameter and sleeve selection."""

import csv
import math
from pathlib import Path

REFERENCE_DIR = Path(__file__).resolve().parent.parent / "reference_data"


def load_wire_diameters() -> dict[str, float]:
    """Return AWG-to-diameter data from the reference CSV."""
    data = {}
    filepath = REFERENCE_DIR / "wire_diameters.csv"

    with open(filepath, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            data[row["awg"]] = float(row["wire_diameter_in"])

    return data


def load_wire_specs() -> dict[str, dict]:
    """Return AWG-to-wire-spec data from the reference CSV."""
    data = {}
    filepath = REFERENCE_DIR / "wire_specs.csv"

    with open(filepath, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            data[row["awg"]] = {
                "od_in": float(row["od_in"]),
                "ampacity_a": float(row["ampacity_a"]),
                "resistance_ohm_per_kft": float(row["resistance_ohm_per_kft"]),
            }

    return data


def load_bundle_factors() -> dict[int, float]:
    """Return wire-count bundle factors from the reference CSV."""
    data = {}
    filepath = REFERENCE_DIR / "bundle_factors.csv"

    with open(filepath, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            data[int(row["wire_count"])] = float(row["bundle_factor"])

    return data


def load_sleeve_ranges() -> list[dict]:
    """Return sleeve fit ranges from the reference CSV."""
    filepath = REFERENCE_DIR / "sleeve_ranges.csv"

    with open(filepath, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        return [
            {
                "sleeve_pn": row["sleeve_pn"],
                "min_diameter_in": float(row["min_diameter_in"]),
                "max_diameter_in": float(row["max_diameter_in"]),
                "wall_thickness_in": float(row["wall_thickness_in"]),
            }
            for row in reader
        ]


def get_wire_diameter(awg: str) -> float:
    """Return the reference wire diameter for an AWG value."""
    wire_diameters = load_wire_diameters()
    if awg not in wire_diameters:
        raise ValueError(f"No wire diameter found for AWG: {awg}")

    return wire_diameters[awg]


def get_wire_spec(awg: str) -> dict:
    """Return the reference spec data for an AWG value."""
    wire_specs = load_wire_specs()
    if awg not in wire_specs:
        raise ValueError(f"No wire spec found for AWG: {awg}")

    return wire_specs[awg]


def get_bundle_factor(wire_count: int) -> float:
    """Return the bundle factor for a given wire count."""
    bundle_factors = load_bundle_factors()
    if wire_count not in bundle_factors:
        raise ValueError(f"No bundle factor found for wire count: {wire_count}")

    return bundle_factors[wire_count]


def calculate_rms_diameter(diameters: list[float]) -> float:
    """Return RMS diameter for a mixed-diameter bundle estimate."""
    if not diameters:
        raise ValueError("At least one diameter is required.")

    return math.sqrt(sum(diameter**2 for diameter in diameters) / len(diameters))


def calculate_bundle_diameter(wire_list: list[dict]) -> float:
    """Estimate bundle diameter using RMS diameter and bundle factor."""
    if not wire_list:
        raise ValueError("Wire list cannot be empty.")

    diameters = [get_wire_diameter(wire["awg"]) for wire in wire_list]
    rms_diameter = calculate_rms_diameter(diameters)
    bundle_factor = get_bundle_factor(len(wire_list))

    return rms_diameter * bundle_factor


def select_sleeve(bundle_diameter: float) -> dict | None:
    """Return the first sleeve whose range fits the bundle diameter."""
    sleeves = load_sleeve_ranges()

    for sleeve in sleeves:
        if sleeve["min_diameter_in"] <= bundle_diameter <= sleeve["max_diameter_in"]:
            return sleeve

    return None


def round_up_to_half_foot(length_ft: float) -> float:
    """Round a length in feet up to the nearest 0.5 ft."""
    return math.ceil(length_ft * 2) / 2


def calculate_sleeve_length(cable_length_ft: float, runs: int = 1) -> dict:
    """Return sleeve length with spreadsheet-style margin and tolerance."""
    if cable_length_ft <= 0:
        raise ValueError("Cable length must be greater than zero.")

    if runs <= 0:
        raise ValueError("Number of runs must be greater than zero.")

    cable_length_in = cable_length_ft * 12
    adjusted_per_run_in = (cable_length_in * 1.03) + 6
    total_length_in = adjusted_per_run_in * runs
    total_length_ft = total_length_in / 12
    rounded_length_ft = round_up_to_half_foot(total_length_ft)

    return {
        "base_length_ft": cable_length_ft,
        "base_length_in": cable_length_in,
        "runs": runs,
        "margin_percent": 3.0,
        "tolerance_in": 6.0,
        "sleeve_length_in": total_length_in,
        "sleeve_length_ft": rounded_length_ft,
        "sleeve_length_note": "Sleeve length includes 3% margin and 6 in tolerance, rounded up to nearest 0.5 ft",
    }


def get_packaging_data(wire_list: list[dict]) -> dict:
    """Return bundle-diameter and sleeve-selection data for a wire list."""
    bundle_diameter = calculate_bundle_diameter(wire_list)
    sleeve = select_sleeve(bundle_diameter)
    sleeve_length_data = calculate_sleeve_length(float(wire_list[0]["length"]))

    if sleeve is None:
        return {
            "bundle_diameter_in": bundle_diameter,
            "bundle_diameter_method": "Bundle diameter estimated using RMS wire diameter and bundle factor",
            "recommended_sleeve_pn": "No matching sleeve",
            "has_valid_sleeve": False,
            "packaging_warning": (
                "No sleeve range found for bundle diameter "
                f"{bundle_diameter:.3f} in. Wire design remains valid, but sleeve "
                "selection requires manual review."
            ),
            "sleeve_min_diameter_in": None,
            "sleeve_max_diameter_in": None,
            "sleeve_wall_thickness_in": None,
            "sleeve_length_ft": sleeve_length_data["sleeve_length_ft"],
            "sleeve_length_in": sleeve_length_data["sleeve_length_in"],
            "sleeve_length_note": sleeve_length_data["sleeve_length_note"],
            "margin_percent": sleeve_length_data["margin_percent"],
            "tolerance_in": sleeve_length_data["tolerance_in"],
        }

    return {
        "bundle_diameter_in": bundle_diameter,
        "bundle_diameter_method": "Bundle diameter estimated using RMS wire diameter and bundle factor",
        "recommended_sleeve_pn": sleeve["sleeve_pn"],
        "has_valid_sleeve": True,
        "packaging_warning": "",
        "sleeve_min_diameter_in": sleeve["min_diameter_in"],
        "sleeve_max_diameter_in": sleeve["max_diameter_in"],
        "sleeve_wall_thickness_in": sleeve["wall_thickness_in"],
        "sleeve_length_ft": sleeve_length_data["sleeve_length_ft"],
        "sleeve_length_in": sleeve_length_data["sleeve_length_in"],
        "sleeve_length_note": sleeve_length_data["sleeve_length_note"],
        "margin_percent": sleeve_length_data["margin_percent"],
        "tolerance_in": sleeve_length_data["tolerance_in"],
    }
