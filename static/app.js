const COLS = 'ABCDEFGHIJ'.split('');
const ROWS = 10;

function buildGrid() {
    const tbody = document.querySelector('#grid tbody');
    for (let r = 1; r <= ROWS; r++) {
        const tr = document.createElement('tr');
        const th = document.createElement('th');
        th.textContent = r;
        tr.appendChild(th);
        for (const col of COLS) {
            const td = document.createElement('td');
            const input = document.createElement('input');
            const cellId = col + r;
            input.id = 'cell-' + cellId;
            input.dataset.cell = cellId;
            input.addEventListener('focus', onFocus);
            input.addEventListener('blur', onBlur);
            td.appendChild(input);
            tr.appendChild(td);
        }
        tbody.appendChild(tr);
    }
}

function onFocus(e) {
    const cellId = e.target.dataset.cell;
    const raw = e.target.dataset.raw || '';
    e.target.value = raw;
}

function onBlur(e) {
    const cellId = e.target.dataset.cell;
    const raw = e.target.value;
    if (raw === (e.target.dataset.raw || '')) return;
    fetch('/cells', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cell: cellId, raw: raw })
    })
    .then(r => r.json())
    .then(data => updateCells(data.cells))
    .catch(err => console.error(err));
}

function updateCells(cells) {
    for (const [cellId, info] of Object.entries(cells)) {
        const input = document.getElementById('cell-' + cellId);
        if (!input) continue;
        input.dataset.raw = info.raw;
        const td = input.parentElement;
        if (info.error) {
            input.value = 'ERR';
            td.classList.add('error');
            td.title = info.error;
        } else {
            input.value = info.value !== null && info.value !== 0 ? info.value : (info.raw === '' ? '' : info.value);
            td.classList.remove('error');
            td.title = '';
        }
    }
}

function loadAll() {
    fetch('/cells')
        .then(r => r.json())
        .then(data => updateCells(data.cells))
        .catch(err => console.error(err));
}

buildGrid();
loadAll();
