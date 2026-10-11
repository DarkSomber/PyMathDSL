# PyMathDSL

A small, beginner-friendly **Domain-Specific Language (DSL) for basic mathematics**, written in Python using only the standard library.

**Current version:** Addition and subtraction edition.

PyMathDSL currently supports addition, subtraction, variables, parentheses, and basic linear equation solving. Multiplication, division, modulo, exponentiation, comparisons, and mathematical functions are planned features.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation and Usage](#installation-and-usage)
- [Example Program](#example-program)
- [Language Syntax](#language-syntax)
- [Equation Solving](#equation-solving)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Adding Future Features](#adding-future-features)
- [Testing](#testing)

## Features

### Currently Supported

- **Numbers:** Integers and decimals, with exact decimal arithmetic.
- **Arithmetic:** Addition (`+`) and subtraction (`-`).
- **Unary operators:** Positive (`+`) and negative (`-`) signs.
- **Parentheses:** Group expressions using parentheses.
- **Variables:** Declare variables using `let` and reassign existing variables.
- **Print statements:** Evaluate and display expressions.
- **Equation solving:** Solve basic linear equations containing one unknown variable.
- **Interactive mode:** Enter statements directly into the command line.
- **Script execution:** Run programs saved in `.math` files.
- **Error reporting:** Display understandable errors with line numbers.

### Planned Features

The following features are not available in the current version:

- Multiplication (`*`)
- Division (`/`)
- Modulo (`%`)
- Exponentiation (`^`)
- Comparisons (`==`, `!=`, `<`, `>`, `<=`, `>=`)
- Mathematical functions, including square roots, percentages, and geometry calculations

Using unsupported features in the current version produces a descriptive error.

## Requirements

- Python 3.10 or newer
- No external dependencies required

## Installation and Usage

Clone the repository and navigate to the project directory.

### Interactive Mode

Run:

```bash
python main.py
```

Enter mathematical statements interactively. Type `exit` to quit.

### Run a Script sample

Execute a `.math` file:

```bash
python main.py basic.math (if inside a folder do parent/child // parent/basic.math)
```


Each script uses one statement per line. Blank lines are ignored.

The entire script is parsed before execution. If a syntax error occurs, execution stops before any output is produced. Runtime errors report the relevant line and stop execution.

## Example Program

Create a file named `basic.math`:

```text
let price = 500
let paid = 120

print price - paid
solve x + 4 = 14
```

Expected output:

```text
380
x = 10
```

Another example:

```text
let x = 10
let y = 5

print x + y
print x - y

x = x + 1
print x
```

Expected output:

```text
15
5
11
```

## Language Syntax

### Statements

PyMathDSL supports four statement forms:

| Statement | Purpose | Example |
|---|---|---|
| Variable declaration | Create a variable | `let x = 10` |
| Variable assignment | Update an existing variable | `x = x + 1` |
| Print | Evaluate and display an expression | `print x + 5` |
| Solve | Solve a supported equation | `solve x + 4 = 14` |

### Grammar

The following EBNF grammar describes the current language and matches the intended structure of `parser.py`.

```ebnf
program    = { [ statement ] NEWLINE } [ statement ] ;

statement  = "let" IDENT "=" expression
           | IDENT "=" expression
           | "print" expression
           | "solve" expression "=" expression ;

expression = unary { ( "+" | "-" ) unary } ;

unary      = ( "-" | "+" ) unary
           | primary ;

primary    = NUMBER
           | IDENT
           | "(" expression ")" ;
```

### Operator Precedence

Addition and subtraction have equal precedence and are evaluated from left to right.

For example:

```text
print 10 - 4 - 3
```

Expected output:

```text
3
```

Parentheses can be used to control evaluation order.

### Variables

Variable names must begin with a letter or underscore and may contain letters, digits, and underscores.

The following names are reserved keywords:

- `let`
- `print`
- `solve`

Variables must be declared before use. Reassigning an undeclared variable or referencing an undefined variable produces an error.

### Numeric Output

PyMathDSL uses exact decimal arithmetic.

For example:

```text
print 0.1 + 0.2
print 1.5 + 1.5
```

Expected output:

```text
0.3
3
```

Whole-number results are printed without unnecessary decimal places.

## Equation Solving

PyMathDSL supports equations written using the `solve` statement.

The solver reduces each side of an equation to a linear expression of the form:

\[
ax+b
\]

It then solves for the single unknown variable using exact fractions.

### Examples

```text
solve x + 4 = 14
```

Output:

```text
x = 10
```

Equations can also use previously declared variables as constants:

```text
let a = 4
solve x + a = 10
```

Output:

```text
x = 6
```

### Solver Rules

- An undefined variable represents the unknown.
- Variables that already have values are treated as constants.
- The unknown variable must not have been declared using `let`.
- Solving an equation does not create or assign a variable.
- Equations must contain exactly one unknown variable.
- Only addition and subtraction are currently supported in equation expressions.

For example, the equation below is supported:

```text
solve x + x = 6
```

Output:

```text
x = 3
```

### Unsupported or Invalid Equations

The solver reports errors for:

- Equations containing multiple unknown variables.
- Equations containing no unknown variables.
- Equations with no solution, such as `x + 1 = x + 2`.
- Equations with infinitely many solutions, such as `x = x`.
- Attempts to solve for a variable already declared with `let`.

Multiplication and division are not currently supported in the main language, so more advanced equation forms are outside the current scope.

## How It Works

PyMathDSL uses a lexer, parser, abstract syntax tree (AST), and interpreter to process mathematical statements.

For example:

```text
print 10 - 4
```

The statement passes through the following stages:

1. **Lexer:** Converts the source text into tokens, such as `print`, `10`, `-`, and `4`.
2. **Parser:** Builds an AST representing the print statement and subtraction operation.
3. **Interpreter:** Evaluates the subtraction using its `OPERATORS` table.
4. **Output:** Displays the result, `6`.

Conceptually, the AST resembles:

```text
Print(
    BinOp("-", 10, 4)
)
```

The language evaluates its own parsed representation rather than executing the source as Python code. Python's `eval()` and `exec()` are not used.

## Project Structure

```text
PyMathDSL/
├── main.py
├── lexer.py
├── parser.py
├── ast_nodes.py
├── interpreter.py
├── environment.py
├── errors.py
├── numeric.py
├── equation_solver.py
└── README.md
```

| File or directory | Responsibility |
|---|---|
| `main.py` | Command-line interface and program execution |
| `lexer.py` | Converts source text into tokens |
| `parser.py` | Converts tokens into a structured syntax tree |
| `ast_nodes.py` | Defines AST node classes |
| `interpreter.py` | Evaluates expressions and executes statements |
| `environment.py` | Stores and manages variables |
| `errors.py` | Defines language-specific errors |
| `numeric.py` | Provides exact-number helpers and output formatting |
| `equation_solver.py` | Solves supported linear equations |


## Adding Future Features

The project contains prepared implementations for planned features under `future_features/`.

Search the codebase for `FUTURE` to locate integration points.

**Important:** When implementing a feature consult me after to test and fix it since I am the only one who sorta understands how these works. 

### Feature Integration Guide

| Feature | Main integration points |
|---|---|
| Multiplication, division, and modulo | `lexer.py`, `parser.py`, `interpreter.py` |
| Exponentiation | `lexer.py`, `parser.py`, and the interpreter's operator table |
| Comparisons | `lexer.py`, `parser.py`, and the interpreter's operator table |
| Mathematical functions | `lexer.py`, `ast_nodes.py`, `parser.py`, `interpreter.py`, and `equation_solver.py` |
| New operators | Lexer token definitions, parser precedence rules, and interpreter operator definitions |

### General Integration Steps

1. Locate the relevant `FUTURE` comments.
2. Code the corresponding Feature.
3. Review the corresponding implementations you added.
4. Update the grammar and README to reflect the newly supported syntax.
5. Run a test suite for that feature:

   ```bash
   example code for test:
   python -m unittest
   ```

8. Verify that existing functionality remains unchanged.

### Notes on Planned Features

**Multiplication, division, and modulo**

These require updates to token recognition, parser precedence levels, and the interpreter's operator table.

**Exponentiation**

This requires a dedicated precedence rule so that exponentiation behaves correctly relative to unary operators and other arithmetic operations.

**Comparisons**

The lexer must recognize both single-character and multi-character comparison operators. The parser must assign the correct precedence.

**Mathematical functions**

Function support requires function-call parsing, an AST representation for calls, a controlled function registry, and appropriate handling in the equation solver.

**New operators**

A new operator generally requires a lexer token, a parser precedence rule, and an interpreter implementation.

Always confirm the actual integration points in the current source code before applying changes.

Additional tests for planned features are stored in:

```text
please add the feature in the future as the creature go the creature feature
```

These tests are not necessarily compatible with the current implementation until their associated features have been integrated.

The project includes prepared tests for future arithmetic operators, comparisons, functions, and equation-solving extensions. Run those tests after integration to verify the new functionality.

## Project Status

PyMathDSL is currently an educational mathematics DSL focused on addition, subtraction, variables, parentheses, and basic linear equation solving.

The architecture is designed to allow additional mathematical operations to be integrated incrementally without replacing the entire interpreter.

The priority is to maintain a small, understandable, and testable language that demonstrates how a DSL can be implemented using Python.

---
