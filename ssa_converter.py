"""
Static Single Assignment (SSA) form converter implementation.
This module provides functionality to convert code into SSA form.
"""

class SSAConverter:
    def __init__(self):
        self.counter = {}  # Tracks variable versions: {'x': 3}
        self.env = {}      # Current version mapping: {'x': 'x_3'}
        self.ssa = []      # List of SSA statements

    def new_version(self, var):
        """Create a new version of a variable."""
        n = self.counter.get(var, 0) + 1
        self.counter[var] = n
        vname = f"{var}_{n}"
        self.env[var] = vname
        return vname

    def current(self, var):
        """Get current version of a variable."""
        return self.env.get(var, var)

    def convert(self, ast):
        """Convert AST to SSA form."""
        for stmt in ast:
            if stmt[0] == 'assign':
                self.handle_assignment(stmt)
            elif stmt[0] == 'if':
                self.handle_if(stmt)
            elif stmt[0] == 'assert':
                self.handle_assert(stmt)
        return self.ssa

    def handle_assignment(self, stmt):
        """Handle assignment statement."""
        _, var, expr = stmt
        # First transform the expression using current variable versions
        new_expr = self.transform_expr(expr)
        # Then create a new version of the variable
        new_var = self.new_version(var)
        self.ssa.append((new_var, '=', new_expr))

    def handle_if(self, stmt):
        """Handle if statement."""
        _, cond, true_block, false_block = stmt
        new_cond = self.transform_expr(cond)
        self.ssa.append(('if', new_cond))
        
        if true_block:
            for s in true_block:
                if s[0] == 'assign':
                    self.handle_assignment(s)
        
        if false_block:
            for s in false_block:
                if s[0] == 'assign':
                    self.handle_assignment(s)

    def handle_assert(self, stmt):
        """Handle assert statement."""
        _, cond = stmt
        new_cond = self.transform_expr(cond)
        self.ssa.append(('assert', new_cond))

    def transform_expr(self, expr):
        """Transform expression to use SSA variables."""
        if isinstance(expr, tuple):
            if expr[0] == 'var':
                return ('var', self.current(expr[1]))
            elif expr[0] == 'cond':
                op = expr[1].value if hasattr(expr[1], 'value') else expr[1]
                left = self.transform_expr(expr[2])
                right = self.transform_expr(expr[3])
                return ('cond', op, left, right)
            elif expr[0] in ('add', 'sub', 'mul', 'div'):
                left = self.transform_expr(expr[1])
                right = self.transform_expr(expr[2])
                return (expr[0], left, right)
        return expr

def format_ssa_output(ssa_list):
    """Format SSA statements into readable code."""
    def format_expr(expr):
        if isinstance(expr, tuple):
            if expr[0] == 'var':
                return expr[1]
            elif expr[0] == 'cond':
                return f"{format_expr(expr[2])} {expr[1]} {format_expr(expr[3])}"
            elif expr[0] in ('add', 'sub', 'mul', 'div'):
                ops = {
                    'add': '+', 'sub': '-',
                    'mul': '*', 'div': '/'
                }
                return f"{format_expr(expr[1])} {ops[expr[0]]} {format_expr(expr[2])}"
        return str(expr)

    output = []
    indent = 0
    for stmt in ssa_list:
        if isinstance(stmt, tuple):
            if stmt[0] == 'if':
                output.append("  " * indent + f"if {format_expr(stmt[1])}")
                indent += 1
            elif stmt[0] == 'assert':
                output.append("  " * indent + f"assert({format_expr(stmt[1])})")
            else:
                var, op, rhs = stmt
                output.append("  " * indent + f"{var} := {format_expr(rhs)}")
        if stmt[0] != 'if' and indent > 0:
            indent -= 1
    return "\n".join(output)