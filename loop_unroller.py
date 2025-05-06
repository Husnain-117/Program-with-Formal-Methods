"""
Loop unroller for MiniLang AST.
Supports unrolling 'for' and 'while' loops up to a given bound.
"""

import copy

def unroll_loops(ast, unroll_bound=3):
    """
    Unrolls all for/while loops in the AST up to unroll_bound iterations.
    Returns a new AST with loops unrolled.
    """
    def unroll_stmt(stmt):
        if stmt[0] == 'for':
            # ('for', init, cond, update, body)
            init, cond, update, body = stmt[1], stmt[2], stmt[3], stmt[4]
            stmts = [init]
            for _ in range(unroll_bound):
                stmts.append(('if', cond, body, None))
                stmts.extend(body)
                stmts.append(update)
            return stmts
        elif stmt[0] == 'while':
            # ('while', cond, body)
            cond, body = stmt[1], stmt[2]
            stmts = []
            for _ in range(unroll_bound):
                stmts.append(('if', cond, body, None))
                stmts.extend(body)
            return stmts
        elif stmt[0] == 'if':
            # ('if', cond, then_block, else_block)
            cond, then_block, else_block = stmt[1], stmt[2], stmt[3]
            then_unrolled = []
            for s in then_block:
                then_unrolled.extend(unroll_stmt(s) if is_loop(s) else [s])
            else_unrolled = []
            if else_block:
                for s in else_block:
                    else_unrolled.extend(unroll_stmt(s) if is_loop(s) else [s])
            return [('if', cond, then_unrolled, else_unrolled if else_block else None)]
        else:
            return [stmt]

    def is_loop(stmt):
        return stmt[0] in ('for', 'while')

    new_ast = []
    for stmt in ast:
        if is_loop(stmt):
            new_ast.extend(unroll_stmt(stmt))
        else:
            new_ast.append(stmt)
    return new_ast

def format_unrolled_code(ast):
    """
    Formats the unrolled AST back into readable MiniLang code.
    """
    def fmt(stmt, indent=0):
        ind = '    ' * indent
        if stmt[0] == 'assign':
            return f"{ind}{stmt[1]} := {format_expr(stmt[2])};"
        elif stmt[0] == 'assert':
            return f"{ind}assert({format_expr(stmt[1])});"
        elif stmt[0] == 'if':
            cond = format_expr(stmt[1])
            then_block = '\n'.join(fmt(s, indent+1) for s in stmt[2])
            res = f"{ind}if ({cond}) {{\n{then_block}\n{ind}}}"
            if stmt[3]:
                else_block = '\n'.join(fmt(s, indent+1) for s in stmt[3])
                res += f" else {{\n{else_block}\n{ind}}}"
            return res
        else:
            return f"{ind}{stmt}"

    def format_expr(expr):
        if isinstance(expr, tuple):
            if expr[0] == 'var':
                return expr[1]
            elif expr[0] == 'cond':
                return f"{format_expr(expr[2])} {expr[1]} {format_expr(expr[3])}"
            elif expr[0] in ('add', 'sub', 'mul', 'div'):
                ops = {'add': '+', 'sub': '-', 'mul': '*', 'div': '/'}
                return f"{format_expr(expr[1])} {ops[expr[0]]} {format_expr(expr[2])}"
        return str(expr)

    return '\n'.join(fmt(stmt) for stmt in ast) 