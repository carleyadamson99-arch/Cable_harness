# Cable Harness

Cable Harness is a Python-based prototype tool for point-to-point cable design. It is intended to reduce repetitive manual engineering work by converting a small set of electrical inputs into a wire list, a bill of materials (BOM), and basic packaging recommendations.

The project was developed incrementally for a graduate product development course. The current codebase is a working end-to-end prototype with both a terminal workflow and a Streamlit GUI.

## Problem

Designing standard cables often requires engineers to repeatedly:
- look up wire gauge from current
- choose standard wire attributes such as color
- map those selections to part numbers
- prepare a wire list
- prepare a BOM
- estimate packaging such as sleeve selection

These steps are repetitive, rules-based, and easy to perform inconsistently by hand. This tool automates that workflow for a simplified point-to-point cable design use case.

## Current Capabilities

Inputs currently supported:
- number of conductors
- signal name for each conductor
- current for each conductor
- optional wire color override
- cable or harness length

Outputs currently supported:
- wire list
- bill of materials
- bundle diameter estimate
- recommended sleeve
- voltage-drop guidance
- harness routing view in Streamlit
- CSV export for wire list and BOM
- dark-themed GUI tables and direct download buttons

Current implemented logic includes:
- AWG lookup using local reference ampacity values
- expanded AWG coverage from 22 AWG through 2 AWG
- validation for blank and duplicate signal names
- rejection of unsupported current values outside the prototype data range
- length-aware AWG bump for long cable runs
- wire part-number mapping
- per-wire engineering notes in the GUI and wire-list CSV export
- bundle diameter calculation using RMS wire diameter and bundle factor
- sleeve selection from fit-range reference data
- sleeve BOM quantity using margin, tolerance, and rounding rules

## How To Run

Terminal version:

```powershell
& "C:\Users\carby\AppData\Local\Programs\Python\Python312\python.exe" main.py
```

Streamlit version:

```powershell
& "C:\Users\carby\AppData\Local\Programs\Python\Python312\python.exe" -m streamlit run streamlit_app.py
```

## Project Structure

- [main.py](/abs/c:/Users/carby/OneDrive/FINAL_PROJECT/Cable_harness/main.py): terminal-based orchestrator
- [streamlit_app.py](/abs/c:/Users/carby/OneDrive/FINAL_PROJECT/Cable_harness/streamlit_app.py): Streamlit GUI
- [modules/awg.py](/abs/c:/Users/carby/OneDrive/FINAL_PROJECT/Cable_harness/modules/awg.py): AWG lookup and sizing rules
- [modules/mapper.py](/abs/c:/Users/carby/OneDrive/FINAL_PROJECT/Cable_harness/modules/mapper.py): signal processing and wire-list generation
- [modules/output.py](/abs/c:/Users/carby/OneDrive/FINAL_PROJECT/Cable_harness/modules/output.py): BOM generation, formatting, and CSV export
- [modules/packaging.py](/abs/c:/Users/carby/OneDrive/FINAL_PROJECT/Cable_harness/modules/packaging.py): bundle diameter and sleeve selection logic
- [reference_data](/abs/c:/Users/carby/OneDrive/FINAL_PROJECT/Cable_harness/reference_data): simplified engineering lookup tables used by the prototype

## Phase Status

### Phase 1: Core Wire Selection MVP
Status: Complete for prototype

Completed:
- signal, current, and length inputs
- AWG lookup
- wire color and part-number mapping
- structured wire list
- wire BOM
- voltage-drop flag

### Phase 2: User Interface And Usable Workflow
Status: Complete for prototype

Completed:
- terminal workflow
- Streamlit web interface
- formatted wire list and BOM display
- harness routing visualization
- CSV export
- direct CSV download buttons in the GUI
- polished dark-mode interface for demo use
- dark-themed tables and dark download-button styling

### Phase 3: Better Engineering Rules
Status: Complete for current prototype scope

Completed:
- AWG selection tied to local ampacity reference values
- expanded AWG reference coverage through 2 AWG
- unsupported-current validation
- length-aware AWG adjustment for longer cable runs
- stronger signal input validation
- voltage-drop guidance
- per-wire engineering notes in the GUI and CSV output

Future Phase 3 enhancements:
- improve voltage-drop logic from a simple warning into a more explicit engineering calculation or threshold rule
- expand the supported AWG/current range even further if the project grows beyond the current prototype envelope

### Phase 4: Harness Packaging Features
Status: Complete for prototype scope

Completed:
- reference-data extraction from engineering spreadsheets
- bundle diameter calculation using RMS wire diameter and bundle factor
- sleeve recommendation from min/max fit ranges
- sleeve BOM line item
- packaging summary in the tool
- packaging data reflected in the BOM and CSV export flow
- sleeve length logic with 3 percent margin, 6 in tolerance, and rounding to the nearest 0.5 ft
- packaging summary now explains bundle-diameter and sleeve-length methods
- graceful no-fit sleeve handling so the tool still returns wire results, surfaces a packaging warning, and omits unresolved sleeve BOM lines

Future Phase 4 enhancements:
- expose packaging-calculation details more explicitly in the GUI and export outputs if more traceability is needed
- expand packaging coverage if future sleeve families or additional packaging materials are added

## Best Next Improvements

With the four prototype phases now complete, the highest-value next steps are:

1. Improve packaging traceability
- Show packaging calculation details more explicitly in the GUI and exports if reviewers need to trace sleeve quantities and bundle assumptions.

2. Deepen electrical analysis
- Upgrade voltage-drop guidance from a simple review note into a more explicit engineering calculation.

3. Expand packaging scope if needed
- Add future packaging materials or branch-level packaging logic if the prototype grows beyond a single sleeve recommendation.

## Recommended Definition Of "Phase Complete"

To mark the remaining phases as fully complete, I'd recommend using this standard:

- Phase 3 is complete when the engineering rules are data-backed, transparent to the user, and robust across the supported prototype current range.
- Phase 4 is complete when packaging outputs are recommended on-screen, calculated with realistic quantities, exported clearly, and robust when no sleeve fit is available.

## Suggested Next Build Order

If you want to deepen the prototype beyond its current completed state, the cleanest order is:

1. Improve packaging traceability in the GUI and exports.
2. Upgrade voltage-drop guidance into a more explicit calculation.
3. Expand packaging scope only if the project needs more than a single-sleeve workflow.

That path would build on a prototype that already completes all four planned phases.
