# Program Equivalence Checker

A formal methods tool that checks program equivalence using SSA form and SMT solving.

## Overview

This project implements a program equivalence checker using formal methods techniques. It consists of several components:

1. **Parser (`parser.py`)**: Parses a simple programming language with assignments, if statements, and assertions
2. **SSA Converter (`ssa_converter.py`)**: Converts the parsed program into Static Single Assignment (SSA) form
3. **SMT Generator (`smt_generator.py`)**: Generates SMT constraints from SSA form using Z3 solver
4. **Equivalence Checker**: Verifies if two programs are functionally equivalent

## Features

- Custom programming language parser using Lark
- Support for basic arithmetic operations (+, -, *, /)
- Conditional statements (if)
- Program assertions
- Conversion to SSA form
- SMT constraint generation
- Program equivalence verification using Z3 solver

## Requirements

- Python 3.x
- lark-parser
- z3-solver

## Installation

1. Clone this repository
2. Install the required dependencies:
```bash
pip install lark-parser z3-solver
```

## Usage

Run the program with two input programs to check their equivalence:

```python
python parser.py program1.txt program2.txt
```

### Example Program Format

```
x := 10;
y := 5;
if (x > y) {
    z := x + y;
}
assert(z > 10);
```

## Project Structure

- `parser.py`: Main program and language parser
- `ssa_converter.py`: Converts programs to SSA form
- `smt_generator.py`: Generates and solves SMT constraints
