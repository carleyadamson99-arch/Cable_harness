# Project Notes

## Project Summary

This project is a Python-based cable harness design prototype for a graduate product development course. The goal is to reduce repetitive manual lookup work in point-to-point cable design by converting electrical inputs into a wire list and bill of materials (BOM).

## Problem Being Solved

Engineers often perform repeated manual steps when designing standard cables:
- look up wire gauge from current
- assign standard wire attributes
- find wire part numbers
- prepare a wire list
- prepare a BOM

This tool automates those repeatable steps for a simple MVP workflow.

## Current Functionality

The current prototype supports:
- user input for number of conductors
- user input for signal name and current per conductor
- user input for cable length
- AWG lookup from current
- color and wire part number mapping
- wire list generation
- BOM generation
- voltage-drop flag for longer runs
- connection summary output
- text-based connection diagram
- CSV export for wire list and BOM
- minimal Streamlit UI

## Current Files

- [main.py](/abs/c:/Users/carby/OneDrive/FINAL_PROJECT/Cable_harness/main.py): terminal-based app orchestrator
- [streamlit_app.py](/abs/c:/Users/carby/OneDrive/FINAL_PROJECT/Cable_harness/streamlit_app.py): simple Streamlit UI
- [modules/awg.py](/abs/c:/Users/carby/OneDrive/FINAL_PROJECT/Cable_harness/modules/awg.py): AWG selection logic
- [modules/mapper.py](/abs/c:/Users/carby/OneDrive/FINAL_PROJECT/Cable_harness/modules/mapper.py): signal processing and wire-list generation
- [modules/output.py](/abs/c:/Users/carby/OneDrive/FINAL_PROJECT/Cable_harness/modules/output.py): BOM generation, formatting, and CSV export
- [README.md](/abs/c:/Users/carby/OneDrive/FINAL_PROJECT/Cable_harness/README.md): project overview and phased roadmap

## Phase Plan

### Phase 1: Core Wire Selection MVP
- input signal name, current, and harness length
- AWG lookup
- color and wire part number mapping
- structured wire list
- wire BOM
- simple voltage-drop flag

### Phase 2: User Interface And Usable Workflow
- replace hardcoded inputs with user prompts or a simple UI
- improve demo readiness
- display wire list and BOM clearly
- support exports
- optionally include a basic connection summary or diagram

### Phase 3: Better Engineering Rules
- temperature derating flag
- improved wire sizing logic
- optional length multiplier logic
- stronger validation and error handling

### Phase 4: Harness Packaging Features
- bundle diameter calculation
- sleeve selection
- sleeve BOM
- more refined material calculations

## Important Decisions Made

- keep the MVP simple and readable
- use hardcoded lookup rules and dictionaries
- avoid external APIs and databases
- keep `main.py` as the orchestrator
- separate logic into small modules
- remove sleeve calculations for now
- prioritize a text-based visual representation over graphics
- move UI/demo improvements earlier in the phase plan

## How To Run

Terminal version:

```powershell
& "C:\Users\carby\AppData\Local\Programs\Python\Python312\python.exe" main.py
```

Streamlit version:

```powershell
& "C:\Users\carby\AppData\Local\Programs\Python\Python312\python.exe" -m streamlit run streamlit_app.py
```

## Likely Next Steps

- improve Streamlit layout and polish
- add CSV download buttons in Streamlit
- add stronger validation for empty signal names
- update README with Streamlit run instructions
- consider simple deployment or local-network sharing for demo purposes
