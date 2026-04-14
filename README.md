# Cable_harness

Cable Harness is a Python-based prototype tool for point-to-point cable design. The goal is to reduce repetitive manual work involved in selecting wire sizes and part numbers from static reference tables.

The tool takes simple electrical inputs and converts them into a structured wire list and bill of materials (BOM). The project is being developed incrementally, starting with a focused MVP and expanding toward a more complete harness design workflow.

## Problem

Designing standard power cables often requires engineers to repeatedly:
- look up wire gauge from current
- assign standard wire attributes
- select part numbers
- prepare a wire list and BOM

These steps are rule-based and repetitive, which makes them a good target for automation.

## Current MVP Scope

Current inputs:
- signal name
- current rating
- cable or harness length

Current tool behavior:
- AWG lookup based on current
- color lookup
- wire part number lookup
- wire list generation
- wire BOM generation
- simple voltage-drop flag for longer runs

Current outputs:
- wire list
- basic wire BOM
- simple design flag output

## Development Phases

### Phase 1: Core Wire Selection MVP
Status: Complete for prototype

- input signal name, current, and harness length
- AWG lookup
- color and wire part number mapping
- structured wire list
- wire BOM
- simple voltage-drop flag

### Phase 2: User Interface And Usable Workflow
Status: Complete for prototype

- replace hardcoded sample inputs with a simple user input form
- make the tool easier to run and demo
- display wire list and BOM clearly
- add exportable outputs if feasible
- optionally add a basic connection summary or simple diagram view

### Phase 3: Better Engineering Rules
Status: Mostly complete for prototype

- improved wire sizing logic
- length-aware logic for stronger voltage-drop guidance
- optional AWG recommendation bump for longer runs
- stronger validation and error handling
- more meaningful engineering notes in the outputs

### Phase 4: Harness Packaging Features
Status: Partially complete with core packaging prototype

- bundle diameter calculation
- sleeve selection
- sleeve BOM
- more refined material calculations

## Implementation Status

Current prototype coverage by phase:
- Phase 1 is complete at the MVP level
- Phase 2 is complete at the prototype/demo level
- Phase 3 is mostly complete, with room for more advanced engineering rules
- Phase 4 is partially complete, with bundle sizing and sleeve recommendation implemented

Current implemented features include:
- terminal-based workflow
- Streamlit web app
- CSV export
- AWG lookup and part-number mapping
- length-aware wire sizing
- voltage-drop guidance
- validation for blank and duplicate signal names
- connection summary and text-based connection diagram
- bundle diameter calculation
- sleeve recommendation
- sleeve BOM line item

## Project Structure

- [main.py](/abs/c:/Users/carby/OneDrive/FINAL_PROJECT/Cable_harness/main.py): orchestrates the prototype workflow
- [modules/awg.py](/abs/c:/Users/carby/OneDrive/FINAL_PROJECT/Cable_harness/modules/awg.py): AWG lookup logic
- [modules/mapper.py](/abs/c:/Users/carby/OneDrive/FINAL_PROJECT/Cable_harness/modules/mapper.py): mapping and wire-list generation logic
- [modules/output.py](/abs/c:/Users/carby/OneDrive/FINAL_PROJECT/Cable_harness/modules/output.py): BOM generation and display formatting
