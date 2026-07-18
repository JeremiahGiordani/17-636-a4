# Running the Mini Spreadsheet

## Prerequisites
- Python 3.10+ (developed on 3.14)

## Setup
```bash
git clone https://github.com/JeremiahGiordani/17-636-a4.git
cd 17-636-a4
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run the app
```bash
python app.py
```
Then open **http://127.0.0.1:5000** in a browser.

> macOS note: port 5000 is used by the AirPlay Receiver. Either turn it off
> (System Settings → General → AirDrop & Handoff → "AirPlay Receiver"), or run
> on another port:
> ```bash
> flask --app app run --port 5001
> ```

## Use it
Click any cell and type either:
- a **value** — e.g. `42`, `3.14`, `-7`
- a **formula** starting with `=`:
  - arithmetic: `=A1+B2*3`, `=(A1+B1)/2`
  - functions & ranges: `=SUM(A1:A5)`, `=AVG(A1:A3)`, `=MAX(A1:A10)`, `=COUNT(A1:A5)`
  - conditionals: `=IF(A1>10, 100, 0)`, `=IF(SUM(A1:A2)>5, 1, 0)`

Press Enter. Every cell that depends on your edit recalculates automatically.
Errors (division by zero, circular references, bad formulas) show as `ERR`.

## Run the tests
```bash
python -m pytest        # 55 tests: 27 base + 28 extension
```
