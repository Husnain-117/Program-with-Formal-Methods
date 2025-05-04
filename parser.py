from lark import Lark, Transformer
from ssa_converter import SSAConverter, format_ssa_output
from smt_generator import SMTGenerator, check_program_equivalence

# Load grammar from mini_lang.lark
with open('mini_lang.lark', 'r') as f:
    grammar = f.read()

# Create parser
parser = Lark(grammar, start='start', parser='earley')

class MiniLangTransformer(Transformer):
    def start(self, items):
        # Recursively flatten nested lists
        def flatten(lst):
            result = []
            for item in lst:
                if isinstance(item, list):
                    result.extend(flatten(item))
                else:
                    result.append(item)
            return result
        return flatten(items)
        
    def assignment(self, items):
        var_name, expr = items
        return ('assign', str(var_name), expr)
        
    def for_assignment(self, items):
        var_name, expr = items
        return ('assign', str(var_name), expr)
        
    def if_statement(self, items):
        cond, block = items[0], items[1]
        else_block = items[2] if len(items) > 2 else None
        return ('if', cond, block, else_block)
        
    def while_loop(self, items):
        cond, block = items
        return self.unroll_while_loop(cond, block)
        
    def for_loop(self, items):
        init, cond, update, block = items
        return self.unroll_for_loop(init, cond, update, block)
        
    def assert_stmt(self, items):
        return ('assert', items[0])
        
    def block(self, items):
        return items
        
    def condition(self, items):
        left, op, right = items
        return ('cond', str(op), left, right)
        
    def add(self, items):
        left, right = items
        return ('add', left, right)
        
    def sub(self, items):
        left, right = items
        return ('sub', left, right)
        
    def mul(self, items):
        left, right = items
        return ('mul', left, right)
        
    def div(self, items):
        left, right = items
        return ('div', left, right)
        
    def number(self, items):
        return int(str(items[0]))
        
    def var(self, items):
        return ('var', str(items[0]))
    
    def unroll_for_loop(self, init, cond, update, block, max_iterations=3):
        """Unroll a for loop into a sequence of conditional statements."""
        unrolled = [init]
        for _ in range(max_iterations):
            block_statements = block if isinstance(block, list) else [block]
            unrolled.append(('if', cond, block_statements + [update], None))
        return unrolled
    
    def unroll_while_loop(self, cond, block, max_iterations=3):
        """Unroll a while loop into a sequence of conditional statements."""
        unrolled = []
        for _ in range(max_iterations):
            unrolled.append(('if', cond, block, None))
        return unrolled

def parse_and_transform(program_text):
    """Parse program text and transform it to AST."""
    tree = parser.parse(program_text)
    transformer = MiniLangTransformer()
    ast = transformer.transform(tree)
    return ast

def main():
    print("\nProgram Analysis Options:")
    print("----------------------------------------")
    print("1. Input Program")
    print("2. Parse Tree")
    print("3. Abstract Syntax Tree (AST)")
    print("4. Static Single Assignment (SSA) Form")
    print("5. Verify Program (SMT)")
    print("6. Check Program Equivalence")
    print("0. Exit Program")
    print("----------------------------------------")
    
    while True:
        try:
            choice = input("Enter numbers (e.g., 123456 to see all): ").strip()
            if choice == '0':
                break
                
            if '1' in choice:
                print("\nInput Program:")
                print("----------------------------------------")
                print(EXAMPLE_PROGRAM)
            
            if '2' in choice:
                print("\nParse Tree:")
                print("----------------------------------------")
                tree = parser.parse(EXAMPLE_PROGRAM)
                print(tree.pretty())
            
            if '3' in choice:
                print("\nAbstract Syntax Tree (AST):")
                print("----------------------------------------")
                ast = parse_and_transform(EXAMPLE_PROGRAM)
                print(ast)
            
            if '4' in choice:
                print("\nStatic Single Assignment (SSA) Form:")
                print("----------------------------------------")
                ast = parse_and_transform(EXAMPLE_PROGRAM)
                ssa = SSAConverter().convert(ast)
                print(format_ssa_output(ssa))
            
            if '5' in choice:
                print("\nProgram Verification (SMT):")
                print("----------------------------------------")
                ast = parse_and_transform(EXAMPLE_PROGRAM)
                ssa = SSAConverter().convert(ast)
                smt = SMTGenerator(ssa)
                smt.to_smt()
                print(smt.check_assertions())
            
            if '6' in choice:
                print("\nProgram Equivalence Check:")
                print("----------------------------------------")
                # Parse and convert first program
                ast1 = parse_and_transform(EXAMPLE_PROGRAM)
                ssa1 = SSAConverter().convert(ast1)
                
                # Parse and convert second program
                print("\nSecond Program:")
                print(EXAMPLE_PROGRAM_2)
                ast2 = parse_and_transform(EXAMPLE_PROGRAM_2)
                ssa2 = SSAConverter().convert(ast2)
                
                print("\nProgram 1 SSA:")
                print(format_ssa_output(ssa1))
                print("\nProgram 2 SSA:")
                print(format_ssa_output(ssa2))
                
                print("\nEquivalence Result:")
                result = check_program_equivalence(ssa1, ssa2)
                print(result)
                
        except Exception as e:
            print(f"\nError: {str(e)}")
            import traceback
            traceback.print_exc()

# Example programs
EXAMPLE_PROGRAM = """
x := 0;
for (i := 0; i < 3; i := i + 1) {
    x := x + 1;
}
assert(x >= 3);
"""

# Example program 2 (for equivalence checking)
EXAMPLE_PROGRAM_2 = """
x := 1;
y := x + 2;
for (i := 0; i < 3; i := i + 1) {
    y := y + 1;
}
assert(y >= 0);
"""

if __name__ == "__main__":
    main()