"""Entry point for the cable harness MVP prototype."""

from pathlib import Path

from modules.mapper import (
    check_voltage_flag,
    generate_wire_list,
    map_attributes,
    process_signals,
)
from modules.packaging import get_packaging_data
from modules.output import (
    export_bom_csv,
    export_wire_list_csv,
    format_bom_data,
    format_connection_diagram,
    format_connection_summary,
    format_packaging_data,
    format_wire_list,
    generate_bom,
)


def get_positive_int(prompt: str) -> int:
    """Prompt the user until a positive integer is entered."""
    while True:
        user_input = input(prompt).strip()
        try:
            value = int(user_input)
        except ValueError:
            print("Please enter a whole number.")
            continue

        if value <= 0:
            print("Please enter a value greater than zero.")
            continue

        return value


def get_positive_float(prompt: str) -> float:
    """Prompt the user until a positive number is entered."""
    while True:
        user_input = input(prompt).strip()
        try:
            value = float(user_input)
        except ValueError:
            print("Please enter a numeric value.")
            continue

        if value <= 0:
            print("Please enter a value greater than zero.")
            continue

        return value


def get_signal_name(prompt: str, existing_names: set[str]) -> str:
    """Prompt the user until a unique, non-empty signal name is entered."""
    while True:
        signal_name = input(prompt).strip()

        if not signal_name:
            print("Signal name cannot be blank.")
            continue

        if signal_name in existing_names:
            print("Signal name must be unique.")
            continue

        return signal_name


def get_user_inputs() -> tuple[list[dict], float]:
    """Collect signal inputs and cable length from the user."""
    signals = []
    signal_names = set()
    conductor_count = get_positive_int("Enter number of conductors: ")

    for index in range(1, conductor_count + 1):
        signal_name = get_signal_name(
            f"Enter signal name for conductor {index}: ", signal_names
        )
        current = get_positive_float(f"Enter current for {signal_name} (A): ")
        signals.append({"signal_name": signal_name, "current": current})
        signal_names.add(signal_name)

    length = get_positive_float("Enter cable length: ")
    return signals, length


def get_export_paths() -> tuple[str, str]:
    """Collect optional export filenames and folder from the user."""
    output_folder = input(
        "Enter output folder path or press Enter to use the current folder: "
    ).strip()
    folder = Path(output_folder) if output_folder else Path.cwd()
    folder.mkdir(parents=True, exist_ok=True)

    wire_list_name = input(
        "Enter wire list filename or press Enter for wire_list.csv: "
    ).strip()
    bom_name = input("Enter BOM filename or press Enter for bom.csv: ").strip()

    wire_list_filename = wire_list_name or "wire_list.csv"
    bom_filename = bom_name or "bom.csv"

    return str(folder / wire_list_filename), str(folder / bom_filename)


def main() -> None:
    """Run the full prototype pipeline with user-provided data."""
    print("CABLE HARNESS MVP")
    print("=================")
    signals, length = get_user_inputs()

    processed_signals = process_signals(signals)
    for signal in processed_signals:
        map_attributes(signal["awg"])

    wire_list = generate_wire_list(signals, length)
    packaging_data = get_packaging_data(wire_list)
    bom = generate_bom(wire_list, packaging_data)
    voltage_flag = check_voltage_flag(length)

    print()
    print(f"Signals: {len(signals)}")
    print(f"Cable Length: {length:.1f}")
    print()
    print("WIRE LIST")
    print(format_wire_list(wire_list))
    print()
    print("BILL OF MATERIALS")
    print(format_bom_data(bom))
    print()
    print("CONNECTION SUMMARY")
    print(format_connection_summary(wire_list))
    print()
    print("CONNECTION DIAGRAM")
    print(format_connection_diagram(wire_list))
    print()
    print("PACKAGING SUMMARY")
    print(format_packaging_data(packaging_data))
    print()
    print("FLAGS")
    packaging_warning = packaging_data.get("packaging_warning", "")
    if packaging_warning:
        print(f"- {packaging_warning}")
    if voltage_flag:
        print(f"- {voltage_flag}")
    if not packaging_warning and not voltage_flag:
        print("- None")
    print()

    wire_list_path, bom_path = get_export_paths()
    export_wire_list_csv(wire_list, wire_list_path)
    export_bom_csv(bom, bom_path)
    print(f"Exported wire list to {wire_list_path}")
    print(f"Exported BOM to {bom_path}")


if __name__ == "__main__":
    main()
