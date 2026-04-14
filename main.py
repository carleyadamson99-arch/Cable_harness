"""Entry point for the cable harness MVP prototype."""

from modules.mapper import (
    check_voltage_flag,
    generate_wire_list,
    map_attributes,
    process_signals,
)
from modules.output import format_bom, format_wire_list, generate_bom


def get_sample_inputs() -> tuple[list[dict], float]:
    """Return example signal inputs and a shared cable length."""
    signals = [
        {"signal_name": "DC_PWR", "current": 12.0},
        {"signal_name": "PUMP_FEED", "current": 7.5},
        {"signal_name": "SENSOR_PWR", "current": 3.0},
    ]
    length = 12.0
    return signals, length


def main():
    """Run the full prototype pipeline with sample data."""
    signals, length = get_sample_inputs()

    processed_signals = process_signals(signals)
    for signal in processed_signals:
        map_attributes(signal["awg"])

    wire_list = generate_wire_list(signals, length)
    bom = generate_bom(wire_list)
    voltage_flag = check_voltage_flag(length)

    print("CABLE HARNESS MVP")
    print("=================")
    print(f"Signals: {len(signals)}")
    print(f"Cable Length: {length:.1f}")
    print()
    print("WIRE LIST")
    print(format_wire_list(wire_list))
    print()
    print("BOM")
    print(format_bom(wire_list))
    print()
    print("FLAGS")
    if voltage_flag:
        print(f"- {voltage_flag}")
    else:
        print("- None")


if __name__ == "__main__":
    main()
