"""Mapping logic for converting electrical inputs into wire selections."""

from modules.awg import get_awg, get_design_awg
from modules.packaging import get_wire_spec

DEFAULT_AWG_COLOR_MAP = {
    "22 AWG": "white",
    "20 AWG": "blue",
    "18 AWG": "red",
    "16 AWG": "yellow",
    "14 AWG": "green",
    "12 AWG": "black",
    "10 AWG": "white",
    "8 AWG": "blue",
    "6 AWG": "red",
    "4 AWG": "yellow",
    "2 AWG": "green",
}

COLOR_CODE_MAP = {
    "black": "BLK",
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
    if awg not in DEFAULT_AWG_COLOR_MAP:
        raise ValueError(f"No attribute mapping found for AWG: {awg}")

    # This replaces manual lookup of standard wire attributes and part numbers.
    default_color = DEFAULT_AWG_COLOR_MAP[awg]
    attributes = {
        "color": default_color,
        "wire_pn": build_wire_part_number(awg, default_color),
    }

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


def build_engineering_note(current: float, awg: str, length: float, base_note: str = "") -> str:
    """Return a concise engineering note for one wire row."""
    notes = []
    if base_note:
        notes.append(base_note)

    spec = get_wire_spec(awg)
    ampacity = float(spec["ampacity_a"])
    load_ratio = current / ampacity

    if length > 15:
        notes.append("Long run: review voltage drop")
    elif length > 10:
        notes.append("Voltage drop review recommended")

    if load_ratio >= 0.9:
        notes.append("Current is close to ampacity limit")

    return "; ".join(dict.fromkeys(notes))


def generate_wire_list(signals: list[dict], length: float) -> list[dict]:
    """Return a structured wire list with a shared wire length."""
    if not isinstance(length, (int, float)):
        raise TypeError("Length must be a number.")

    if length <= 0:
        raise ValueError("Length must be greater than zero.")

    wire_list = []
    for signal in signals:
        design_awg, base_note = get_design_awg(signal["current"], length)
        attributes = map_attributes(design_awg, signal.get("color"))
        note = build_engineering_note(
            float(signal["current"]),
            design_awg,
            float(length),
            base_note,
        )

        # This turns repeated table lookups into a consistent wire-list row
        # that can be used directly for downstream BOM generation.
        wire_list.append(
            {
                "signal_name": signal["signal_name"],
                "current": signal["current"],
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
