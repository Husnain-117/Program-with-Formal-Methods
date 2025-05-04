from lark import Lark, Transformer
from ssa_converter import SSAConverter, format_ssa_output
from smt_generator import SMTGenerator, check_program_equivalence

# Grammar definition
grammar = """
    start: statement+
    
    ?statement: assignment | if_statement | assert_stmt
    
    assignment: NAME ":=" expr ";"
    
    if_statement: "if" "(" condition ")" "{" statement+ "}"
    
    assert_stmt: "assert" "(" condition ")" ";"
    
    condition: expr COMP expr
    
    ?expr: term
         | expr "+" term -> add
         | expr "-" term -> sub
    
    ?term: factor
         | term "*" factor -> mul
         | term "/" factor -> div
    
    ?factor: NUMBER -> number
           | NAME -> var
           | "(" expr ")"
    
    COMP: "<"|">"|"<="|">="|"=="|"!="
    NAME: /[a-zA-Z_][a-zA-Z0-9_]*/
    NUMBER: /-?[0-9]+/
    
    %import common.WS
    %ignore WS
"""

# Create parser
parser = Lark(grammar)

class MiniLangTransformer(Transformer):
    def start(self, items):
        return items
        
    def assignment(self, items):
        var_name, expr = items
        return ('assign', str(var_name), expr)
        
    def if_statement(self, items):
        cond = items[0]
        block = items[1:]
        return ('if', cond, block, None)
        
    def assert_stmt(self, items):
        return ('assert', items[0])
        
    def condition(self, items):
        left, op, right = items
        return ('cond', op, left, right)
        
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
x := 10;
y := 5;
if (x > y) {
    z := x + y;
    assert(z > x);
}
y := z - 2;
assert(y >= 0);
"""

# Example program 2 (for equivalence checking)
EXAMPLE_PROGRAM_2 = """
x := 1;
y := x + 2;
if (y > 5) {
    z := y - 2;
}
assert(z < 0);
"""

if __name__ == "__main__":
    main()