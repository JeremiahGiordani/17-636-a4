You are building the BASE system of a minimal spreadsheet web app. This is ONE
iteration of a loop; the repo is your memory across iterations.

Each run, do this:

1. Read SPEC.md, PLAN.md, and progress.md to understand the goal and what is
   left. The pytest suite in tests/ is the definition of done.
2. Run `python3 -m pytest -q` to see what is currently failing.
3. Implement or fix the NEXT chunk of application code to make failing tests
   pass, following the interfaces in PLAN.md. Order: formula engine (engine.py)
   first, then the Flask app (app.py) with GET / , GET /cells, POST /cells,
   then the frontend (templates/index.html + static/) so the 10x10 grid works
   in a browser. A Python virtualenv is active (.venv) — use it; if you add a
   dependency, pip-install it and add it to requirements.txt.
4. Do NOT weaken, delete, or trivially rewrite the tests in tests/ to make them
   pass — make the code correct instead. (Only fix a test if it clearly
   contradicts SPEC.md, and say why in the commit.)
5. Run `python3 -m pytest -q` again to check progress.
6. Commit your changes with a clear message, e.g. "base build: implement
   formula engine".
7. Update progress.md: check off what is done, list what remains.
8. If ALL tests pass, confirm app.py serves the grid page, mark the base system
   complete in progress.md, and commit.

Work in focused increments — one meaningful chunk per run. Keep going until the
entire test suite passes.
