"""Packaging calculations for bundle diameter and sleeve selection."""

import csv
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


def get_bundle_factor(wire_count: int) -> float:
    """Return the bundle factor for a given wire count."""
    bundle_factors = load_bundle_factors()
    if wire_count not in bundle_factors:
        raise ValueError(f"No bundle factor found for wire count: {wire_count}")

    return bundle_factors[wire_count]


def calculate_bundle_diameter(wire_list: list[dict]) -> float:
    """Estimate bundle diameter using average wire diameter and bundle factor."""
    if not wire_list:
        raise ValueError("Wire list cannot be empty.")

    diameters = [get_wire_diameter(wire["awg"]) for wire in wire_list]
    average_diameter = sum(diameters) / len(diameters)
    bundle_factor = get_bundle_factor(len(wire_list))

    return average_diameter * bundle_factor


def select_sleeve(bundle_diameter: float) -> dict:
    """Return the first sleeve whose range fits the bundle diameter."""
    sleeves = load_sleeve_ranges()

    for sleeve in sleeves:
        if sleeve["min_diameter_in"] <= bundle_diameter <= sleeve["max_diameter_in"]:
            return sleeve

    raise ValueError(
        f"No sleeve range found for bundle diameter: {bundle_diameter:.3f} in"
    )


def get_packaging_data(wire_list: list[dict]) -> dict:
    """Return bundle-diameter and sleeve-selection data for a wire list."""
    bundle_diameter = calculate_bundle_diameter(wire_list)
    sleeve = select_sleeve(bundle_diameter)

    return {
        "bundle_diameter_in": bundle_diameter,
        "recommended_sleeve_pn": sleeve["sleeve_pn"],
        "sleeve_min_diameter_in": sleeve["min_diameter_in"],
        "sleeve_max_diameter_in": sleeve["max_diameter_in"],
        "sleeve_wall_thickness_in": sleeve["wall_thickness_in"],
    }
