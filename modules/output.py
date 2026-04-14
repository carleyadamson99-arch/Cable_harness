"""Output formatting helpers for the cable harness prototype."""

import csv
from collections import Counter


def generate_bom(wire_list: list[dict], packaging_data: dict | None = None) -> dict:
    """Return counted wire and sleeve part numbers from a wire list."""
    wire_counts = Counter()
    sleeve_counts = Counter()

    for wire in wire_list:
        wire_counts[wire["wire_pn"]] += 1

    if packaging_data:
        sleeve_counts[packaging_data["recommended_sleeve_pn"]] += 1

    return {
        "wire": dict(wire_counts),
        "sleeve": dict(sleeve_counts),
    }


def format_wire_list(wire_list: list[dict]) -> str:
    """Return a printable wire list table."""
    headers = ["Signal Name", "AWG", "Color", "Wire Part Number", "Length", "Note"]
    rows = []

    for wire in wire_list:
        rows.append(
            [
                str(wire["signal_name"]),
                str(wire["awg"]),
                str(wire["color"]),
                str(wire["wire_pn"]),
                f"{wire['length']:.1f}",
                str(wire.get("note", "")),
            ]
        )

    widths = [len(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    header_line = " | ".join(
        header.ljust(widths[index]) for index, header in enumerate(headers)
    )
    separator_line = "-+-".join("-" * width for width in widths)
    lines = [header_line, separator_line]

    for row in rows:
        lines.append(
            " | ".join(value.ljust(widths[index]) for index, value in enumerate(row))
        )

    return "\n".join(lines)


def format_bom_data(bom: dict) -> str:
    """Return a printable BOM summary from grouped BOM data."""
    headers = ["Part Number", "Quantity"]
    rows = [
        [part_number, str(quantity)] for part_number, quantity in sorted(bom["wire"].items())
    ]

    if bom.get("sleeve"):
        rows.extend(
            [part_number, str(quantity)]
            for part_number, quantity in sorted(bom["sleeve"].items())
        )

    widths = [len(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    header_line = " | ".join(
        header.ljust(widths[index]) for index, header in enumerate(headers)
    )
    separator_line = "-+-".join("-" * width for width in widths)
    lines = [header_line, separator_line]

    for row in rows:
        lines.append(
            " | ".join(value.ljust(widths[index]) for index, value in enumerate(row))
        )

    return "\n".join(lines)


def format_bom(wire_list: list[dict]) -> str:
    """Return a printable BOM summary based on selected parts."""
    bom = generate_bom(wire_list)
    return format_bom_data(bom)


def format_connection_summary(wire_list: list[dict]) -> str:
    """Return a simple text summary of each connection."""
    lines = []

    for wire in wire_list:
        lines.append(
            f"{wire['signal_name']} -> {wire['awg']} wire -> {wire['length']:.1f} ft"
        )

    return "\n".join(lines)


def format_connection_diagram(wire_list: list[dict]) -> str:
    """Return a simple text-based connection diagram for demo purposes."""
    lines = []

    for wire in wire_list:
        lines.append(
            f"[SOURCE] --- ({wire['signal_name']}, {wire['awg']}) --- [DESTINATION]"
        )

    return "\n".join(lines)


def format_packaging_data(packaging_data: dict) -> str:
    """Return a printable summary of packaging calculations."""
    lines = [
        f"Bundle Diameter: {packaging_data['bundle_diameter_in']:.3f} in",
        f"Recommended Sleeve: {packaging_data['recommended_sleeve_pn']}",
        (
            "Sleeve Fit Range: "
            f"{packaging_data['sleeve_min_diameter_in']:.3f} in to "
            f"{packaging_data['sleeve_max_diameter_in']:.3f} in"
        ),
        (
            "Sleeve Wall Thickness: "
            f"{packaging_data['sleeve_wall_thickness_in']:.3f} in"
        ),
    ]

    return "\n".join(lines)


def export_wire_list_csv(
    wire_list: list[dict], filename: str = "wire_list.csv"
) -> None:
    """Export the wire list to a CSV file with headers."""
    headers = ["signal_name", "awg", "color", "wire_pn", "length", "note"]

    with open(filename, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(wire_list)


def export_bom_csv(bom: dict, filename: str = "bom.csv") -> None:
    """Export the BOM to a CSV file with headers."""
    with open(filename, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["part_number", "quantity"])

        for part_number, quantity in sorted(bom["wire"].items()):
            writer.writerow([part_number, quantity])

        for part_number, quantity in sorted(bom.get("sleeve", {}).items()):
            writer.writerow([part_number, quantity])
