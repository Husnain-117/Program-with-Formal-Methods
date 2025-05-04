Program Equivalence Checker
A formal methods tool that checks program equivalence using SSA form and SMT solving.
Overview
This project implements a program equivalence checker using formal methods techniques. It consists of several components:

Parser (parser.py): Parses a simple programming language with assignments, if statements, loops, and assertions
SSA Converter (ssa_converter.py): Converts the parsed program into Static Single Assignment (SSA) form
SMT Generator (smt_generator.py): Generates SMT constraints from SSA form using Z3 solver
Equivalence Checker: Verifies if two programs are functionally equivalent

Features

Custom programming language parser using Lark
Support for basic arithmetic operations (+, -, *, /)
Conditional statements (if)
Loop constructs (for, while) with loop unrolling
Program assertions
Conversion to SSA form
SMT constraint generation
Program equivalence verification using Z3 solver

Requirements

Python 3.x
lark-parser
z3-solver

Installation

Clone this repository
Install the required dependencies:

pip install lark-parser z3-solver

Usage
Run the program with two input programs to check their equivalence:
python parser.py program1.txt program2.txt

Example Program Format
x := 10;
y := 5;
if (x > y) {
    z := x + y;
}
assert(z > 10);

Example with Loop
for (i := 0; i < 3; i := i + 1) {
    x := x + 1;
}
assert(x >= 3);

Project Structure

parser.py: Main program and language parser
ssa_converter.py: Converts programs to SSA form
smt_generator.py: Generates and solves SMT constraints
mini_lang.lark: Grammar definition for the mini-language

Notes

Loops are unrolled up to 3 iterations to ensure finite execution for analysis.
The SSA converter processes unrolled loops as sequences of conditional statements.

