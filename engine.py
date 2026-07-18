"""Formula engine for the minimal spreadsheet."""

import re


# Valid cell pattern: column A-J, row 1-10
_CELL_RE = re.compile(r'^([A-Ja-j])(10|[1-9])$')

# Token patterns for the formula lexer
_TOKEN_RE = re.compile(
    r'([A-Ja-j](?:10|[1-9]))'   # cell reference
    r'|(\d+(?:\.\d*)?|\.\d+)'    # number
    r'|([+\-*/()])'              # operator or paren
)


def _is_valid_cell(cell_id: str) -> bool:
    return bool(_CELL_RE.match(cell_id))


def _normalize(cell_id: str) -> str:
    return cell_id.upper()


def _tokenize(expr: str):
    """Tokenize a formula expression (without the leading '=').
    Returns list of (type, value) tuples.
    Types: 'NUM', 'CELL', 'OP'
    Raises ValueError on invalid tokens.
    """
    tokens = []
    pos = 0
    while pos < len(expr):
        if expr[pos].isspace():
            pos += 1
            continue
        m = _TOKEN_RE.match(expr, pos)
        if not m:
            raise ValueError(f"unexpected character: {expr[pos]}")
        if m.group(1):
            tokens.append(('CELL', _normalize(m.group(1))))
        elif m.group(2):
            tokens.append(('NUM', float(m.group(2))))
        elif m.group(3):
            tokens.append(('OP', m.group(3)))
        pos = m.end()
    return tokens


class _Parser:
    """Recursive-descent parser for arithmetic expressions with cell refs.

    Grammar:
        expr   -> term (('+' | '-') term)*
        term   -> unary (('*' | '/') unary)*
        unary  -> '-' unary | atom
        atom   -> NUMBER | CELL_REF | '(' expr ')'

    Returns an AST as nested tuples.
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def _peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def _consume(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def parse(self):
        result = self._expr()
        if self.pos < len(self.tokens):
            raise ValueError("unexpected token after expression")
        return result

    def _expr(self):
        left = self._term()
        while self._peek() and self._peek() == ('OP', '+') or \
              self._peek() and self._peek() == ('OP', '-'):
            op = self._consume()[1]
            right = self._term()
            left = ('binop', op, left, right)
        return left

    def _term(self):
        left = self._unary()
        while self._peek() and self._peek() == ('OP', '*') or \
              self._peek() and self._peek() == ('OP', '/'):
            op = self._consume()[1]
            right = self._unary()
            left = ('binop', op, left, right)
        return left

    def _unary(self):
        if self._peek() and self._peek() == ('OP', '-'):
            self._consume()
            operand = self._unary()
            return ('unary', '-', operand)
        return self._atom()

    def _atom(self):
        tok = self._peek()
        if tok is None:
            raise ValueError("unexpected end of expression")
        if tok[0] == 'NUM':
            self._consume()
            return ('num', tok[1])
        if tok[0] == 'CELL':
            self._consume()
            return ('cell', tok[1])
        if tok == ('OP', '('):
            self._consume()
            node = self._expr()
            if not self._peek() or self._peek() != ('OP', ')'):
                raise ValueError("missing closing parenthesis")
            self._consume()
            return node
        raise ValueError(f"unexpected token: {tok}")


def _parse_formula(expr: str):
    """Parse a formula expression string (without '=') into an AST."""
    tokens = _tokenize(expr)
    if not tokens:
        raise ValueError("empty expression")
    return _Parser(tokens).parse()


def _collect_refs(ast):
    """Collect all cell references from an AST."""
    refs = set()
    if ast[0] == 'num':
        pass
    elif ast[0] == 'cell':
        refs.add(ast[1])
    elif ast[0] == 'binop':
        refs |= _collect_refs(ast[2])
        refs |= _collect_refs(ast[3])
    elif ast[0] == 'unary':
        refs |= _collect_refs(ast[2])
    return refs


def _eval_ast(ast, cell_values):
    """Evaluate an AST given a dict of cell_id -> numeric value.
    Raises ZeroDivisionError or ValueError on errors.
    cell_values maps cell_id to its value (float) or raises if error.
    """
    if ast[0] == 'num':
        return ast[1]
    elif ast[0] == 'cell':
        return cell_values(ast[1])
    elif ast[0] == 'unary':
        return -_eval_ast(ast[2], cell_values)
    elif ast[0] == 'binop':
        left = _eval_ast(ast[2], cell_values)
        right = _eval_ast(ast[3], cell_values)
        op = ast[1]
        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            if right == 0:
                raise ZeroDivisionError("division by zero")
            return left / right
    raise ValueError("unknown AST node")


class Spreadsheet:
    """Holds all cell state and evaluates formulas."""

    def __init__(self):
        # cell_id -> raw string
        self._raw = {}
        # cell_id -> parsed AST (None if literal or parse error)
        self._ast = {}
        # cell_id -> set of cell_ids this cell depends on
        self._deps = {}
        # cell_id -> computed value (float) or None if error
        self._values = {}
        # cell_id -> error string or None
        self._errors = {}

    def _parse_and_store(self, cell_id, raw):
        """Parse raw input, store AST and deps."""
        self._raw[cell_id] = raw
        if raw == '' or raw is None:
            self._ast[cell_id] = None
            self._deps[cell_id] = set()
            return
        if not raw.startswith('='):
            # Literal value
            try:
                float(raw)
                self._ast[cell_id] = None
                self._deps[cell_id] = set()
            except ValueError:
                self._ast[cell_id] = None
                self._deps[cell_id] = set()
                self._errors[cell_id] = "invalid value"
                self._values[cell_id] = None
            return
        # Formula
        try:
            ast = _parse_formula(raw[1:])
            self._ast[cell_id] = ast
            self._deps[cell_id] = _collect_refs(ast)
        except ValueError as e:
            self._ast[cell_id] = None
            self._deps[cell_id] = set()
            self._errors[cell_id] = str(e)
            self._values[cell_id] = None

    def _get_dependents(self, cell_id):
        """Get all cells that directly depend on cell_id."""
        result = set()
        for cid, deps in self._deps.items():
            if cell_id in deps:
                result.add(cid)
        return result

    def _get_all_dependents(self, cell_id):
        """Get all cells transitively depending on cell_id (BFS)."""
        visited = set()
        queue = [cell_id]
        while queue:
            current = queue.pop(0)
            for dep in self._get_dependents(current):
                if dep not in visited:
                    visited.add(dep)
                    queue.append(dep)
        return visited

    def _detect_cycle(self, start_cell):
        """Detect if start_cell is part of a dependency cycle.
        Returns set of cells in the cycle, or empty set if no cycle.
        """
        # DFS from start_cell following deps
        visited = set()
        path = set()
        cycle_cells = set()

        def dfs(cell):
            if cell in path:
                cycle_cells.add(cell)
                return True
            if cell in visited:
                return False
            visited.add(cell)
            path.add(cell)
            for dep in self._deps.get(cell, set()):
                if dfs(dep):
                    if cell in path:
                        cycle_cells.add(cell)
            path.discard(cell)
            return bool(cycle_cells)

        dfs(start_cell)
        return cycle_cells

    def _find_all_cycle_cells(self, cell_id):
        """Find all cells involved in cycles reachable from cell_id."""
        # Collect all cells reachable from cell_id through deps
        all_cells = {cell_id}
        all_cells |= self._get_all_dependents(cell_id)

        # For each cell, check if it's in a cycle
        cycle_cells = set()
        for cid in all_cells:
            # A cell is in a cycle if following its deps can reach itself
            visited = set()
            queue = list(self._deps.get(cid, set()))
            while queue:
                current = queue.pop(0)
                if current == cid:
                    cycle_cells.add(cid)
                    break
                if current not in visited:
                    visited.add(current)
                    queue.extend(self._deps.get(current, set()))

        return cycle_cells

    def _topo_sort(self, cells):
        """Topological sort of cells by dependency order.
        Returns sorted list. Raises ValueError if cycle detected.
        """
        # Build in-degree map restricted to the given cells
        in_degree = {c: 0 for c in cells}
        for c in cells:
            for dep in self._deps.get(c, set()):
                if dep in cells:
                    in_degree[c] = in_degree.get(c, 0)  # ensure exists

        # Kahn's algorithm
        for c in cells:
            for dep in self._deps.get(c, set()):
                if dep in in_degree:
                    in_degree[c] += 1

        # Reset and recount properly
        in_degree = {c: 0 for c in cells}
        for c in cells:
            for dep in self._deps.get(c, set()):
                if dep in cells:
                    # dep is a dependency of c, so c depends on dep
                    # In topo sort, dep must come before c
                    in_degree[c] += 1

        queue = [c for c in cells if in_degree[c] == 0]
        result = []
        while queue:
            node = queue.pop(0)
            result.append(node)
            # Find cells in our set that depend on node
            for c in cells:
                if node in self._deps.get(c, set()):
                    in_degree[c] -= 1
                    if in_degree[c] == 0:
                        queue.append(c)

        return result

    def _evaluate_cell(self, cell_id):
        """Evaluate a single cell. Sets _values and _errors."""
        raw = self._raw.get(cell_id, '')

        # Already marked as error from parsing
        if cell_id in self._errors and self._ast.get(cell_id) is None and \
           raw.startswith('='):
            return

        if raw == '' or raw is None:
            self._values[cell_id] = 0
            self._errors.pop(cell_id, None)
            return

        if not raw.startswith('='):
            try:
                self._values[cell_id] = float(raw)
                self._errors.pop(cell_id, None)
            except ValueError:
                self._values[cell_id] = None
                self._errors[cell_id] = "invalid value"
            return

        # Formula evaluation
        ast = self._ast.get(cell_id)
        if ast is None:
            # Parse error already set
            return

        def get_value(ref_cell):
            if ref_cell in self._errors:
                raise ValueError(f"reference to error cell {ref_cell}")
            return self._values.get(ref_cell, 0)

        try:
            value = _eval_ast(ast, get_value)
            self._values[cell_id] = value
            self._errors.pop(cell_id, None)
        except ZeroDivisionError:
            self._values[cell_id] = None
            self._errors[cell_id] = "division by zero"
        except (ValueError, TypeError) as e:
            self._values[cell_id] = None
            self._errors[cell_id] = str(e)

    def _cell_info(self, cell_id):
        """Build the info dict for a cell."""
        info = {
            'raw': self._raw.get(cell_id, ''),
            'value': self._values.get(cell_id, 0),
        }
        if cell_id in self._errors:
            info['value'] = None
            info['error'] = self._errors[cell_id]
        return info

    def set_cell(self, cell_id: str, raw: str) -> dict:
        """Set a cell's raw content and recalculate."""
        cell_id = _normalize(cell_id)

        # Save old values for change detection
        old_values = {}
        for cid in list(self._values.keys()):
            old_values[cid] = (self._values.get(cid), self._errors.get(cid))

        # Clear old error for this cell
        self._errors.pop(cell_id, None)

        # Parse and store
        self._parse_and_store(cell_id, raw)

        # Detect cycles
        cycle_cells = self._find_all_cycle_cells(cell_id)

        if cycle_cells:
            # Mark all cycle cells as errors
            for cid in cycle_cells:
                self._values[cid] = None
                self._errors[cid] = "circular reference"

            # Also mark cells that depend on cycle cells as errors
            for cid in cycle_cells:
                for dep in self._get_all_dependents(cid):
                    if dep not in cycle_cells:
                        self._values[dep] = None
                        self._errors[dep] = "reference to error cell"

            # Build result with all changed cells
            changed = {}
            changed[cell_id] = self._cell_info(cell_id)
            for cid in cycle_cells:
                changed[cid] = self._cell_info(cid)
            for cid in cycle_cells:
                for dep in self._get_all_dependents(cid):
                    changed[dep] = self._cell_info(dep)
            return changed

        # Evaluate this cell
        self._evaluate_cell(cell_id)

        # Get all transitive dependents and recalculate in order
        dependents = self._get_all_dependents(cell_id)

        if dependents:
            # Check for cycles among dependents
            non_cycle = dependents - cycle_cells
            sorted_deps = self._topo_sort(non_cycle)
            for dep in sorted_deps:
                self._evaluate_cell(dep)

        # Build result: include this cell + all changed cells
        changed = {}
        changed[cell_id] = self._cell_info(cell_id)
        for cid in dependents:
            new_val = (self._values.get(cid), self._errors.get(cid))
            old_val = old_values.get(cid)
            if old_val != new_val or cid not in old_values:
                changed[cid] = self._cell_info(cid)

        return changed

    def get_all_cells(self) -> dict:
        """Return the full grid state."""
        result = {}
        for cell_id in self._raw:
            result[cell_id] = self._cell_info(cell_id)
        return result
