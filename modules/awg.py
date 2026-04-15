"""AWG lookup logic for the cable harness prototype."""

import csv
from pathlib import Path

REFERENCE_DIR = Path(__file__).resolve().parent.parent / "reference_data"


def load_awg_ampacity_limits() -> dict[str, float]:
    """Return AWG ampacity limits from the shared wire-spec reference table."""
    filepath = REFERENCE_DIR / "wire_specs.csv"
    limits = {}

    with open(filepath, newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            limits[row["awg"]] = float(row["ampacity_a"])

    return limits


def get_awg_order() -> list[str]:
    """Return supported AWG values ordered from smallest to largest conductor."""
    limits = load_awg_ampacity_limits()
    return sorted(limits, key=lambda awg: int(awg.split()[0]), reverse=True)


def get_awg(current: float) -> str:
    """Return a wire gauge based on the requested current."""
    if not isinstance(current, (int, float)):
        raise TypeError("Current must be a number.")

    if current <= 0:
        raise ValueError("Current must be greater than zero.")

    ampacity_limits = load_awg_ampacity_limits()
    awg_order = get_awg_order()

    # This replaces the manual step of checking a current-vs-AWG reference chart.
    for awg in awg_order:
        if current <= ampacity_limits[awg]:
            return awg

    largest_awg = awg_order[-1]
    max_supported_current = ampacity_limits[largest_awg]
    raise ValueError(
        "Current exceeds the supported prototype range. "
        f"The largest available wire is {largest_awg} at {max_supported_current:.1f} A."
    )


def bump_awg_size(awg: str) -> str:
    """Return the next larger wire size when available."""
    awg_order = get_awg_order()

    if awg not in awg_order:
        raise ValueError(f"Unknown AWG value: {awg}")

    index = awg_order.index(awg)
    if index == len(awg_order) - 1:
        return awg

    return awg_order[index + 1]


def get_design_awg(current: float, length: float) -> tuple[str, str]:
    """Return an AWG recommendation adjusted for longer cable runs."""
    if not isinstance(length, (int, float)):
        raise TypeError("Length must be a number.")

    if length <= 0:
        raise ValueError("Length must be greater than zero.")

    base_awg = get_awg(current)

    # For longer runs, recommend one larger wire size to reduce voltage drop risk.
    if length > 15:
        adjusted_awg = bump_awg_size(base_awg)
        if adjusted_awg != base_awg:
            return adjusted_awg, "AWG increased for longer cable run"

    return base_awg, ""


def select_awg(current: float) -> str:
    """Backward-compatible wrapper for existing code paths."""
    return get_awg(current).split()[0]


if __name__ == "__main__":
    print(get_awg(3.0))
    print(get_awg(8.5))
    print(get_awg(14.0))
    print(get_awg(19.5))
    try:
        print(get_awg(25.0))
    except ValueError as error:
        print(error)
