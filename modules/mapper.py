"""Mapping logic for converting electrical inputs into wire selections."""

from modules.awg import get_awg

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


def map_attributes(awg: str) -> dict:
    """Return mapped part attributes for a given AWG value."""
    if awg not in ATTRIBUTE_MAP:
        raise ValueError(f"No attribute mapping found for AWG: {awg}")

    return ATTRIBUTE_MAP[awg].copy()


def map_wire(requirement: dict) -> dict:
    """Convert one input requirement into a structured wire record."""
    signal_name = requirement["signal_name"]
    current = requirement["current"]
    awg = get_awg(current)
    attributes = map_attributes(awg)

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
        current = signal["current"]
        awg = get_awg(current)
        attributes = map_attributes(awg)
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

    processed_signals = process_signals(signals)

    wire_list = []
    for signal in processed_signals:
        wire_list.append(
            {
                "signal_name": signal["signal_name"],
                "awg": signal["awg"],
                "color": signal["color"],
                "wire_pn": signal["wire_pn"],
                "length": length,
            }
        )

    return wire_list


def check_voltage_flag(length: float) -> str:
    """Return a simple voltage drop warning for longer cable runs."""
    if length > 10:
        return "Voltage drop check recommended"

    return ""
