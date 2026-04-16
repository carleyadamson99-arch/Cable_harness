"""Convert a scenario test JSON log into a demo-friendly HTML report."""

from __future__ import annotations

import csv
import html
import io
import json
import sys
from pathlib import Path


def parse_csv_text(csv_text: str) -> list[dict[str, str]]:
    """Return rows parsed from embedded CSV text."""
    if not csv_text.strip():
        return []

    return list(csv.DictReader(io.StringIO(csv_text)))


def format_list(values: list[str]) -> str:
    """Return a readable string for list values."""
    return ", ".join(values) if values else "None"


def build_summary_rows(results: list[dict]) -> str:
    """Return summary table rows for all scenarios."""
    rows = []
    for result in results:
        status_class = "status-pass" if result["status"] == "PASS" else "status-fail"
        rows.append(
            f"""
            <tr>
              <td>{html.escape(result["name"])}</td>
              <td><span class="status-pill {status_class}">{html.escape(result["status"])}</span></td>
              <td>{result["conductor_count"]}</td>
              <td>{result["length_ft"]:.1f}</td>
              <td>{html.escape(format_list(result.get("wire_part_numbers", [])))}</td>
              <td>{html.escape(format_list(result.get("sleeve_part_numbers", [])))}</td>
              <td>{html.escape(result.get("voltage_flag") or "None")}</td>
            </tr>
            """
        )
    return "\n".join(rows)


def build_detail_section(result: dict) -> str:
    """Return one detailed HTML section for a scenario result."""
    wire_rows = parse_csv_text(result.get("wire_csv", ""))
    bom_rows = parse_csv_text(result.get("bom_csv", ""))
    packaging = result.get("packaging", {})
    status_class = "status-pass" if result["status"] == "PASS" else "status-fail"

    wire_table_rows = "\n".join(
        f"""
        <tr>
          <td>{html.escape(row.get("signal_name", ""))}</td>
          <td>{html.escape(row.get("current", ""))}</td>
          <td>{html.escape(row.get("awg", ""))}</td>
          <td>{html.escape(row.get("color", ""))}</td>
          <td>{html.escape(row.get("wire_pn", ""))}</td>
          <td>{html.escape(row.get("length", ""))}</td>
          <td>{html.escape(row.get("note", ""))}</td>
        </tr>
        """
        for row in wire_rows
    ) or '<tr><td colspan="7">No wire data available.</td></tr>'

    bom_table_rows = "\n".join(
        f"""
        <tr>
          <td>{html.escape(row.get("FN", ""))}</td>
          <td>{html.escape(row.get("description", ""))}</td>
          <td>{html.escape(row.get("part_number", ""))}</td>
          <td>{html.escape(row.get("quantity", ""))}</td>
        </tr>
        """
        for row in bom_rows
    ) or '<tr><td colspan="4">No BOM data available.</td></tr>'

    packaging_warning = result.get("packaging_warning") or packaging.get("packaging_warning") or "None"
    error = result.get("error", "")

    packaging_items = [
        ("Bundle Diameter", f"{packaging.get('bundle_diameter_in', 0):.3f} in" if packaging else "N/A"),
        ("Recommended Sleeve", str(packaging.get("recommended_sleeve_pn", "N/A"))),
        ("Sleeve Qty", f"{packaging.get('sleeve_length_ft', 0):.1f} ft" if packaging else "N/A"),
        ("Voltage Flag", result.get("voltage_flag") or "None"),
        ("Packaging Warning", packaging_warning),
    ]

    packaging_html = "\n".join(
        f"""
        <div class="metric">
          <div class="metric-label">{html.escape(label)}</div>
          <div class="metric-value">{html.escape(value)}</div>
        </div>
        """
        for label, value in packaging_items
    )

    error_html = (
        f'<div class="callout fail">Error: {html.escape(error)}</div>'
        if error
        else ""
    )

    return f"""
    <section class="scenario-card">
      <div class="scenario-header">
        <div>
          <h2>{html.escape(result["name"])}</h2>
          <p>{html.escape(result["description"])}</p>
        </div>
        <span class="status-pill {status_class}">{html.escape(result["status"])}</span>
      </div>
      {error_html}
      <div class="metric-grid">
        {packaging_html}
      </div>
      <div class="table-block">
        <h3>Wire List</h3>
        <table>
          <thead>
            <tr>
              <th>Signal</th>
              <th>Current</th>
              <th>AWG</th>
              <th>Color</th>
              <th>Wire P/N</th>
              <th>Length</th>
              <th>Note</th>
            </tr>
          </thead>
          <tbody>
            {wire_table_rows}
          </tbody>
        </table>
      </div>
      <div class="table-block">
        <h3>Bill of Materials</h3>
        <table>
          <thead>
            <tr>
              <th>FN</th>
              <th>Description</th>
              <th>Part Number</th>
              <th>Quantity</th>
            </tr>
          </thead>
          <tbody>
            {bom_table_rows}
          </tbody>
        </table>
      </div>
    </section>
    """


def build_html(results: list[dict], source_name: str, print_mode: bool = False) -> str:
    """Return a complete HTML report."""
    pass_count = sum(1 for result in results if result["status"] == "PASS")
    detail_sections = "\n".join(build_detail_section(result) for result in results)
    page_max_width = "1500px" if not print_mode else "100%"
    page_padding = "32px 24px 56px" if not print_mode else "18px 18px 28px"
    hero_columns = "1.4fr 1fr" if not print_mode else "1fr 1fr"
    body_background = (
        "linear-gradient(180deg, #10121a 0%, #121522 100%)"
        if not print_mode
        else "#ffffff"
    )
    body_color = "var(--text)" if not print_mode else "#111111"
    card_background = (
        "linear-gradient(180deg, rgba(28, 31, 43, 0.98), rgba(19, 22, 31, 0.98))"
        if not print_mode
        else "#ffffff"
    )
    scenario_background = (
        "linear-gradient(180deg, rgba(24, 27, 38, 0.98), rgba(18, 20, 29, 0.98))"
        if not print_mode
        else "#ffffff"
    )
    table_header_background = "rgba(22, 26, 38, 0.95)" if not print_mode else "#f1f3f8"
    metric_background = "rgba(17, 20, 30, 0.95)" if not print_mode else "#f8f9fc"
    border_color = "var(--border)" if not print_mode else "rgba(25, 35, 52, 0.18)"
    muted_color = "var(--muted)" if not print_mode else "#4e5a70"
    blue_color = "var(--blue)" if not print_mode else "#2d4d8f"
    report_title = "Scenario Test Report" if not print_mode else "Scenario Test Report (Print-Friendly)"
    screen_only = "" if not print_mode else ".screen-only { display: none !important; }"
    print_button = (
        '<button class="print-button screen-only" onclick="window.print()">Print / Save as PDF</button>'
        if print_mode
        else ""
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Scenario Test Report</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #0f1017;
      --panel: #171a24;
      --panel-2: #1d2230;
      --border: rgba(128, 138, 170, 0.24);
      --text: #eef2fb;
      --muted: #aab5cb;
      --green: #3fd27a;
      --red: #ff6b7d;
      --blue: #8eb8ff;
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      font-family: "Avenir Next LT Pro", "Avenir Next", Avenir, "Segoe UI", sans-serif;
      background: {body_background};
      color: {body_color};
    }}
    .page {{
      max-width: {page_max_width};
      margin: 0 auto;
      padding: {page_padding};
    }}
    .hero {{
      display: grid;
      grid-template-columns: {hero_columns};
      gap: 18px;
      margin-bottom: 22px;
    }}
    .card {{
      background: {card_background};
      border: 1px solid {border_color};
      border-radius: 18px;
      padding: 20px 22px;
      box-shadow: 0 14px 34px rgba(3, 6, 12, 0.24);
    }}
    h1 {{
      margin: 0 0 10px;
      font-size: 2rem;
      letter-spacing: 0.02em;
    }}
    p {{
      margin: 0;
      color: {muted_color};
      line-height: 1.6;
    }}
    .meta {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
    }}
    .meta .mini {{
      background: {metric_background};
      border: 1px solid {border_color};
      border-radius: 14px;
      padding: 14px 16px;
    }}
    .mini-label {{
      color: {muted_color};
      font-size: 0.76rem;
      text-transform: uppercase;
      letter-spacing: 0.16em;
      margin-bottom: 8px;
    }}
    .mini-value {{
      font-size: 1.35rem;
      font-weight: 700;
    }}
    .section-title {{
      margin: 0 0 12px;
      font-size: 0.9rem;
      text-transform: uppercase;
      letter-spacing: 0.18em;
      color: {blue_color};
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 0;
    }}
    th, td {{
      text-align: left;
      padding: 10px 12px;
      border-bottom: 1px solid {border_color};
      vertical-align: top;
    }}
    th {{
      color: {muted_color};
      font-size: 0.76rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      background: {table_header_background};
    }}
    td {{
      font-size: 0.92rem;
    }}
    .status-pill {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 72px;
      padding: 6px 10px;
      border-radius: 999px;
      font-size: 0.8rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}
    .status-pass {{
      background: rgba(63, 210, 122, 0.14);
      color: var(--green);
      border: 1px solid rgba(63, 210, 122, 0.28);
    }}
    .status-fail {{
      background: rgba(255, 107, 125, 0.12);
      color: var(--red);
      border: 1px solid rgba(255, 107, 125, 0.28);
    }}
    .scenario-card {{
      background: {scenario_background};
      border: 1px solid {border_color};
      border-radius: 18px;
      padding: 20px 22px 22px;
      margin-top: 18px;
      break-inside: avoid-page;
    }}
    .scenario-header {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: flex-start;
      margin-bottom: 16px;
    }}
    .scenario-header h2 {{
      margin: 0 0 6px;
      font-size: 1.15rem;
    }}
    .metric-grid {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 18px;
    }}
    .metric {{
      background: {metric_background};
      border: 1px solid {border_color};
      border-radius: 14px;
      padding: 12px 14px;
      min-height: 90px;
    }}
    .metric-label {{
      color: {muted_color};
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      margin-bottom: 8px;
    }}
    .metric-value {{
      font-size: 0.94rem;
      font-weight: 600;
      line-height: 1.5;
      word-break: break-word;
    }}
    .table-block {{
      overflow: hidden;
      border: 1px solid {border_color};
      border-radius: 16px;
      margin-top: 14px;
      break-inside: avoid-page;
    }}
    .table-block h3 {{
      margin: 0;
      padding: 14px 16px;
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.16em;
      color: {blue_color};
      border-bottom: 1px solid {border_color};
      background: {table_header_background};
    }}
    .callout {{
      padding: 12px 14px;
      border-radius: 12px;
      margin-bottom: 14px;
      font-size: 0.9rem;
      line-height: 1.5;
    }}
    .callout.fail {{
      background: rgba(255, 107, 125, 0.12);
      border: 1px solid rgba(255, 107, 125, 0.24);
      color: #ffd6dc;
    }}
    .print-button {{
      margin-top: 14px;
      padding: 11px 16px;
      border-radius: 12px;
      border: 1px solid rgba(128, 138, 170, 0.32);
      background: rgba(18, 21, 31, 0.95);
      color: #f3f6fd;
      font-weight: 600;
      cursor: pointer;
    }}
    {screen_only}
    @media print {{
      body {{
        background: #ffffff !important;
        color: #111111 !important;
      }}
      .page {{
        max-width: 100% !important;
        padding: 0 !important;
      }}
      .card, .scenario-card, .table-block, .metric, .meta .mini {{
        background: #ffffff !important;
        color: #111111 !important;
        box-shadow: none !important;
      }}
      .section-title, .mini-label, th, p, .metric-label {{
        color: #445066 !important;
      }}
      th {{
        background: #f1f3f8 !important;
      }}
      .status-pass {{
        color: #136b3b !important;
        background: #edf8f1 !important;
        border-color: #b8e0c7 !important;
      }}
      .status-fail {{
        color: #8d2132 !important;
        background: #feeff2 !important;
        border-color: #f1bec8 !important;
      }}
      .screen-only {{
        display: none !important;
      }}
      .hero {{
        grid-template-columns: 1fr 1fr !important;
      }}
      a {{
        color: #111111 !important;
        text-decoration: none !important;
      }}
    }}
    @media (max-width: 1100px) {{
      .hero, .metric-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <div class="hero">
      <div class="card">
        <div class="section-title">{report_title}</div>
        <h1>Cable Harness Test Results</h1>
        <p>This report converts the scenario JSON log into a readable demo view. It summarizes pass/fail status, packaging outcomes, voltage warnings, and the generated wire/BOM data for each validation case.</p>
        {print_button}
      </div>
      <div class="card">
        <div class="meta">
          <div class="mini">
            <div class="mini-label">Source</div>
            <div class="mini-value">{html.escape(source_name)}</div>
          </div>
          <div class="mini">
            <div class="mini-label">Scenarios</div>
            <div class="mini-value">{len(results)}</div>
          </div>
          <div class="mini">
            <div class="mini-label">Passed</div>
            <div class="mini-value">{pass_count}/{len(results)}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="section-title">Scenario Summary</div>
      <table>
        <thead>
          <tr>
            <th>Scenario</th>
            <th>Status</th>
            <th>Conductors</th>
            <th>Length (ft)</th>
            <th>Wire Part Numbers</th>
            <th>Sleeve Part Numbers</th>
            <th>Voltage Flag</th>
          </tr>
        </thead>
        <tbody>
          {build_summary_rows(results)}
        </tbody>
      </table>
    </div>

    {detail_sections}
  </div>
</body>
</html>
"""


def main() -> None:
    """Build an HTML report from a scenario JSON log."""
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python build_scenario_report.py <scenario_log.json>")

    json_path = Path(sys.argv[1])
    results = json.loads(json_path.read_text(encoding="utf-8"))
    output_path = json_path.with_suffix(".html")
    print_output_path = json_path.with_name(f"{json_path.stem}_print.html")
    latest_output_path = json_path.with_name("latest_report.html")
    latest_print_output_path = json_path.with_name("latest_report_print.html")

    standard_html = build_html(results, json_path.name)
    print_html = build_html(results, json_path.name, print_mode=True)

    output_path.write_text(standard_html, encoding="utf-8")
    print_output_path.write_text(print_html, encoding="utf-8")
    latest_output_path.write_text(standard_html, encoding="utf-8")
    latest_print_output_path.write_text(print_html, encoding="utf-8")

    print(f"HTML report written to {output_path}")
    print(f"Print-friendly report written to {print_output_path}")
    print(f"Latest HTML report written to {latest_output_path}")
    print(f"Latest print-friendly report written to {latest_print_output_path}")


if __name__ == "__main__":
    main()
