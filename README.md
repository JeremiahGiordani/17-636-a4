# 17-636 A4 — Loop-Engineered Web App

A small web app built with an AI coding assistant driven by a **loop**
(`loop.sh`), rather than by hand-prompting. Built in two steps (base system +
extension), each in three stages (specify → plan → build), using the loop for
the build stage.

- **What it is:** a minimal browser spreadsheet — a grid of cells holding values or formulas (`=A1+B2*3`), evaluated by a Flask backend, with automatic recalculation of dependent cells.
- **How it was built:** see `prompts.txt` (all prompts), `loop.sh` (the loop),
  and the commit history (one commit per stage).
- **How to run it:** see `running.md`.
- **What we learned:** see `reflection.md`.
