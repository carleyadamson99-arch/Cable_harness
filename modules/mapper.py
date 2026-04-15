"""Mapping logic for converting electrical inputs into wire selections."""

from modules.awg import get_awg, get_design_awg

ATTRIBUTE_MAP = {
    "22 AWG": {
        "color": "white",
        "wire_pn": "WIRE-22-WHT-001",
    },
    "20 AWG": {
        "color": "blue",
        "wire_pn": "WIRE-20-BLU-001",
    },
    "18 AWG": {
        "color": "red",
        "wire_pn": "WIRE-18-RED-001",
    },
    "16 AWG": {
        "color": "yellow",
        "wire_pn": "WIRE-16-YEL-001",
    },
    "14 AWG": {
        "color": "green",
        "wire_pn": "WIRE-14-GRN-001",
    },
}

COLOR_CODE_MAP = {
    "white": "WHT",
    "blue": "BLU",
    "red": "RED",
    "yellow": "YEL",
    "green": "GRN",
}


def get_available_colors() -> list[str]:
    """Return the supported user-selectable wire colors."""
    return list(COLOR_CODE_MAP)


def build_wire_part_number(awg: str, color: str) -> str:
    """Return a part number based on AWG and selected color."""
    if color not in COLOR_CODE_MAP:
        raise ValueError(f"Unsupported wire color: {color}")

    gauge = awg.split()[0]
    return f"WIRE-{gauge}-{COLOR_CODE_MAP[color]}-001"


def map_attributes(awg: str, color: str | None = None) -> dict:
    """Return mapped part attributes for a given AWG value."""
    if awg not in ATTRIBUTE_MAP:
        raise ValueError(f"No attribute mapping found for AWG: {awg}")

    # This replaces manual lookup of standard wire attributes and part numbers.
    attributes = ATTRIBUTE_MAP[awg].copy()

    if not color:
        return attributes

    normalized_color = color.strip().lower()
    attributes["color"] = normalized_color
    attributes["wire_pn"] = build_wire_part_number(awg, normalized_color)
    return attributes


def map_wire(requirement: dict) -> dict:
    """Convert one input requirement into a structured wire record."""
    signal_name = requirement["signal_name"]
    current = requirement["current"]
    awg = get_awg(current)
    attributes = map_attributes(awg, requirement.get("color"))

    return {
        "signal_name": signal_name,
        "current": current,
        "awg": awg,
        "color": attributes["color"],
        "wire_part_number": attributes["wire_pn"],
    }


def build_wire_list(requirements: list[dict]) -> list[dict]:
    """Convert a list of user inputs into a wire list."""
    return [map_wire(requirement) for requirement in requirements]


def process_signals(signals: list[dict]) -> list[dict]:
    """Return a simplified wire selection for each input signal."""
    processed = []

    for signal in signals:
        # For each signal, the tool automates the usual engineer workflow:
        # read the required current, choose the AWG, then pull the mapped part data.
        current = signal["current"]
        awg = get_awg(current)
        attributes = map_attributes(awg, signal.get("color"))
        processed.append(
            {
                "signal_name": signal["signal_name"],
                "current": current,
                "awg": awg,
                "color": attributes["color"],
                "wire_pn": attributes["wire_pn"],
            }
        )

    return processed


def generate_wire_list(signals: list[dict], length: float) -> list[dict]:
    """Return a structured wire list with a shared wire length."""
    if not isinstance(length, (int, float)):
        raise TypeError("Length must be a number.")

    if length <= 0:
        raise ValueError("Length must be greater than zero.")

    wire_list = []
    for signal in signals:
        design_awg, note = get_design_awg(signal["current"], length)
        attributes = map_attributes(design_awg, signal.get("color"))

        # This turns repeated table lookups into a consistent wire-list row
        # that can be used directly for downstream BOM generation.
        wire_list.append(
            {
                "signal_name": signal["signal_name"],
                "awg": design_awg,
                "color": attributes["color"],
                "wire_pn": attributes["wire_pn"],
                "length": length,
                "note": note,
            }
        )

    return wire_list


def check_voltage_flag(length: float) -> str:
    """Return a simple voltage drop warning for longer cable runs."""
    if length > 15:
        return "Voltage drop check strongly recommended for this cable length"
    if length > 10:
        return "Voltage drop check recommended"

    return ""
