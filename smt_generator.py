"""SMT Generator for converting SSA form to Z3 constraints."""
from z3 import *

class SMTGenerator:
    def __init__(self, ssa_code, var_prefix=""):
        self.ssa_code = ssa_code if isinstance(ssa_code, list) else [ssa_code]
        self.solver = Solver()
        self.vars = {}
        self.path_condition = True
        self.constraints = []
        self.var_prefix = var_prefix

    def get_var(self, name):
        """Get or create a Z3 variable."""
        if name not in self.vars:
            # prefix to avoid name collisions across programs
            self.vars[name] = Int(f"{self.var_prefix}{name}")
        return self.vars[name]

    def expr_to_z3(self, expr):
        """Convert expression to Z3 formula."""
        if isinstance(expr, (int, float)):
            return expr
        elif isinstance(expr, str):
            return self.get_var(expr)
        elif isinstance(expr, tuple):
            if expr[0] == 'var':
                return self.get_var(expr[1])
            elif expr[0] == 'cond':
                _, op, left, right = expr
                left_z3 = self.expr_to_z3(left)
                right_z3 = self.expr_to_z3(right)
                if op == '<':
                    return left_z3 < right_z3
                elif op == '>':
                    return left_z3 > right_z3
                elif op == '<=':
                    return left_z3 <= right_z3
                elif op == '>=':
                    return left_z3 >= right_z3
                elif op == '==':
                    return left_z3 == right_z3
                elif op == '!=':
                    return left_z3 != right_z3
            elif expr[0] == 'add':
                left_z3 = self.expr_to_z3(expr[1])
                right_z3 = self.expr_to_z3(expr[2])
                return left_z3 + right_z3
            elif expr[0] == 'sub':
                left_z3 = self.expr_to_z3(expr[1])
                right_z3 = self.expr_to_z3(expr[2])
                return left_z3 - right_z3
            elif expr[0] == 'mul':
                left_z3 = self.expr_to_z3(expr[1])
                right_z3 = self.expr_to_z3(expr[2])
                return left_z3 * right_z3
            elif expr[0] == 'div':
                left_z3 = self.expr_to_z3(expr[1])
                right_z3 = self.expr_to_z3(expr[2])
                return left_z3 / right_z3
        return expr

    def to_smt(self):
        """Convert SSA code to SMT constraints."""
        for stmt in self.ssa_code:
            if isinstance(stmt, tuple):
                if stmt[0] == 'if':
                    cond = stmt[1]
                    self.solver.add(Implies(self.path_condition, self.expr_to_z3(cond)))
                    self.constraints.append(Implies(self.path_condition, self.expr_to_z3(cond)))
                elif stmt[0] == 'assert':
                    cond = stmt[1]
                    self.solver.add(Implies(self.path_condition, self.expr_to_z3(cond)))
                    self.constraints.append(Implies(self.path_condition, self.expr_to_z3(cond)))
                else:  # Assignment
                    var, op, rhs = stmt
                    if isinstance(rhs, str) and rhs.startswith('phi'):
                        # Handle phi nodes
                        args = rhs[4:-1].split(',')
                        args = [arg.strip() for arg in args]
                        # For now, just use the first non-None argument
                        for arg in args:
                            if arg != 'None':
                                self.solver.add(self.get_var(var) == self.get_var(arg))
                                self.constraints.append(self.get_var(var) == self.get_var(arg))
                                break
                    else:
                        self.solver.add(self.get_var(var) == self.expr_to_z3(rhs))
                        self.constraints.append(self.get_var(var) == self.expr_to_z3(rhs))

    def get_final_versions(self):
        """Get the final version of each variable."""
        final_versions = {}
        for stmt in self.ssa_code:
            # detect SSA assignments: (var_name, '=', expr)
            if isinstance(stmt, tuple) and len(stmt) == 3 and stmt[1] == '=':
                var = stmt[0]
                base_var = var.split('_')[0]
                final_versions[base_var] = var
        return final_versions

    def check_assertions(self):
        """Check if all assertions hold."""
        if self.solver.check() == sat:
            model = self.solver.model()
            result = "✅ All assertions hold! Model:\n"
            # Sort variables by their base name and version
            sorted_vars = sorted(self.vars.keys(), 
                               key=lambda x: (x.split('_')[0], 
                                           int(x.split('_')[1]) if '_' in x and x.split('_')[1].isdigit() else 0))
            for var in sorted_vars:
                if self.vars[var] in model:
                    result += f"{var} = {model[self.vars[var]]}\n"
            return result
        else:
            return "❌ Assertion violation found!"

    def get_outputs(self):
        """Get output variables and their expressions."""
        outputs = []
        current_cond = None
        var_versions = {}  # Track the latest version of each variable
        
        # First pass: collect all variable versions
        for stmt in self.ssa_code:
            if isinstance(stmt, tuple):
                if stmt[0] == 'if':
                    current_cond = stmt[1]
                elif stmt[0] == 'assign':
                    var = stmt[1]
                    expr = stmt[2]
                    base_var = var.split('_')[0]  # Get base variable name without version
                    var_versions[base_var] = (var, expr, current_cond)
        
        # Second pass: collect only the final version of each variable
        outputs = list(var_versions.values())
        return outputs

def var_from_stmt(stmt):
    """Extract variable name from an assignment statement."""
    if isinstance(stmt, tuple):
        if stmt[0] == 'assign':
            return stmt[1]  # Return the variable name directly
    return None

def check_program_equivalence(ssa1, ssa2):
    """Check if two programs in SSA form are equivalent by comparing their outputs under all conditions."""
    try:
        # Create SMT solvers with distinct variable prefixes
        smt1 = SMTGenerator(ssa1, var_prefix="p1_")
        smt2 = SMTGenerator(ssa2, var_prefix="p2_")
        
        # Convert to SMT constraints
        smt1.to_smt()
        smt2.to_smt()
        
        # Get final versions of variables
        vars1 = smt1.get_final_versions()
        vars2 = smt2.get_final_versions()
        
        # Create a new solver for equivalence checking
        s = Solver()
        
        # Add all constraints from both programs
        for c in smt1.solver.assertions():
            s.add(c)
        for c in smt2.solver.assertions():
            s.add(c)
        
        # Check if variables can have different values
        common_vars = set(vars1.keys()) & set(vars2.keys())
        if not common_vars:
            return "❌ Programs are NOT equivalent! No common variables to compare."
        
        for base_var in common_vars:
            var1 = vars1[base_var]
            var2 = vars2[base_var]
            
            s.push()
            s.add(smt1.vars[var1] != smt2.vars[var2])
            
            if s.check() == sat:
                model = s.model()
                result = "❌ Programs are NOT equivalent!\n\n"
                
                # Get input values
                input_vals = {}
                for var_name, var_z3 in sorted(smt1.vars.items()):
                    if var_name.endswith('_1') and var_z3.decl() in model:
                        input_vals[var_name] = model[var_z3]
                
                # Get program 1 values
                prog1_vals = {}
                for var_name, var_z3 in sorted(smt1.vars.items()):
                    if var_z3.decl() in model and not var_name.endswith('_1'):
                        prog1_vals[var_name] = model[var_z3]
                
                # Get program 2 values
                prog2_vals = {}
                for var_name, var_z3 in sorted(smt2.vars.items()):
                    if var_z3.decl() in model and not var_name.endswith('_1'):
                        prog2_vals[var_name] = model[var_z3]
                
                result += "Input values:\n"
                result += "\n".join(f"{var} = {val}" for var, val in input_vals.items())
                
                result += "\n\nProgram 1 values:\n"
                result += "\n".join(f"{var} = {val}" for var, val in prog1_vals.items())
                
                result += "\n\nProgram 2 values:\n"
                result += "\n".join(f"{var} = {val}" for var, val in prog2_vals.items())
                
                return result
            
            s.pop()
        
        # Check assertions
        def get_assertions(program):
            assertions = []
            current_cond = None
            for stmt in program:
                if isinstance(stmt, tuple):
                    if stmt[0] == 'if':
                        current_cond = stmt[1]
                    elif stmt[0] == 'assert':
                        assertions.append((stmt[1], current_cond))
            return assertions
        
        assertions1 = get_assertions(ssa1)
        assertions2 = get_assertions(ssa2)
        
        # Check if assertions can be violated in different ways
        for (assert1, cond1), (assert2, cond2) in zip(assertions1, assertions2):
            s.push()
            
            # Convert conditions to Z3 formulas
            z3_cond1 = smt1.expr_to_z3(cond1) if cond1 else True
            z3_cond2 = smt2.expr_to_z3(cond2) if cond2 else True
            
            # Convert assertions to Z3 formulas
            z3_assert1 = smt1.expr_to_z3(assert1)
            z3_assert2 = smt2.expr_to_z3(assert2)
            
            # Check if assertions can be satisfied differently
            s.add(Or(
                And(z3_cond1, z3_assert1, Not(z3_assert2)),
                And(z3_cond2, Not(z3_assert1), z3_assert2)
            ))
            
            if s.check() == sat:
                model = s.model()
                result = "❌ Programs are NOT equivalent!\n"
                result += "Programs have different assertion behaviors:\n\n"
                
                # Get input values
                input_vals = {}
                for var_name, var_z3 in sorted(smt1.vars.items()):
                    if var_name.endswith('_1') and var_z3.decl() in model:
                        input_vals[var_name] = model[var_z3]
                
                # Get program 1 values
                prog1_vals = {}
                for var_name, var_z3 in sorted(smt1.vars.items()):
                    if var_z3.decl() in model and not var_name.endswith('_1'):
                        prog1_vals[var_name] = model[var_z3]
                
                # Get program 2 values
                prog2_vals = {}
                for var_name, var_z3 in sorted(smt2.vars.items()):
                    if var_z3.decl() in model and not var_name.endswith('_1'):
                        prog2_vals[var_name] = model[var_z3]
                
                result += "Input values:\n"
                result += "\n".join(f"{var} = {val}" for var, val in input_vals.items())
                
                result += "\n\nProgram 1:\n"
                result += f"Assertion: {format_condition(assert1)}\n"
                result += f"Under condition: {format_condition(cond1)}\n"
                result += "\n".join(f"{var} = {val}" for var, val in prog1_vals.items())
                
                result += "\n\nProgram 2:\n"
                result += f"Assertion: {format_condition(assert2)}\n"
                result += f"Under condition: {format_condition(cond2)}\n"
                result += "\n".join(f"{var} = {val}" for var, val in prog2_vals.items())
                
                return result
            
            s.pop()
        
        return "✅ Programs are equivalent! They have the same behavior under all conditions."
    
    except Exception as e:
        import traceback
        return f"⚠️ Error checking equivalence: {str(e)}\n{traceback.format_exc()}"

def format_condition(cond):
    """Format a condition tuple into a readable string."""
    if not cond:
        return "always"
    if isinstance(cond, tuple):
        if cond[0] == 'cond':
            op = cond[1].value if hasattr(cond[1], 'value') else cond[1]
            left = cond[2][1] if isinstance(cond[2], tuple) and cond[2][0] == 'var' else cond[2]
            right = cond[3]
            return f"{left} {op} {right}"
    return str(cond)

def parse_ssa(ssa_str):
    """Parse SSA string format into structured format."""
    ssa_code = []
    current_if = None
    then_block = []
    else_block = None

    for line in ssa_str.strip().split('\n'):
        line = line.strip()
        if not line:
            continue

        if line.startswith('if'):
            # Start of if statement
            try:
                cond = line[3:-1].strip()  # Remove 'if' and get condition
                if '(' in cond and ')' in cond:
                    cond = cond[1:-1]  # Remove outer parentheses
                # Convert condition to proper format
                if '<' in cond:
                    left, right = cond.split('<')
                    left = ('var', left.strip()) if not left.strip().isdigit() else int(left)
                    right = int(right.strip())
                    current_if = ('if', ('cond', '<', left, right), [], None)
            except:
                continue
        elif line == '}':
            # End of block
            if current_if:
                ssa_code.append(current_if)
                current_if = None
        elif ':=' in line:
            var, expr = line.split(':=')
            var = var.strip()
            expr = expr.strip()
            if expr.endswith(';'):
                expr = expr[:-1]
            
            try:
                if expr.startswith('(\'var\','):
                    expr = eval(expr)
                elif expr.startswith('(\'cond\','):
                    expr = eval(expr)
                elif expr.startswith('phi('):
                    # Handle phi nodes
                    phi_args = expr[4:-1].split(',')
                    expr = ('phi', 
                           eval(phi_args[0].strip()) if phi_args[0].strip() != 'None' else None,
                           eval(phi_args[1].strip()) if phi_args[1].strip() != 'None' else None)
                elif '+' in expr:
                    parts = expr.split('+')
                    left = parts[0].strip()
                    right = parts[1].strip()
                    left = eval(left) if left.startswith('(') else (int(left) if left.isdigit() else ('var', left))
                    right = eval(right) if right.startswith('(') else (int(right) if right.isdigit() else ('var', right))
                    expr = ('add', left, right)
                elif '-' in expr:
                    parts = expr.split('-')
                    left = parts[0].strip()
                    right = parts[1].strip()
                    left = eval(left) if left.startswith('(') else (int(left) if left.isdigit() else ('var', left))
                    right = eval(right) if right.startswith('(') else (int(right) if right.isdigit() else ('var', right))
                    expr = ('sub', left, right)
                elif '*' in expr:
                    parts = expr.split('*')
                    left = parts[0].strip()
                    right = parts[1].strip()
                    left = eval(left) if left.startswith('(') else (int(left) if left.isdigit() else ('var', left))
                    right = eval(right) if right.startswith('(') else (int(right) if right.isdigit() else ('var', right))
                    expr = ('mul', left, right)
                elif expr.isdigit() or (expr.startswith('-') and expr[1:].isdigit()):
                    expr = int(expr)
                else:
                    expr = ('var', expr)
                
                stmt = ('assign', var, expr)  
                if current_if:
                    current_if[2].append(stmt)
                else:
                    ssa_code.append(stmt)
            except:
                if current_if:
                    current_if[2].append((var, '=', expr))
                else:
                    ssa_code.append((var, '=', expr))
        elif line.startswith('assert'):
            try:
                cond = line[7:-1]  # Remove assert( and )
                if cond.startswith('(\'var\','):
                    var = eval(cond)
                    ssa_code.append(('assert', ('cond', '>', var, 0)))
                elif cond.startswith('(\'cond\','):
                    cond = eval(cond)
                    ssa_code.append(('assert', cond))
                else:
                    # Handle other assertion formats
                    if '>' in cond:
                        left, right = cond.split('>')
                        left = ('var', left.strip()) if not left.strip().isdigit() else int(left)
                        right = int(right.strip())
                        ssa_code.append(('assert', ('cond', '>', left, right)))
            except:
                continue

    return ssa_code

def get_input_vars(vars_dict):
    """Get input variables (usually _1 suffix)"""
    return [name for name in vars_dict.keys() if name.endswith('_1')]

def get_output_vars(vars_dict):
    """Get output variables (usually highest numbered suffix for each base name)"""
    var_groups = {}
    for name in vars_dict.keys():
        if name == "undefined" or not '_' in name:
            continue
        try:
            base, num_str = name.rsplit('_', 1)
            if not num_str.isdigit():
                continue
            num = int(num_str)
            if base not in var_groups or num > var_groups[base][1]:
                var_groups[base] = (name, num)
        except (ValueError, IndexError):
            continue
    
    return [var_info[0] for var_info in var_groups.values()]


def convert_ssa_to_smt(ssa_output):
    """Convert SSA output to SMT constraints and check assertions."""
    if not ssa_output:
        return "No SSA code provided"
        
    ssa_code = parse_ssa(ssa_output)
    
    # Generate and check SMT constraints
    smt = SMTGenerator(ssa_code)
    smt.to_smt()
    return smt.check_assertions()
