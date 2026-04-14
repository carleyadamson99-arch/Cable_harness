"""Simple Streamlit interface for the cable harness prototype."""

import streamlit as st

from modules.mapper import check_voltage_flag, generate_wire_list
from modules.output import (
    format_connection_diagram,
    format_connection_summary,
    generate_bom,
)


def build_signal_inputs(conductor_count: int) -> list[dict]:
    """Collect signal inputs from the Streamlit form."""
    signals = []

    for index in range(1, conductor_count + 1):
        st.subheader(f"Conductor {index}")
        signal_name = st.text_input(
            f"Signal name {index}",
            key=f"signal_name_{index}",
            value=f"SIGNAL_{index}",
        )
        current = st.number_input(
            f"Current {index} (A)",
            min_value=0.1,
            step=0.5,
            key=f"current_{index}",
        )
        signals.append({"signal_name": signal_name.strip(), "current": float(current)})

    return signals


def format_bom_rows(bom: dict) -> list[dict]:
    """Convert BOM data into table rows for display."""
    return [
        {"Part Number": part_number, "Quantity": quantity}
        for part_number, quantity in sorted(bom["wire"].items())
    ]


def main() -> None:
    """Render the Streamlit app and run the cable design pipeline."""
    st.set_page_config(page_title="Cable Harness Tool", layout="centered")
    st.title("Cable Harness Tool")
    st.caption("Generate a wire list and BOM from simple cable design inputs.")

    conductor_count = st.number_input(
        "Number of conductors",
        min_value=1,
        step=1,
        value=3,
    )
    signals = build_signal_inputs(int(conductor_count))
    cable_length = st.number_input(
        "Cable length",
        min_value=0.1,
        step=0.5,
        value=12.0,
    )

    if st.button("Generate Cable Design", type="primary"):
        try:
            wire_list = generate_wire_list(signals, float(cable_length))
            bom = generate_bom(wire_list)
            voltage_flag = check_voltage_flag(float(cable_length))
        except ValueError as error:
            st.error(str(error))
            return

        st.subheader("Wire List")
        st.table(wire_list)

        st.subheader("Bill of Materials")
        st.table(format_bom_rows(bom))

        st.subheader("Connection Summary")
        st.text(format_connection_summary(wire_list))

        st.subheader("Connection Diagram")
        st.text(format_connection_diagram(wire_list))

        if voltage_flag:
            st.warning(voltage_flag)


if __name__ == "__main__":
    main()
