"""Run scenario-based cable design checks and write a log file."""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

from modules.mapper import check_voltage_flag, generate_wire_list
from modules.output import build_bom_csv_text, build_wire_list_csv_text, generate_bom
from modules.packaging import get_packaging_data

LOG_DIR = Path("test_logs")

SCENARIOS = [
    {
        "name": "baseline_low_current",
        "description": "Nominal small harness with low current and valid sleeve fit.",
        "signals": [
            {"signal_name": "SIGNAL_1", "current": 1.0, "color": "white"},
            {"signal_name": "SIGNAL_2", "current": 1.0, "color": "white"},
            {"signal_name": "SIGNAL_3", "current": 1.0, "color": "white"},
        ],
        "length_ft": 12.0,
    },
    {
        "name": "long_run_awg_bump",
        "description": "Long cable run should increase AWG and trigger voltage review.",
        "signals": [
            {"signal_name": "PWR_MAIN", "current": 12.0, "color": "black"},
            {"signal_name": "PWR_RETURN", "current": 12.0, "color": "green"},
        ],
        "length_ft": 20.0,
    },
    {
        "name": "mixed_current_bundle",
        "description": "Mixed loads should produce multiple gauges and a normal sleeve fit.",
        "signals": [
            {"signal_name": "CTRL_A", "current": 3.0, "color": "blue"},
            {"signal_name": "CTRL_B", "current": 8.0, "color": "yellow"},
            {"signal_name": "MOTOR_PWR", "current": 25.0, "color": "red"},
            {"signal_name": "MOTOR_RTN", "current": 25.0, "color": "black"},
        ],
        "length_ft": 15.0,
    },
    {
        "name": "no_fit_sleeve_case",
        "description": "Large bundle should keep wire results and warn when no sleeve fits.",
        "signals": [
            {"signal_name": f"PWR_{index}", "current": 115.0}
            for index in range(1, 40)
        ],
        "length_ft": 12.0,
    },
]


def ensure_log_dir() -> Path:
    """Create the log directory when needed."""
    LOG_DIR.mkdir(exist_ok=True)
    return LOG_DIR


def run_scenario(scenario: dict) -> dict:
    """Run one scenario and return a structured result."""
    wire_list = generate_wire_list(scenario["signals"], float(scenario["length_ft"]))
    packaging_data = get_packaging_data(wire_list)
    bom = generate_bom(wire_list, packaging_data)
    voltage_flag = check_voltage_flag(float(scenario["length_ft"]))

    return {
        "name": scenario["name"],
        "description": scenario["description"],
        "status": "PASS",
        "conductor_count": len(wire_list),
        "length_ft": float(scenario["length_ft"]),
        "wire_count": len(wire_list),
        "wire_part_numbers": sorted(bom["wire"]),
        "sleeve_part_numbers": sorted(bom["sleeve"]),
        "packaging_warning": packaging_data.get("packaging_warning", ""),
        "voltage_flag": voltage_flag,
        "wire_csv": build_wire_list_csv_text(wire_list),
        "bom_csv": build_bom_csv_text(bom),
        "packaging": packaging_data,
    }


def run_all_scenarios() -> list[dict]:
    """Run every scenario and capture pass/fail state."""
    results = []

    for scenario in SCENARIOS:
        try:
            results.append(run_scenario(scenario))
        except Exception as error:  # noqa: BLE001 - keep runner simple/readable
            results.append(
                {
                    "name": scenario["name"],
                    "description": scenario["description"],
                    "status": "FAIL",
                    "conductor_count": len(scenario["signals"]),
                    "length_ft": float(scenario["length_ft"]),
                    "wire_count": 0,
                    "wire_part_numbers": [],
                    "sleeve_part_numbers": [],
                    "packaging_warning": "",
                    "voltage_flag": "",
                    "wire_csv": "",
                    "bom_csv": "",
                    "packaging": {},
                    "error": str(error),
                }
            )

    return results


def write_summary_csv(results: list[dict], filepath: Path) -> None:
    """Write a compact CSV summary of scenario outcomes."""
    with open(filepath, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "scenario",
                "status",
                "conductors",
                "length_ft",
                "wire_part_numbers",
                "sleeve_part_numbers",
                "voltage_flag",
                "packaging_warning",
                "error",
            ]
        )
        for result in results:
            writer.writerow(
                [
                    result["name"],
                    result["status"],
                    result["conductor_count"],
                    result["length_ft"],
                    "; ".join(result["wire_part_numbers"]),
                    "; ".join(result["sleeve_part_numbers"]),
                    result.get("voltage_flag", ""),
                    result.get("packaging_warning", ""),
                    result.get("error", ""),
                ]
            )


def write_text_log(results: list[dict], filepath: Path) -> None:
    """Write a readable text log for scenario review."""
    lines = [
        "Cable Harness Scenario Test Log",
        "=" * 32,
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
    ]

    for result in results:
        lines.extend(
            [
                f"Scenario: {result['name']}",
                f"Description: {result['description']}",
                f"Status: {result['status']}",
                f"Conductors: {result['conductor_count']}",
                f"Length (ft): {result['length_ft']:.1f}",
            ]
        )

        if result["status"] == "PASS":
            lines.extend(
                [
                    f"Wire P/Ns: {', '.join(result['wire_part_numbers']) or 'None'}",
                    f"Sleeve P/Ns: {', '.join(result['sleeve_part_numbers']) or 'None'}",
                    f"Voltage Flag: {result.get('voltage_flag', '') or 'None'}",
                    f"Packaging Warning: {result.get('packaging_warning', '') or 'None'}",
                ]
            )
        else:
            lines.append(f"Error: {result.get('error', 'Unknown error')}")

        lines.append("-" * 48)

    filepath.write_text("\n".join(lines), encoding="utf-8")


def write_json_log(results: list[dict], filepath: Path) -> None:
    """Write full scenario output to JSON for easier machine inspection."""
    filepath.write_text(json.dumps(results, indent=2), encoding="utf-8")


def main() -> None:
    """Run all scenarios and write logs to disk."""
    log_dir = ensure_log_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = run_all_scenarios()

    text_log = log_dir / f"scenario_test_log_{timestamp}.txt"
    json_log = log_dir / f"scenario_test_log_{timestamp}.json"
    csv_log = log_dir / f"scenario_test_summary_{timestamp}.csv"

    write_text_log(results, text_log)
    write_json_log(results, json_log)
    write_summary_csv(results, csv_log)

    passed = sum(1 for result in results if result["status"] == "PASS")
    total = len(results)

    print("Scenario test run complete.")
    print(f"Passed: {passed}/{total}")
    print(f"Text log: {text_log}")
    print(f"JSON log: {json_log}")
    print(f"CSV summary: {csv_log}")


if __name__ == "__main__":
    main()
