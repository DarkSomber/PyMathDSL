# PyMathDSL

A small, beginner-friendly **Domain-Specific Language (DSL) for basic mathematics**, written in Python using only the standard library.

PyMathDSL reads programs made of simple math statements, checks them, and runs them with its own interpreter. It supports the six arithmetic operators, variables, parentheses, and solving linear equations with one unknown. Comparisons and built-in functions are planned.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation and Usage](#installation-and-usage)
- [Example Programs](#example-programs)
- [Language Reference](#language-reference)
- [Equation Solving](#equation-solving)
- [Errors](#errors)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Roadmap](#roadmap)

## Features

### Currently supported

- **Numbers:** integers and decimals, stored as exact fractions.
- **Arithmetic:** addition `+`, subtraction `-`, multiplication `*`, division `/`, modulo `%`, and exponentiation `^`.
- **Unary signs:** `+` and `-` in front of a value, such as `-5`.
- **Parentheses:** group expressions to control evaluation order.
- **Variables:** declare with `let`, update with plain assignment.
- **Print statements:** evaluate and display an expression.
- **Equation solving:** solve linear equations that contain one unknown.
- **Interactive mode (REPL):** type statements one at a time.
- **Script mode:** run programs saved in `.math` files.
- **Clear errors:** messages name the kind of problem and, in scripts, the line and column.

### Not available yet

- Comparisons (`==`, `!=`, `<`, `>`, `<=`, `>=`)
- Built-in functions (such as square root, percentages, geometry formulas)
- Comments and conditional statements

Using `<` or `>` today gives a friendly "not available yet" message, and writing a function call gives "Functions aren't available yet."

## Requirements

- Python 3.10 or newer
- No external packages

## Installation and Usage

Clone the repository and open a terminal in the project folder.

### Interactive mode

```bash
python main.py
```

Type statements at the `>>>` prompt. Variables stay available for the whole session. Type `exit` or `quit` to leave (or press `Ctrl+D` / `Ctrl+C`).

### Run a script

```bash
python main.py basic.math
```

If the file is inside a folder, include the path, for example `python main.py examples/basic.math`.

Script rules:

- One statement per line. Blank lines are ignored.
- The whole file is checked for syntax errors **before** anything runs, so a syntax error produces no output at all.
- Runtime errors (for example dividing by zero) stop the script at that line, after any earlier output has been printed.
- The exit code is `0` on success, `1` if the file cannot be opened or an error occurs, and `2` for wrong command-line usage.

## Example Programs

Save as `basic.math`:

```text
let price = 500
let paid = 120

print price - paid
solve x + 4 = 14
```

Output:

```text
380
x = 10
```

Using the operators:

```text
let a = 7

print a * 3
print a / 2
print a % 4
print 2 ^ 10
print 2 + 3 * 4
print (2 + 3) * 4
print 0.1 + 0.2
```

Output:

```text
21
3.5
3
1024
14
20
0.3
```

Updating a variable:

```text
let x = 10
x = x + 1
print x
```

Output:

```text
11
```

## Language Reference

### Statements

| Statement | Purpose | Example |
|---|---|---|
| Declaration | Create a variable (or replace its value) | `let x = 10` |
| Assignment | Update a variable that already exists | `x = x + 1` |
| Print | Evaluate and display an expression | `print x * 2` |
| Solve | Solve an equation for its unknown | `solve 2 * x + 3 = 11` |

### Keywords

`let`, `print`, and `solve` are reserved and cannot be used as variable names.

### Variables

- Names start with a letter (A to Z, a to z) or an underscore, followed by letters, digits, or underscores.
- A variable must be declared with `let` before it is used. Assigning to or reading an undeclared variable is an error.
- Variables hold numbers only. True/false results are not allowed in variables.

### Numbers

- Write integers (`42`) and decimals (`3.5`). A decimal point needs digits on both sides, so `5.` and `.5` are errors.
- Negative numbers are written with the unary minus: `-5`.
- Arithmetic is exact: `0.1 + 0.2` gives exactly `0.3`.
- Whole-number results print without a decimal point.
- Results that are not whole numbers print as decimals. For example, `1 / 3` prints `0.3333333333333333`.

### Operators and precedence

From highest to lowest precedence:

| Level | Operators | Grouping |
|---|---|---|
| 1 | `( )` | n/a |
| 2 | `^` | right to left |
| 3 | unary `+` `-` | n/a |
| 4 | `*` `/` `%` | left to right |
| 5 | `+` `-` | left to right |

Examples:

```text
print 10 - 4 - 3      # 3, evaluated as (10 - 4) - 3
print 2 ^ 3 ^ 2       # 512, evaluated as 2 ^ (3 ^ 2)
print -2 ^ 2          # -4, evaluated as -(2 ^ 2)
print 2 + 3 * 4       # 14
```

(The `#` notes above are for explanation only. Comments are not supported in PyMathDSL programs.)

Operator limits:

- Division or modulo by zero is an error.
- An exponent larger than 999 in absolute value is rejected as too large.
- A negative base raised to a fractional power is an error.
- Results that are too large to calculate are reported as errors.

### Grammar

```ebnf
program    = { [ statement ] NEWLINE } [ statement ] ;

statement  = "let" IDENT "=" expression
           | IDENT "=" expression
           | "print" expression
           | "solve" expression "=" expression ;

expression = term { ( "+" | "-" ) term } ;
term       = unary { ( "*" | "/" | "%" ) unary } ;
unary      = ( "-" | "+" ) unary | power ;
power      = primary [ "^" unary ] ;
primary    = NUMBER | IDENT | "(" expression ")" ;

NUMBER     = DIGIT { DIGIT } [ "." DIGIT { DIGIT } ] ;
IDENT      = ( LETTER | "_" ) { LETTER | DIGIT | "_" } ;
```

## Equation Solving

The `solve` statement finds the value of one unknown variable in a linear equation. Each side is reduced to the form `a*x + b` using exact fractions, and then `x` is isolated.

```text
solve x + 4 = 14
```

```text
x = 10
```

More examples:

```text
solve 2 * x + 3 = 11
solve x / 4 = 3
solve 3 * (x - 1) = 12
```

```text
x = 4
x = 12
x = 5
```

Equations can use variables you have already declared as constants:

```text
let a = 4
solve x + a = 10
```

```text
x = 6
```

### Solver rules

- Any name **without** a value is the unknown. Names that already have values are constants.
- The equation must contain exactly one unknown. To solve for a variable, do not declare it with `let` first.
- `solve` prints the answer but does not create or change any variable.
- The equation must be linear in the unknown. Multiplying the unknown by itself, dividing by an expression that contains it, or using it with `^` or `%` is not supported.

### Solver errors

| Situation | Example |
|---|---|
| More than one unknown | `solve x + y = 3` |
| No unknown (everything already has a value) | `let x = 2` then `solve x = 2` |
| No solution | `solve x + 1 = x + 2` |
| Infinitely many solutions | `solve x = x` |
| Not linear | `solve x * x = 4` |

## Errors

Every error has a category and a message:

```text
Name error on line 1: The variable 'y' is not defined. Declare it first with: let y = ...
```

In interactive mode the line number is left out, since each entry is a single line.

| Category | Cause | Example |
|---|---|---|
| Syntax error | Invalid character, malformed number, or malformed statement | `print 5 +` |
| Name error | Undeclared or undefined variable, reserved name used as a variable | `print y` |
| Math error | Division by zero, impossible operation, or a number too large | `print 5 / 0` |
| Type error | A true/false value used where a number is needed | (reserved for comparisons) |
| Equation error | The `solve` rules above were broken | `solve x + 1 = x + 2` |

## How It Works

PyMathDSL processes each program in stages:

1. **Lexer:** converts source text into tokens, recording line and column.
2. **Parser:** a recursive-descent parser that builds an abstract syntax tree (AST).
3. **Interpreter:** walks the tree and calculates results, storing variables in the environment.
4. **Output:** prints results, or reports an error.

Example: `print 2 + 3 * 4` becomes

```text
Print
 └─ BinOp(+)
     ├─ Number(2)
     └─ BinOp(*)
         ├─ Number(3)
         └─ Number(4)
```

`3 * 4` sits deeper in the tree because `*` has higher precedence, so it is calculated first.

The interpreter evaluates the tree itself. Python's `eval()` and `exec()` are never used, so program text can never run as Python code.

Semantic checks (declared before use, numbers only, one unknown in `solve`, no division by zero) happen while the interpreter runs rather than in a separate pass.

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
├── requirements.txt
└── README.md
```

| File | Responsibility |
|---|---|
| `main.py` | Command-line interface: interactive mode and script mode |
| `lexer.py` | Converts source text into tokens |
| `parser.py` | Converts tokens into an AST (precedence is set by `BINARY_LEVELS`) |
| `ast_nodes.py` | AST node definitions |
| `interpreter.py` | Executes statements and evaluates expressions (operators in the `OPERATORS` table) |
| `environment.py` | Variable storage and declaration rules |
| `errors.py` | Error classes and message formatting |
| `numeric.py` | Number helpers and output formatting |
| `equation_solver.py` | Linear equation solver for `solve` |

## Testing

Check the basics by running these in interactive mode and comparing the output:

| Input | Expected output |
|---|---|
| `print 2 + 3 * 4` | `14` |
| `print 10 - 4 - 3` | `3` |
| `print 2 ^ 3 ^ 2` | `512` |
| `print -2 ^ 2` | `-4` |
| `print 0.1 + 0.2` | `0.3` |
| `solve x + 4 = 14` | `x = 10` |
| `print y` | Name error |
| `print 5 / 0` | Math error |
| `print 5 +` | Syntax error |

If you add automated tests in a `tests/` folder, run them with:

```bash
python -m unittest discover tests
```

## Roadmap

Planned features, in no fixed order:

- **Comparisons:** `==`, `!=`, `<`, `>`, `<=`, `>=`, producing true/false results.
- **Built-in functions:** such as square root, percentage, and geometry formulas.

Search the source for `FUTURE` comments to find where each feature plugs in. In general:

| Feature | Parts to change |
|---|---|
| New binary operator | Token set in `lexer.py`, a row in `BINARY_LEVELS` in `parser.py`, an entry in `OPERATORS` in `interpreter.py` |
| Comparisons | Multi-character tokens in `lexer.py`, a loosest precedence level in `parser.py`, operator entries in `interpreter.py` |
| Functions | A `Call` node in `ast_nodes.py`, call parsing in `parser.py`, evaluation in `interpreter.py`, and handling in `equation_solver.py` |

When you add a feature, update the grammar and examples in this README, and run your tests to confirm that existing behavior has not changed.