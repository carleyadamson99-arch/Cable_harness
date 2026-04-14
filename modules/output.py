"""Output formatting helpers for the cable harness prototype."""

from collections import Counter


def generate_bom(wire_list: list[dict]) -> dict:
    """Return counted wire and sleeve part numbers from a wire list."""
    wire_counts = Counter()
    sleeve_counts = Counter()

    for wire in wire_list:
        wire_counts[wire["wire_pn"]] += 1
        sleeve_counts[wire["sleeve_pn"]] += 1

    return {
        "wire": dict(wire_counts),
        "sleeve": dict(sleeve_counts),
    }


def format_wire_list(wire_list):
    """Return a printable wire list table."""
    lines = [
        "Signal Name | AWG | Color | Wire Part Number | Sleeve Part Number | Length"
    ]
    lines.append("-" * len(lines[0]))

    for wire in wire_list:
        lines.append(
            f"{wire['signal_name']} | "
            f"{wire['awg']} | "
            f"{wire['color']} | "
            f"{wire['wire_pn']} | "
            f"{wire['sleeve_pn']} | "
            f"{wire['length']:.1f}"
        )

    return "\n".join(lines)


def format_bom(wire_list):
    """Return a printable BOM summary based on selected parts."""
    bom = generate_bom(wire_list)

    lines = ["WIRE BOM", "Part Number | Quantity", "----------------------"]

    for part_number, quantity in sorted(bom["wire"].items()):
        lines.append(f"{part_number} | {quantity}")

    lines.append("")
    lines.append("SLEEVE BOM")
    lines.append("Part Number | Quantity")
    lines.append("----------------------")

    for part_number, quantity in sorted(bom["sleeve"].items()):
        lines.append(f"{part_number} | {quantity}")

    return "\n".join(lines)
