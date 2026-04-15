"""Streamlit interface for the cable harness prototype."""

import pandas as pd
import streamlit as st

from modules.mapper import check_voltage_flag, generate_wire_list, get_available_colors
from modules.packaging import get_packaging_data, get_wire_diameter
from modules.output import (
    format_connection_diagram,
    format_connection_summary,
    format_packaging_data,
    generate_bom,
)

COLOR_HEX = {
    "red": "#ff5f6d",
    "blue": "#45a7ff",
    "white": "#d8e1f0",
    "yellow": "#f6bf4f",
    "green": "#38c793",
}

AUTO_COLOR_LABEL = "Auto (Recommended)"


def inject_styles() -> None:
    """Apply custom styling for a darker, more polished interface."""
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(59,130,246,0.18), transparent 30%),
                radial-gradient(circle at top right, rgba(16,185,129,0.14), transparent 28%),
                linear-gradient(180deg, #0b1220 0%, #0f172a 60%, #111827 100%);
            color: #e5edf7;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1220px;
        }
        h1, h2, h3 {
            color: #f8fbff;
            letter-spacing: 0.02em;
        }
        .hero {
            padding: 1.4rem 1.6rem;
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 22px;
            background: linear-gradient(180deg, rgba(17,24,39,0.92), rgba(15,23,42,0.85));
            box-shadow: 0 20px 60px rgba(0,0,0,0.28);
            margin-bottom: 1.2rem;
        }
        .hero-eyebrow {
            font-size: 0.78rem;
            color: #8fa6c2;
            text-transform: uppercase;
            letter-spacing: 0.28em;
            margin-bottom: 0.55rem;
        }
        .hero-title {
            font-size: 2rem;
            font-weight: 700;
            color: #f8fbff;
            margin-bottom: 0.35rem;
        }
        .hero-subtitle {
            color: #a9b8cc;
            font-size: 1rem;
            line-height: 1.6;
            max-width: 52rem;
        }
        .panel {
            padding: 1.1rem 1.15rem;
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 20px;
            background: rgba(15, 23, 42, 0.72);
            box-shadow: 0 18px 46px rgba(0,0,0,0.18);
        }
        .section-label {
            color: #8fa6c2;
            text-transform: uppercase;
            letter-spacing: 0.22em;
            font-size: 0.74rem;
            margin-bottom: 0.65rem;
        }
        .metric-card {
            padding: 0.95rem 1rem;
            border-radius: 18px;
            background: linear-gradient(180deg, rgba(30,41,59,0.95), rgba(15,23,42,0.92));
            border: 1px solid rgba(148, 163, 184, 0.14);
            min-height: 96px;
        }
        .metric-label {
            color: #8fa6c2;
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.18em;
            margin-bottom: 0.6rem;
        }
        .metric-value {
            color: #f8fbff;
            font-size: 1.45rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }
        .metric-note {
            color: #9eb0c8;
            font-size: 0.92rem;
        }
        [data-testid="stDataFrame"], [data-testid="stTable"] {
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid rgba(148, 163, 184, 0.14);
        }
        [data-testid="stForm"] {
            border: 1px solid rgba(148, 163, 184, 0.14);
            border-radius: 20px;
            background: rgba(15, 23, 42, 0.74);
            padding: 1rem 1rem 0.5rem 1rem;
        }
        div[data-baseweb="input"] input, div[data-baseweb="select"] input {
            background-color: rgba(15, 23, 42, 0.9) !important;
            color: #f8fbff !important;
        }
        .stButton button {
            background: linear-gradient(90deg, #1d4ed8, #0f9b8e);
            color: white;
            border: none;
            border-radius: 999px;
            padding: 0.7rem 1.2rem;
            font-weight: 700;
        }
        .text-panel {
            padding: 0.95rem 1rem;
            border-radius: 16px;
            background: rgba(15, 23, 42, 0.62);
            border: 1px solid rgba(148, 163, 184, 0.12);
            white-space: pre-wrap;
            font-family: Consolas, "Courier New", monospace;
            line-height: 1.65;
            color: #dce7f5;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    """Render the app header block."""
    st.markdown(
        """
        <div class="hero">
            <div class="hero-eyebrow">Cable Harness Design Tool</div>
            <div class="hero-title">Point-to-Point Harness Layout</div>
            <div class="hero-subtitle">
                Translate electrical requirements into a clean wire list, BOM, packaging
                recommendation, and connection view with a streamlined engineering workflow.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_signal_inputs(conductor_count: int) -> list[dict]:
    """Collect signal inputs from the Streamlit form."""
    signals = []
    selectable_colors = [AUTO_COLOR_LABEL] + [
        color.title() for color in get_available_colors()
    ]

    for index in range(1, conductor_count + 1):
        left, middle, right = st.columns([1.35, 0.9, 1.05])
        with left:
            signal_name = st.text_input(
                f"Signal name {index}",
                key=f"signal_name_{index}",
                value=f"SIGNAL_{index}",
            )
        with middle:
            current = st.number_input(
                f"Current {index} (A)",
                min_value=0.1,
                step=0.5,
                key=f"current_{index}",
                value=1.0,
            )
        with right:
            color_choice = st.selectbox(
                f"Wire color {index}",
                options=selectable_colors,
                key=f"color_{index}",
                index=0,
            )

        selected_color = ""
        if color_choice != AUTO_COLOR_LABEL:
            selected_color = color_choice.lower()

        signals.append(
            {
                "signal_name": signal_name.strip(),
                "current": float(current),
                "color": selected_color,
            }
        )

    return signals


def format_bom_rows(bom: dict) -> list[dict]:
    """Convert BOM data into table rows for display."""
    rows = [
        {"Part Number": part_number, "Quantity": quantity, "Category": "Wire"}
        for part_number, quantity in sorted(bom["wire"].items())
    ]

    rows.extend(
        {
            "Part Number": part_number,
            "Quantity": quantity,
            "Category": "Sleeve",
        }
        for part_number, quantity in sorted(bom.get("sleeve", {}).items())
    )

    return rows


def validate_signals(signals: list[dict]) -> str:
    """Return a validation error message for bad signal inputs, if any."""
    names = []

    for index, signal in enumerate(signals, start=1):
        signal_name = signal["signal_name"].strip()
        if not signal_name:
            return f"Signal name for conductor {index} cannot be blank."
        names.append(signal_name)

    if len(names) != len(set(names)):
        return "Signal names must be unique."

    return ""


def to_wire_dataframe(wire_list: list[dict]) -> pd.DataFrame:
    """Return a display-friendly wire list table."""
    rows = []
    for wire in wire_list:
        rows.append(
            {
                "Signal": wire["signal_name"],
                "AWG": wire["awg"],
                "Color": wire["color"].title(),
                "Part Number": wire["wire_pn"],
                "Length (ft)": f"{wire['length']:.1f}",
                "OD (in)": f"{get_wire_diameter(wire['awg']):.3f}",
                "Note": wire.get("note", ""),
            }
        )

    return pd.DataFrame(rows)


def metric_card(label: str, value: str, note: str) -> None:
    """Render a compact metric card."""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_harness_visual(wire_list: list[dict], packaging_data: dict, length: float) -> None:
    """Render a simple cable-side visual using inline SVG."""
    stripe_lines = []
    label_lines = []
    center_y = 92
    step = 8
    start_y = center_y - ((len(wire_list) - 1) * step / 2)

    for index, wire in enumerate(wire_list):
        y = start_y + index * step
        color = COLOR_HEX.get(wire["color"].lower(), "#d8e1f0")
        stripe_lines.append(
            f'<line x1="70" y1="{y}" x2="770" y2="{y}" '
            f'stroke="{color}" stroke-width="3" stroke-linecap="round" />'
        )
        label_lines.append(
            f'<text x="84" y="{168 + index * 18}" fill="{color}" font-size="12" '
            f'font-family="monospace">{wire["signal_name"]} / {wire["awg"]}</text>'
        )

    bundle = packaging_data["bundle_diameter_in"]
    sleeve = packaging_data["recommended_sleeve_pn"]
    svg = f"""
    <svg viewBox="0 0 840 220" width="100%" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="cableShell" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#334155"/>
          <stop offset="50%" stop-color="#475569"/>
          <stop offset="100%" stop-color="#334155"/>
        </linearGradient>
      </defs>
      <rect x="16" y="16" width="808" height="188" rx="20" fill="#151c27" stroke="#283245" />
      <text x="36" y="40" fill="#90a4bf" font-size="12" letter-spacing="3" font-family="monospace">
        HARNESS SIDE VIEW
      </text>
      <rect x="60" y="76" width="720" height="32" rx="9" fill="url(#cableShell)" stroke="#7087a6" />
      {''.join(stripe_lines)}
      <rect x="52" y="70" width="16" height="44" rx="3" fill="#263244" />
      <rect x="774" y="70" width="16" height="44" rx="3" fill="#263244" />
      <text x="36" y="96" fill="#9fb2ca" font-size="12" font-family="monospace">A</text>
      <text x="806" y="96" fill="#9fb2ca" font-size="12" font-family="monospace">B</text>
      <line x1="372" y1="122" x2="468" y2="122" stroke="#5f738f" stroke-width="1.5" />
      <text x="390" y="138" fill="#8fa6c2" font-size="12" font-family="monospace">{length:.1f} ft</text>
      <text x="36" y="168" fill="#8fa6c2" font-size="12" letter-spacing="2" font-family="monospace">
        CONDUCTORS
      </text>
      {''.join(label_lines)}
      <text x="560" y="168" fill="#8fa6c2" font-size="12" letter-spacing="2" font-family="monospace">
        PACKAGING
      </text>
      <text x="560" y="186" fill="#dce7f5" font-size="12" font-family="monospace">
        Bundle OD: {bundle:.3f} in
      </text>
      <text x="560" y="202" fill="#dce7f5" font-size="12" font-family="monospace">
        Sleeve: {sleeve}
      </text>
    </svg>
    """
    st.markdown(f'<div class="panel">{svg}</div>', unsafe_allow_html=True)


def main() -> None:
    """Render the Streamlit app and run the cable design pipeline."""
    st.set_page_config(page_title="Cable Harness Tool", layout="wide")
    inject_styles()
    render_hero()

    left, right = st.columns([0.95, 1.45], gap="large")

    with left:
        st.markdown('<div class="section-label">Design Inputs</div>', unsafe_allow_html=True)
        with st.form("design_inputs"):
            conductor_count = st.number_input(
                "Number of conductors",
                min_value=1,
                step=1,
                value=3,
            )
            signals = build_signal_inputs(int(conductor_count))
            cable_length = st.number_input(
                "Cable length (ft)",
                min_value=0.1,
                step=0.5,
                value=12.0,
            )
            submitted = st.form_submit_button("Generate Cable Design", type="primary")

    with right:
        st.markdown('<div class="section-label">Visual Preview</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="panel" style="min-height: 240px;">
                <div style="color:#8fa6c2; text-transform:uppercase; letter-spacing:0.2em; font-size:0.76rem; margin-bottom:0.8rem;">
                    Awaiting Design Generation
                </div>
                <div style="color:#dce7f5; font-size:1rem; line-height:1.7;">
                    Enter conductor data on the left, then generate the harness to see the cable
                    routing view, wire tables, BOM, and packaging recommendation.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if not submitted:
        return

    validation_error = validate_signals(signals)
    if validation_error:
        st.error(validation_error)
        return

    try:
        wire_list = generate_wire_list(signals, float(cable_length))
        packaging_data = get_packaging_data(wire_list)
        bom = generate_bom(wire_list, packaging_data)
        voltage_flag = check_voltage_flag(float(cable_length))
    except ValueError as error:
        st.error(str(error))
        return

    st.markdown("---")
    top_metrics = st.columns(4, gap="medium")
    with top_metrics[0]:
        metric_card("Conductors", str(len(wire_list)), "Total wires in harness")
    with top_metrics[1]:
        metric_card("Cable Length", f"{float(cable_length):.1f} ft", "Entered design length")
    with top_metrics[2]:
        metric_card(
            "Bundle Diameter",
            f"{packaging_data['bundle_diameter_in']:.3f} in",
            "Estimated harness bundle size",
        )
    with top_metrics[3]:
        metric_card(
            "Recommended Sleeve",
            packaging_data["recommended_sleeve_pn"],
            "Selected from fit-range reference data",
        )

    st.markdown("")
    render_harness_visual(wire_list, packaging_data, float(cable_length))

    results_left, results_right = st.columns([1.35, 1], gap="large")

    with results_left:
        st.markdown('<div class="section-label">Wire Details</div>', unsafe_allow_html=True)
        st.dataframe(to_wire_dataframe(wire_list), width="stretch", hide_index=True)

        st.markdown('<div class="section-label">Bill of Materials</div>', unsafe_allow_html=True)
        st.dataframe(
            pd.DataFrame(format_bom_rows(bom)),
            width="stretch",
            hide_index=True,
        )

    with results_right:
        st.markdown('<div class="section-label">Engineering Notes</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="text-panel">{format_packaging_data(packaging_data)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("")
        st.markdown(
            f'<div class="text-panel">{format_connection_summary(wire_list)}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("")
        st.markdown(
            f'<div class="text-panel">{format_connection_diagram(wire_list)}</div>',
            unsafe_allow_html=True,
        )

        if voltage_flag:
            st.warning(voltage_flag)
        else:
            st.success("No voltage-drop warning for the current design length.")


if __name__ == "__main__":
    main()
