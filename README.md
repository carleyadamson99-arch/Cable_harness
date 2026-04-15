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

Current implemented logic includes:
- AWG lookup using local reference ampacity values
- validation for blank and duplicate signal names
- rejection of unsupported current values outside the prototype data range
- length-aware AWG bump for long cable runs
- wire part-number mapping
- bundle diameter calculation
- sleeve selection from fit-range reference data
- sleeve BOM quantity based on cable length

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

### Phase 3: Better Engineering Rules
Status: Mostly complete for prototype

Completed:
- AWG selection tied to local ampacity reference values
- unsupported-current validation
- length-aware AWG adjustment for longer cable runs
- stronger signal input validation
- voltage-drop guidance

Remaining to fully close Phase 3:
- add clearer engineering warning messages per wire row in the GUI and CSV output
- support a broader AWG/current reference range so high-current cases do not stop at 14 AWG
- improve voltage-drop logic from a simple warning into a more explicit engineering calculation or threshold rule

### Phase 4: Harness Packaging Features
Status: Core prototype complete, refinement still needed

Completed:
- reference-data extraction from engineering spreadsheets
- bundle diameter calculation
- sleeve recommendation from min/max fit ranges
- sleeve BOM line item
- packaging summary in the tool

Remaining to fully close Phase 4:
- add sleeve length margin and tolerance rules instead of using only entered cable length
- improve bundle sizing fidelity beyond average-diameter estimation
- expose packaging calculations more clearly in export output
- validate edge cases where no sleeve fit is available or where future packaging materials are added

## Best Next Improvements

If the goal is to fully close the unfinished phases, the highest-value next steps are:

1. Expand the AWG reference data
- Add larger supported wire sizes and ampacity values so the tool can handle higher-current cases realistically.

2. Strengthen engineering output visibility
- Add per-wire notes or warnings directly into the GUI tables and CSV exports so users can see why a gauge changed or why a design needs review.

3. Refine sleeve length logic
- Use margin and tolerance rules from the original spreadsheet data so sleeve quantities are more realistic than raw cable length alone.

4. Improve packaging robustness
- Handle no-fit sleeve cases more gracefully and make packaging outputs more explicit in exported deliverables.

## Recommended Definition Of "Phase Complete"

To mark the remaining phases as fully complete, I'd recommend using this standard:

- Phase 3 is complete when the engineering rules are data-backed, transparent to the user, and robust across the supported current range.
- Phase 4 is complete when packaging outputs are not only recommended on-screen, but also calculated with realistic quantities and exported clearly.

## Suggested Next Build Order

The cleanest order to finish the project is:

1. Expand AWG reference coverage and update lookup logic accordingly.
2. Add per-wire engineering notes to GUI tables and CSV outputs.
3. Refine sleeve-length calculation using margin and tolerance rules.
4. Add packaging edge-case handling and clearer packaging export details.

That path would let the README honestly say all four phases are complete for the intended prototype scope.
