"""Flask application for the minimal spreadsheet."""

import re
from flask import Flask, request, jsonify, render_template
from engine import Spreadsheet

app = Flask(__name__)

_sheet = Spreadsheet()

_CELL_RE = re.compile(r'^([A-Ja-j])(10|[1-9])$')


def reset_state():
    """Reset spreadsheet state (used by test fixtures)."""
    global _sheet
    _sheet = Spreadsheet()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/cells', methods=['GET'])
def get_cells():
    return jsonify({'cells': _sheet.get_all_cells()})


@app.route('/cells', methods=['POST'])
def post_cells():
    data = request.get_json(force=True)
    if not data or 'cell' not in data:
        return jsonify({'error': 'missing cell field'}), 400

    cell_id = data['cell']
    if not _CELL_RE.match(cell_id):
        return jsonify({'error': 'invalid cell identifier'}), 400

    raw = data.get('raw', '')
    changed = _sheet.set_cell(cell_id, raw)
    return jsonify({'cells': changed})


if __name__ == '__main__':
    app.run(debug=True)
