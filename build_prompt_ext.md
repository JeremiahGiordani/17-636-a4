You are implementing the EXTENSION of the minimal spreadsheet: spreadsheet
functions (SUM, AVG, MIN, MAX, COUNT), ranges (A1:A5), and IF with comparison
operators (> < >= <= = <>). This is ONE iteration of a loop; the repo is your
memory across iterations.

Each run:
1. Read SPEC-ext.md, PLAN-ext.md, progress.md, and the tests in tests/. The FULL
   pytest suite (base tests + tests/test_functions.py) is the definition of done.
2. Run `python3 -m pytest -q` to see what is failing.
3. Implement the next chunk in engine.py: extend the tokenizer/parser for ranges,
   function calls, and comparison operators, and add evaluation for the aggregate
   functions and IF, following SPEC-ext.md / PLAN-ext.md. Keep all base behavior
   working. Use the active venv (.venv); add any new deps to requirements.txt.
4. Do NOT weaken, delete, or trivially rewrite any tests (base or extension), and
   do not break existing base tests. Make the code correct instead.
5. Run `python3 -m pytest -q` again.
6. Commit your changes with a clear message (e.g. "extension build: SUM/AVG over
   ranges").
7. Update progress.md: check off what is done, list what remains.
8. When ALL tests pass (base + extension), mark the extension complete in
   progress.md and commit.

Work in focused increments. Keep going until the entire suite passes.
