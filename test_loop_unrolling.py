from parser import parse_and_transform, SSAConverter, format_ssa_output

def test_loop_unrolling():
    program = """
    x := 0;
    for (i := 0; i < 3; i := i + 1) {
        x := x + 1;
    }
    assert(x >= 3);
    """
    
    # Parse and transform to AST
    ast = parse_and_transform(program)
    
    # Convert to SSA
    ssa_converter = SSAConverter()
    ssa = ssa_converter.convert(ast)
    
    # Format and print SSA output
    ssa_output = format_ssa_output(ssa)
    print("SSA Output for Test Program:")
    print(ssa_output)
    
    # Verify key aspects of the output
    assert "x_1 := 0" in ssa_output, "Initial assignment missing"
    assert "x_2 := x_1 + 1" in ssa_output, "First iteration missing"
    assert "x_3 := x_2 + 1" in ssa_output, "Second iteration missing"
    assert "x_4 := x_3 + 1" in ssa_output, "Third iteration missing"
    assert "assert(x_4 >= 3)" in ssa_output, "Assertion missing"
    print("✅ Test passed: Loop unrolling verified.")

if __name__ == "__main__":
    test_loop_unrolling()