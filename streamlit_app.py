"""Streamlit interface for the cable harness prototype."""

from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from modules.mapper import check_voltage_flag, generate_wire_list, get_available_colors
from modules.packaging import get_packaging_data, get_wire_spec
from modules.output import build_bom_csv_text, build_wire_list_csv_text, generate_bom

COLOR_HEX = {
    "black": "#2f3443",
    "red": "#ff5f6d",
    "blue": "#45a7ff",
    "white": "#d8e1f0",
    "yellow": "#f6bf4f",
    "green": "#38c793",
}
AUTO_COLOR_LABEL = "Auto (Recommended)"
LOGO_PATH = Path(__file__).resolve().parent / "CA_LOGO.png"


def inject_styles() -> None:
    """Apply custom styling for a darker, more polished interface."""
    st.markdown(
        """
        <style>
        :root {
            --ui-font: "Avenir Next LT Pro", "Avenir Next", Avenir, "Segoe UI", sans-serif;
        }
        html {
            color-scheme: dark !important;
            background: #0f1017 !important;
        }
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(108, 76, 224, 0.16), transparent 24%),
                radial-gradient(circle at top right, rgba(53, 138, 255, 0.12), transparent 22%),
                linear-gradient(180deg, #0f1017 0%, #14151f 55%, #161726 100%);
            color: #e4e8f1;
            font-family: var(--ui-font);
        }
        .block-container {
            max-width: 1380px;
            padding-top: 3.6rem;
            padding-bottom: 1.8rem;
        }
        html, body, [class*="css"], [data-testid="stAppViewContainer"], [data-testid="stMarkdownContainer"] {
            font-family: var(--ui-font) !important;
            background-color: transparent !important;
        }
        h1, h2, h3 {
            color: #f5f7fb;
            font-family: var(--ui-font) !important;
        }
        .section-label {
            color: #9aa4bd;
            text-transform: uppercase;
            letter-spacing: 0.22em;
            font-size: 0.72rem;
            margin-bottom: 0.5rem;
        }
        .copy-block {
            color: #b3bdd3;
            font-size: 0.93rem;
            line-height: 1.62;
            margin-bottom: 0.9rem;
            max-width: 46rem;
        }
        .metric-card {
            padding: 0.85rem 0.95rem 0.9rem 0.95rem;
            min-height: 168px;
            height: 168px;
            border: 1px solid rgba(120, 126, 148, 0.35);
            background: linear-gradient(180deg, rgba(28, 30, 44, 0.96), rgba(21, 23, 34, 0.96));
            border-radius: 14px;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            overflow: hidden;
        }
        .metric-label {
            color: #9aa4bd;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-size: 0.69rem;
            margin-bottom: 0.45rem;
        }
        .metric-value {
            color: #f8fbff;
            font-size: 1.24rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
            line-height: 1.18;
            overflow-wrap: anywhere;
            word-break: break-word;
            min-height: 3.6rem;
        }
        .metric-note {
            color: #afb8ca;
            font-size: 0.8rem;
            line-height: 1.3;
            min-height: 3.1rem;
            overflow-wrap: anywhere;
            word-break: break-word;
            margin-top: auto;
        }
        [data-testid="stForm"] {
            border: 1px solid rgba(103, 110, 131, 0.22);
            background: linear-gradient(180deg, rgba(20, 22, 33, 0.92), rgba(15, 17, 27, 0.92));
            border-radius: 18px;
            padding: 1rem 1rem 1.15rem 1rem;
            box-shadow: 0 14px 40px rgba(5, 7, 13, 0.16);
        }
        [data-testid="stForm"] > div {
            gap: 0.45rem;
        }
        [data-testid="stForm"] [data-testid="stVerticalBlock"] > div {
            gap: 0.4rem;
        }
        [data-testid="stForm"] input {
            background: rgba(16, 18, 28, 0.98) !important;
            color: #ffffff !important;
            border: 1px solid rgba(128, 138, 170, 0.6) !important;
            border-radius: 10px !important;
            min-height: 2.8rem;
            font-size: 1rem !important;
            font-weight: 600 !important;
            box-shadow: inset 0 0 0 1px rgba(255,255,255,0.03);
            padding-left: 0.8rem !important;
        }
        [data-baseweb="select"] > div {
            background: rgba(16, 18, 28, 0.98) !important;
            border: 1px solid rgba(128, 138, 170, 0.6) !important;
            border-radius: 10px !important;
            min-height: 2.8rem;
            box-shadow: inset 0 0 0 1px rgba(255,255,255,0.03);
            padding-left: 0.15rem !important;
        }
        [data-baseweb="select"] * {
            color: #f8fbff !important;
            font-size: 0.98rem !important;
            font-weight: 600 !important;
        }
        [role="listbox"], [data-baseweb="menu"] {
            background: rgba(16, 18, 28, 0.98) !important;
            border: 1px solid rgba(128, 138, 170, 0.35) !important;
            border-radius: 12px !important;
            box-shadow: 0 18px 38px rgba(4, 7, 12, 0.44) !important;
        }
        [role="option"] {
            color: #f4f7fc !important;
            background: transparent !important;
            font-weight: 600 !important;
        }
        [role="option"][aria-selected="true"],
        [role="option"]:hover {
            background: rgba(66, 92, 173, 0.28) !important;
        }
        [data-baseweb="base-input"] input::placeholder,
        [data-testid="stForm"] input::placeholder {
            color: #c7cfde !important;
            opacity: 1 !important;
        }
        [data-testid="stForm"] input:focus,
        [data-baseweb="select"] > div:focus-within {
            border-color: rgba(161, 188, 255, 0.9) !important;
            box-shadow: 0 0 0 1px rgba(161, 188, 255, 0.45), 0 0 18px rgba(74, 109, 214, 0.18) !important;
        }
        [data-testid="stForm"] label p {
            color: #ccd4e5 !important;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            font-size: 0.70rem !important;
        }
        [data-testid="stNumberInput-stepUp"], [data-testid="stNumberInput-stepDown"],
        [data-testid="stNumberInput-stepUp"] svg, [data-testid="stNumberInput-stepDown"] svg {
            color: #f5f7fb !important;
            fill: #f5f7fb !important;
        }
        [data-testid="stNumberInput-stepUp"], [data-testid="stNumberInput-stepDown"] {
            border-radius: 8px !important;
            background: rgba(29, 33, 48, 0.98) !important;
            border-left: 1px solid rgba(128, 138, 170, 0.28) !important;
        }
        [data-testid="stNumberInput-stepUp"]:hover, [data-testid="stNumberInput-stepDown"]:hover {
            background: rgba(53, 59, 83, 0.98) !important;
        }
        .stButton button, .stFormSubmitButton button {
            background: linear-gradient(180deg, #cf6b73, #8c3142) !important;
            color: #fff !important;
            border: 1px solid rgba(255, 158, 167, 0.3) !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            padding: 0.82rem 1.3rem !important;
            box-shadow: 0 12px 32px rgba(161, 58, 77, 0.28);
            letter-spacing: 0.03em;
        }
        .divider {
            height: 1px;
            background: linear-gradient(90deg, rgba(113,120,141,0), rgba(113,120,141,0.4), rgba(113,120,141,0));
            margin: 1rem 0 1.1rem 0;
        }
        .wire-card {
            border: 1px solid rgba(103, 110, 131, 0.22);
            border-radius: 18px;
            background: linear-gradient(180deg, rgba(25, 27, 39, 0.98), rgba(19, 21, 31, 0.98));
            overflow: hidden;
            box-shadow: 0 14px 40px rgba(5, 7, 13, 0.22);
        }
        .wire-card-header {
            border-bottom: 1px solid rgba(103, 110, 131, 0.22);
            padding: 0.82rem 1.05rem;
            color: #9aa4bd;
            text-transform: uppercase;
            letter-spacing: 0.2em;
            font-size: 0.72rem;
        }
        .wire-card-body {
            padding: 0.75rem 1rem 0.95rem 1rem;
        }
        .text-panel {
            padding: 0.95rem 1rem;
            border-radius: 14px;
            background: rgba(18, 20, 31, 0.88);
            border: 1px solid rgba(103, 110, 131, 0.2);
            white-space: pre-wrap;
            font-family: Consolas, "Courier New", monospace;
            line-height: 1.7;
            color: #dce3ef;
        }
        [data-testid="stDataFrame"], [data-testid="stTable"] {
            border: 1px solid rgba(103, 110, 131, 0.2);
            border-radius: 14px;
            overflow: hidden;
        }
        [data-testid="stDataFrame"] {
            margin-top: 0.15rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def build_signal_inputs(conductor_count: int) -> list[dict]:
    """Collect signal inputs from the Streamlit form."""
    signals = []
    selectable_colors = [AUTO_COLOR_LABEL] + [
        color.title() for color in get_available_colors()
    ]

    header_cols = st.columns([1.45, 0.8, 0.95], gap="small")
    with header_cols[0]:
        st.markdown('<div class="section-label">Signal Name</div>', unsafe_allow_html=True)
    with header_cols[1]:
        st.markdown('<div class="section-label">Current (A)</div>', unsafe_allow_html=True)
    with header_cols[2]:
        st.markdown('<div class="section-label">Color</div>', unsafe_allow_html=True)

    for index in range(1, conductor_count + 1):
        left, middle, right = st.columns([1.45, 0.8, 0.95], gap="small")
        with left:
            signal_name = st.text_input(
                f"Signal name {index}",
                key=f"signal_name_{index}",
                value=f"SIGNAL {index}",
                label_visibility="collapsed",
            )
        with middle:
            current = st.number_input(
                f"Current {index} (A)",
                min_value=0.1,
                step=0.5,
                key=f"current_{index}",
                value=1.0,
                label_visibility="collapsed",
            )
        with right:
            color_choice = st.selectbox(
                f"Wire color {index}",
                options=selectable_colors,
                key=f"color_{index}",
                index=0,
                label_visibility="collapsed",
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


def to_wire_dataframe(wire_list: list[dict]) -> pd.DataFrame:
    """Return a display-friendly wire details table."""
    rows = []

    for index, wire in enumerate(wire_list, start=1):
        spec = get_wire_spec(wire["awg"])
        current = float(wire["current"])
        resistance = spec["resistance_ohm_per_kft"] * wire["length"] / 1000
        voltage_drop = current * resistance
        voltage_drop_pct = (voltage_drop / 12.0) * 100
        status = "OK" if current <= spec["ampacity_a"] and voltage_drop_pct < 3 else "CHECK"

        rows.append(
            {
                "FN": index,
                "Color": wire["color"].title(),
                "Wire Label": wire["signal_name"],
                "Gauge": wire["awg"],
                "OD": f"{spec['od_in']:.3f} in",
                "Current / Ampacity": f"{current:.1f} A / {spec['ampacity_a']:.1f} A",
                "Resistance": f"{resistance:.4f} ohm",
                "Voltage Drop": f"{voltage_drop:.3f}V / {voltage_drop_pct:.2f}%",
                "Status": status,
                "Engineering Note": wire.get("note", ""),
            }
        )

    return pd.DataFrame(rows)


def to_bom_dataframe(bom: dict) -> pd.DataFrame:
    """Return a display-friendly BOM table."""
    rows = []
    fn = 1

    for part_number, quantity in sorted(bom["wire"].items()):
        rows.append(
            {
                "FN": fn,
                "Description": "Hook-up wire",
                "P/N": part_number,
                "QTY": f"{quantity:.1f}",
            }
        )
        fn += 1

    for part_number, quantity in sorted(bom.get("sleeve", {}).items()):
        rows.append(
            {
                "FN": fn,
                "Description": "Shrink sleeve",
                "P/N": part_number,
                "QTY": f"{quantity:.1f}",
            }
        )
        fn += 1

    return pd.DataFrame(rows)


def render_harness_visual(
    wire_list: list[dict], packaging_data: dict, length: float
) -> None:
    """Render a sleek harness-side visual using inline SVG."""
    conductor_count = len(wire_list)
    label_font_size = 13 if conductor_count <= 6 else 11
    awg_font_size = 14 if conductor_count <= 6 else 12
    line_step = 18 if conductor_count <= 6 else 16
    top_margin = 76
    harness_start_x = 238
    harness_end_x = 676
    center_y = top_margin + ((conductor_count - 1) * line_step / 2)
    start_y = top_margin
    sleeve_height = max(38, (conductor_count - 1) * line_step + 28)
    sleeve_y = center_y - (sleeve_height / 2)
    label_left_x = 172
    awg_right_x = 710
    body_height = max(248, 184 + conductor_count * 22)
    footer_y = body_height - 54
    footer_value_y = body_height - 34

    stripe_lines = []
    left_labels = []
    right_labels = []

    for index, wire in enumerate(wire_list):
        y = start_y + index * line_step
        color = COLOR_HEX.get(wire["color"].lower(), "#d8e1f0")
        signal_name = escape(wire["signal_name"])
        awg = escape(wire["awg"])
        stripe_lines.append(
            f'<line x1="{harness_start_x}" y1="{y}" x2="{harness_end_x}" y2="{y}" '
            f'stroke="{color}" stroke-width="4" stroke-linecap="round" />'
        )
        left_labels.append(
            f'<text x="{label_left_x}" y="{y + 4}" text-anchor="end" fill="#eef3fb" '
            f'font-size="{label_font_size}" font-family="monospace" font-weight="600" '
            f'stroke="#0d1018" stroke-width="1.25" paint-order="stroke">{signal_name}</text>'
        )
        right_labels.append(
            f'<text x="{awg_right_x}" y="{y + 4}" fill="#ffffff" '
            f'font-size="{awg_font_size}" font-family="monospace" font-weight="700" '
            f'letter-spacing="0.4" stroke="#0d1018" stroke-width="1.5" paint-order="stroke">{awg}</text>'
        )

    bundle = packaging_data["bundle_diameter_in"]
    sleeve = escape(packaging_data["recommended_sleeve_pn"])
    svg = f"""
    <svg viewBox="0 0 900 {body_height}" width="100%" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="bodyGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#232735"/>
          <stop offset="20%" stop-color="#4e536a"/>
          <stop offset="50%" stop-color="#747a90"/>
          <stop offset="80%" stop-color="#4e536a"/>
          <stop offset="100%" stop-color="#232735"/>
        </linearGradient>
        <linearGradient id="sleeveGlow" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#1f2230"/>
          <stop offset="50%" stop-color="#32384b"/>
          <stop offset="100%" stop-color="#1f2230"/>
        </linearGradient>
      </defs>
      <rect x="18" y="16" width="864" height="{body_height - 32}" rx="18" fill="#181b25" stroke="#2f3443"/>
      <text x="34" y="42" fill="#9aa4bd" font-size="12" letter-spacing="3" font-family="monospace">
        HARNESS SIDE VIEW - WIRE ROUTING
      </text>
      {''.join(left_labels)}
      {''.join(right_labels)}
      <rect x="{harness_start_x}" y="{sleeve_y}" width="{harness_end_x - harness_start_x}" height="{sleeve_height}" rx="18" fill="url(#sleeveGlow)" stroke="#59627a"/>
      <rect x="{harness_start_x - 10}" y="{sleeve_y - 4}" width="18" height="{sleeve_height + 8}" rx="5" fill="url(#bodyGradient)" stroke="#5d6479"/>
      <rect x="{harness_end_x - 8}" y="{sleeve_y - 4}" width="18" height="{sleeve_height + 8}" rx="5" fill="url(#bodyGradient)" stroke="#5d6479"/>
      {''.join(stripe_lines)}
      <line x1="{harness_start_x}" y1="{footer_y}" x2="{harness_end_x + 10}" y2="{footer_y}" stroke="#d09b39" stroke-width="1.6" />
      <line x1="{harness_start_x}" y1="{footer_y - 9}" x2="{harness_start_x}" y2="{footer_y + 9}" stroke="#d09b39" stroke-width="1.6" />
      <line x1="{harness_end_x + 10}" y1="{footer_y - 9}" x2="{harness_end_x + 10}" y2="{footer_y + 9}" stroke="#d09b39" stroke-width="1.6" />
      <text x="{(harness_start_x + harness_end_x + 10) / 2 - 18}" y="{footer_y - 6}" fill="#e0bd72" font-size="12" font-family="monospace">{length:.1f} ft</text>
      <text x="34" y="{footer_y}" fill="#9aa4bd" font-size="12" letter-spacing="2" font-family="monospace">
        SLEEVE
      </text>
      <text x="104" y="{footer_y}" fill="#f2f6fb" font-size="13" font-family="monospace">{sleeve}</text>
      <text x="34" y="{footer_value_y}" fill="#9aa4bd" font-size="12" letter-spacing="2" font-family="monospace">
        BUNDLE OD
      </text>
      <text x="122" y="{footer_value_y}" fill="#f2f6fb" font-size="13" font-family="monospace">{bundle:.3f} in</text>
    </svg>
    """
    st.markdown(
        f"""
        <div class="wire-card">
            <div class="wire-card-header">Harness Routing View</div>
            <div class="wire-card-body">{svg}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    """Render the Streamlit app and run the cable design pipeline."""
    st.set_page_config(page_title="Cable Automator", layout="wide")
    inject_styles()

    left, right = st.columns([0.95, 1.25], gap="large")

    with left:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=280)
        st.markdown(
            '<div class="copy-block">Translate electrical requirements into a wiring diagram, a BOM, packaging recommendation, and wire-detail summary with a streamlined engineering workflow.</div>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Cable Design Inputs</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="copy-block">Enter conductor data on the left, then generate the harness to see the wiring diagram view, wire table, BOM, and packaging recommendations.</div>',
            unsafe_allow_html=True,
        )

        with st.form("design_inputs"):
            top_left, top_right = st.columns(2, gap="medium")
            with top_left:
                conductor_count = st.number_input(
                    "No. of Conductors",
                    min_value=1,
                    step=1,
                    value=3,
                )
            with top_right:
                cable_length = st.number_input(
                    "Length (ft)",
                    min_value=0.1,
                    step=0.5,
                    value=12.0,
                )

            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            signals = build_signal_inputs(int(conductor_count))
            st.markdown("<div style='height: 1.2rem;'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Generate Cable Design", type="primary")

    with right:
        st.markdown('<div class="section-label">Cable Design Outputs</div>', unsafe_allow_html=True)

    if not submitted:
        with right:
            st.markdown(
                """
                <div class="wire-card">
                    <div class="wire-card-header">Output Dashboard</div>
                    <div class="wire-card-body" style="color:#dbe3f0; line-height:1.8;">
                        Generate a design to populate the dashboard summary, harness routing view,
                        wire details, bill of materials, and packaging recommendation.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
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

    with right:
        summary_cols = st.columns(4, gap="small")
        with summary_cols[0]:
            metric_card("Conductors", str(len(wire_list)), "Total wires in harness")
        with summary_cols[1]:
            metric_card("Cable Length", f"{float(cable_length):.1f} ft", "Entered design length")
        with summary_cols[2]:
            metric_card(
                "Bundle Diameter",
                f"{packaging_data['bundle_diameter_in']:.3f} in",
                "Estimated harness bundle size",
            )
        with summary_cols[3]:
            metric_card(
                "Recommended Sleeve",
                packaging_data["recommended_sleeve_pn"],
                "Selected from fit-range reference data",
            )

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        render_harness_visual(wire_list, packaging_data, float(cable_length))

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Wire Details</div>', unsafe_allow_html=True)
        st.dataframe(to_wire_dataframe(wire_list), use_container_width=True, hide_index=True)

        st.markdown("<div style='height: 1rem;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Bill of Materials</div>', unsafe_allow_html=True)
        st.dataframe(to_bom_dataframe(bom), use_container_width=True, hide_index=True)

        st.markdown("<div style='height: 0.6rem;'></div>", unsafe_allow_html=True)
        export_cols = st.columns(2, gap="small")
        with export_cols[0]:
            st.download_button(
                "Download Wire List CSV",
                data=build_wire_list_csv_text(wire_list),
                file_name="wire_list.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with export_cols[1]:
            st.download_button(
                "Download BOM CSV",
                data=build_bom_csv_text(bom),
                file_name="bom.csv",
                mime="text/csv",
                use_container_width=True,
            )

        if voltage_flag:
            st.warning(voltage_flag)
        else:
            st.success("No voltage-drop warning for the current design length.")


if __name__ == "__main__":
    main()
