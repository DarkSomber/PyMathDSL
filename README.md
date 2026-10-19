# PyMathDSL

PyMathDSL is a small, beginner-friendly **domain-specific language (DSL) for basic mathematics**, written in Python using only the standard library.

You write short programs made of simple math statements. PyMathDSL reads them, checks them, and runs them with its own interpreter. It supports arithmetic, comparisons, variables, parentheses, built-in math functions (rounding, percentages, geometry), and solving linear equations with one unknown. Numbers are stored as exact fractions wherever possible, so `0.1 + 0.2` is exactly `3/10` and never `0.30000000000000004`.

Python's `eval()` and `exec()` are never used, so program text can never run as Python code.

## Table of Contents

- [Prerequisites and Setup](#prerequisites-and-setup)
- [Launching the REPL](#launching-the-repl)
- [Running a `.math` Script](#running-a-math-script)
- [Language Reference](#language-reference)
  - [Numbers and how results are displayed](#numbers-and-how-results-are-displayed)
  - [Arithmetic operators](#arithmetic-operators)
  - [Unary signs, parentheses, and precedence](#unary-signs-parentheses-and-precedence)
  - [Comparisons and boolean results](#comparisons-and-boolean-results)
  - [Variables: `let` and reassignment](#variables-let-and-reassignment)
  - [Print](#print)
  - [Solving linear equations with `solve`](#solving-linear-equations-with-solve)
  - [Built-in functions](#built-in-functions)
  - [Grammar](#grammar)
- [Error Handling](#error-handling)
- [Project Structure](#project-structure)
- [Verified Examples](#verified-examples)
- [Current Limitations](#current-limitations)

## Prerequisites and Setup

- Python 3.10 or newer
- No external packages. `requirements.txt` only records this.

There is nothing to install. Put the project files in one folder, open a terminal there, and run `main.py` with Python. On some systems the command is `python3` instead of `python`.

## Launching the REPL

Run `main.py` with no arguments:

```bash
python main.py
```

You will see a banner and a prompt:

```text
Math DSL - type 'exit' to quit.
>>>
```

Type one statement per line. Variables stay available for the whole session.

- Leave with `exit` or `quit`, or press `Ctrl+C` or `Ctrl+D` (on Windows, `Ctrl+Z` then `Enter`).
- If you make a mistake, the error is shown and the session keeps going, so you do not lose your variables.
- Errors in the REPL do not show a line number, since every entry is a single line.

A short session:

```text
>>> let x = 5
>>> print x * 2
10
>>> print x < 10
true
>>> solve z + 1 = 3
z = 2
>>> print y
Name error: The variable 'y' is not defined. Declare it first with: let y = ...
```

## Running a `.math` Script

Save your statements in a text file (conventionally with the `.math` extension) and pass its path to `main.py`:

```bash
python main.py basic.math
```

If the file is in a folder, include the path, for example `python main.py my_scripts/basic.math`. The file must be UTF-8 text.

For example, save this as `basic.math`:

```text
let price = 500
let paid = 120

print price - paid
solve x + 4 = 14
```

Running it prints:

```text
380
x = 10
```

Script rules:

- One statement per line. Blank lines are ignored.
- The whole file is checked for syntax errors **before** anything runs. If there is a syntax error, nothing is printed except the error.
- A runtime error (for example dividing by zero) stops the script at that line. Anything printed earlier stays printed.
- Output goes to standard output. Errors go to standard error.
- Exit codes: `0` on success, `1` if the file cannot be opened or read, or if an error occurs, and `2` if you pass more than one argument.

## Language Reference

### Numbers and how results are displayed

Write integers (`42`) and decimals (`3.5`). A decimal point needs digits on both sides, so `5.` and `.5` are errors. There is no scientific notation (`1e3` is an error), and a minus sign is the unary minus (`-5`), not part of the number.

Internally a value is either an **exact fraction** or a **float**:

- Number literals and the operators `+ - * / % ^` give exact fractions. The exception is `^` with a fractional exponent, which gives a float (for example `2 ^ 0.5`).
- `frac` gives an exact fraction. `dec`, `roundUp`, `roundDown`, `sqrt`, `pct`, `percentage`, and all the geometry functions give floats.
- Once a float enters a calculation, the result is a float.

How a result is printed:

| Kind of value | How it prints | Example |
|---|---|---|
| Whole number (fraction or float) | No decimal point | `print 10 / 5` gives `2` |
| Non-whole exact fraction | As `numerator/denominator` | `print 7 / 2` gives `7/2` |
| Non-whole float | As a decimal | `print sqrt(2)` gives `1.4142135623730951` |
| Comparison result | `true` or `false` | `print 2 < 3` gives `true` |

Use `dec(...)` when you want a decimal instead of a fraction: `print dec(7 / 2)` gives `3.5`. Float results can show normal floating-point noise, for example `print areaRectangle(0.1, 0.2)` gives `0.020000000000000004`.

### Arithmetic operators

| Operator | Meaning | Example | Result |
|---|---|---|---|
| `+` | Addition | `print 7 + 3` | `10` |
| `-` | Subtraction | `print 7 - 3` | `4` |
| `*` | Multiplication | `print 7 * 3` | `21` |
| `/` | Division | `print 7 / 2` | `7/2` |
| `%` | Remainder (modulo) | `print 7 % 4` | `3` |
| `^` | Exponent | `print 2 ^ 10` | `1024` |

Notes:

- `%` takes the sign of the right-hand number, like Python: `-7 % 3` is `2` and `7 % -3` is `-2`. It also works on decimals: `7.5 % 2` is `3/2`.
- Division or remainder by zero is a Math error.
- `^` accepts negative and fractional exponents (`2 ^ -1` is `1/2`), but an exponent larger than 999 in absolute value is rejected as too large. A negative base with a fractional exponent, such as `(-8) ^ (1 / 3)`, is an error.
- Results that are too large to calculate are reported as Math errors.
- There is no implicit multiplication. Write `2 * x`, not `2x`.

### Unary signs, parentheses, and precedence

A `+` or `-` in front of a value is a unary sign: `-5`, `+5`, `- -5` (which is `5`), `2 * -3` (which is `-6`).

Parentheses group expressions: `print (2 + 3) * 4` gives `20`.

From highest precedence to lowest:

| Level | Operators | Grouping |
|---|---|---|
| 1 | `( )` and function calls | n/a |
| 2 | `^` | right to left |
| 3 | unary `+` and `-` | n/a |
| 4 | `*` `/` `%` | left to right |
| 5 | `+` `-` | left to right |
| 6 | `==` `~=` `<` `>` `<=` `>=` | not chainable |

What that means in practice:

```text
print 10 - 4 - 3
print 2 ^ 3 ^ 2
print -2 ^ 2
print (-2) ^ 2
print 2 ^ -1
print 2 + 3 * 4
```

```text
3
512
-4
4
1/2
14
```

- `10 - 4 - 3` is `(10 - 4) - 3`.
- `2 ^ 3 ^ 2` is `2 ^ (3 ^ 2)`.
- `-2 ^ 2` is `-(2 ^ 2)`, because `^` binds tighter than a unary sign. The exponent itself may carry a sign, which is why `2 ^ -1` works.

### Comparisons and boolean results

| Operator | Meaning |
|---|---|
| `==` | equal to |
| `~=` | not equal to (this language uses `~=`, **not** `!=`) |
| `<` | less than |
| `>` | greater than |
| `<=` | less than or equal to |
| `>=` | greater than or equal to |

A comparison produces `true` or `false`:

```text
let price = 500
let paid = 120
print price > paid
print price == paid
print 0.1 + 0.2 == 0.3
print 1 / 3 == 2 / 6
```

```text
true
false
true
true
```

Rules for boolean results:

- Comparisons have the loosest precedence, so arithmetic on each side is done first: `print 1 + 1 == 2` gives `true`.
- Comparisons cannot be chained. `1 < 2 < 3` and `1 == 1 == 1` are syntax errors. Compare two values at a time.
- `true` and `false` are results to display, not values you can type or store. They are not numbers: they cannot be used in arithmetic, passed to functions, compared again (`(1 < 2) == (2 < 3)` is a Type error), or stored in a variable (`let b = 1 < 2` is a Type error). Use `print` to see them.
- `!=` is not recognized. Use `~=`.
- A single `=` is never a comparison. It is only used in `let`, reassignment, and `solve`.

### Variables: `let` and reassignment

| Statement | Purpose | Example |
|---|---|---|
| Declaration | Create a variable (or replace the value of an existing one) | `let x = 10` |
| Reassignment | Update a variable that already exists | `x = x + 1` |

```text
let x = 10
x = x + 1
print x
```

```text
11
```

Rules:

- Names start with an ASCII letter (A to Z, a to z) or an underscore, followed by letters, digits, or underscores. Names are case-sensitive.
- `let`, `print`, and `solve` are reserved keywords (lowercase) and cannot be variable names.
- The names of built-in functions (such as `sqrt`) cannot be used as variable names.
- A variable must be declared with `let` before it is read or reassigned. Reading or reassigning an undeclared variable is a Name error.
- Variables hold numbers only, never true/false results.
- A variable can hold the result of a function call: `let area = areaRectangle(3, 4)`.

### Print

`print <expression>` evaluates an expression and shows the result.

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

```text
21
7/2
3
1024
14
20
3/10
```

An expression on its own line does nothing useful here and is a syntax error. To use a value, wrap it in `print` or store it with `let`. This includes function calls: `sqrt(4)` alone on a line gives "Did you forget 'print'?".

### Solving linear equations with `solve`

`solve` finds the value of one unknown variable in a linear equation. Both sides are reduced to the form `a*x + b` using exact fractions, and then `x` is isolated.

```text
solve x + 4 = 14
solve 2 * x + 3 = 11
solve x / 4 = 3
solve 3 * (x - 1) = 12
solve 2 * x = 3
```

```text
x = 10
x = 4
x = 12
x = 5
x = 3/2
```

Variables that already have values act as constants:

```text
let a = 4
solve x + a = 10
```

```text
x = 6
```

Built-in function calls are fine as long as they do not contain the unknown: `solve x + sqrt(4) = 5` gives `x = 3`.

Solver rules:

- Any name **without** a value is the unknown. The equation must contain exactly one unknown. To solve for a variable, do not declare it with `let` first.
- `solve` only prints the answer. It does not create or change any variable.
- Each side of the `=` is an arithmetic expression. Comparison operators (`==`, `<`, and so on) are not allowed inside a `solve` statement.
- The equation must be **linear** in the unknown. You can add, subtract, and negate expressions containing the unknown, multiply by constants, and divide by constants (`solve x / 4 = 3`).
- Not supported when they involve the unknown: multiplying it by itself, dividing by an expression containing it, `^`, `%`, and function calls such as `sqrt(x)`.

Solver errors (all reported as an Equation error unless noted):

| Situation | Example |
|---|---|
| More than one unknown | `solve x + y = 3` |
| No unknown (everything already has a value) | `let x = 2` then `solve x = 2` |
| No solution | `solve x + 1 = x + 2` |
| Infinitely many solutions | `solve x = x` |
| Not linear | `solve x * x = 4`, `solve 4 / x = 2`, `solve x ^ 2 = 4`, `solve sqrt(x) = 2` |
| Dividing by a constant zero (Math error) | `solve x / 0 = 1` |
| A true/false value used as a number (Type error) | `solve x = (1 < 2)` |

### Built-in functions

Call a function by name with arguments in parentheses, separated by commas: `sqrt(16)`, `areaRectangle(3, 4)`. Calls can be nested (`sqrt(sqrt(16))`) and used anywhere a value is allowed, including in `let`, `print`, and arithmetic.

General rules for every function:

- Every argument must be a number. A true/false value is a Type error.
- The wrong number of arguments is a Function error, and the message lists the parameters.
- An unknown function name is a Function error.
- A function call on its own line must be wrapped in `print` or stored with `let`.

#### Conversion and rounding

| Function | Arguments | What it does | Example | Result |
|---|---|---|---|---|
| `frac` | `(value)` | Converts a number to an exact fraction. A float is read as the decimal it displays. | `frac(0.75)` | `3/4` |
| `dec` | `(value)` | Converts a number to a float (a decimal). | `dec(1 / 3)` | `0.3333333333333333` |
| `roundUp` | `(value, decimalPlaces)` | Rounds toward positive infinity. | `roundUp(3.14159, 2)` | `3.15` |
| `roundDown` | `(value, decimalPlaces)` | Rounds toward negative infinity. | `roundDown(3.14159, 2)` | `3.14` |

Rounding details:

- Rounding uses exact fractions, so values like `0.07` are never nudged by floating-point error: `roundUp(0.07, 2)` is `0.07`.
- The direction is always toward `+` or `-` infinity, so negatives behave accordingly: `roundUp(-1.11, 1)` is `-1.1` and `roundDown(-1.11, 1)` is `-1.2`.
- `decimalPlaces` must be a whole number from `0` to `999`. `2.0` is accepted, but `1.5`, negative values, and values over 999 are Function errors.

More examples:

```text
print frac(dec(0.1))
print roundUp(2.1, 0)
print roundDown(2.5, 0)
print roundUp(1 / 3, 3)
```

```text
1/10
3
2
0.334
```

#### Roots and percentages

| Function | Arguments | What it does | Example | Result |
|---|---|---|---|---|
| `sqrt` | `(value)` | Square root. A negative value is a Math error. | `sqrt(16)` | `4` |
| `pct` | `(value)` | Converts a percent to a decimal by dividing by 100. | `pct(50)` | `0.5` |
| `percentage` | `(part, total)` | What percent `part` is of `total`. A zero total is a Math error. | `percentage(25, 200)` | `12.5` |

`sqrt(2)` gives `1.4142135623730951`, `pct(7.5)` gives `0.075`, and `percentage(1, 3)` gives `33.33333333333333`.

#### Geometry

| Function | Arguments (in order) | Returns | Example | Result |
|---|---|---|---|---|
| `areaCircle` | `(radius)` | Area of a circle | `areaCircle(1)` | `3.141592653589793` |
| `perimeterCircle` | `(radius)` | Circumference of a circle | `perimeterCircle(5)` | `31.41592653589793` |
| `circleCircumference` | `(radius)` | Same as `perimeterCircle` | `circleCircumference(5)` | `31.41592653589793` |
| `areaTriangle` | `(base, height)` | Area of a triangle | `areaTriangle(10, 4)` | `20` |
| `perimeterTriangle` | `(sideA, sideB, sideC)` | Sum of the three sides | `perimeterTriangle(3, 4, 5)` | `12` |
| `areaRectangle` | `(width, height)` | Area of a rectangle | `areaRectangle(3, 4)` | `12` |
| `perimeterRectangle` | `(width, height)` | Perimeter of a rectangle | `perimeterRectangle(3, 4)` | `14` |

- A negative radius, side, base, height, or width is a Math error. For example, `areaCircle(-1)` gives "Radius cannot be negative." and `areaRectangle(-1, 2)` gives "Rectangle dimensions cannot be negative."
- `perimeterTriangle` only adds the three sides. It does not check that they can form a triangle.

A script that combines several functions:

```text
let radius = 5
let area = areaCircle(radius)
print roundUp(area, 2)
print roundDown(area, 2)
print percentage(25, 200)
print pct(50)
print frac(0.75)
print dec(1 / 3)
print sqrt(16)
print areaRectangle(3, 4)
print perimeterTriangle(3, 4, 5)
```

```text
78.54
78.53
12.5
0.5
3/4
0.3333333333333333
4
12
12
```

### Grammar

This grammar matches the lexer and parser.

```ebnf
program    = { [ statement ] NEWLINE } [ statement ] ;

statement  = "let" IDENT "=" expression
           | IDENT "=" expression
           | "print" expression
           | "solve" sum "=" sum ;

expression = comparison ;
comparison = sum [ ( "==" | "~=" | "<" | ">" | "<=" | ">=" ) sum ] ;   (* not chainable *)
sum        = product { ( "+" | "-" ) product } ;
product    = unary { ( "*" | "/" | "%" ) unary } ;
unary      = ( "-" | "+" ) unary | power ;
power      = primary [ "^" unary ] ;
primary    = NUMBER | IDENT | call | "(" expression ")" ;
call       = IDENT "(" [ expression { "," expression } ] ")" ;

NUMBER     = DIGIT { DIGIT } [ "." DIGIT { DIGIT } ] ;
IDENT      = ( LETTER | "_" ) { LETTER | DIGIT | "_" } ;
```

Notes on the grammar:

- `let`, `print`, and `solve` are keywords. `LETTER` means an ASCII letter.
- Spaces, tabs, and carriage returns between tokens are ignored. Statements are separated by newlines.
- Both sides of a `solve` statement are `sum`, so they cannot contain comparisons.
- The grammar only describes the shape of the code. Rules that need values, such as declaring variables before use or the linearity rule for `solve`, are checked while the program runs.

## Error Handling

Every error has a category and a message:

```text
Name error on line 1: The variable 'y' is not defined. Declare it first with: let y = ...
```

| Category | Cause | Example |
|---|---|---|
| Syntax error | Invalid character, malformed number, malformed statement, or a chained comparison | `print 5 +`, `print 5 @ 3`, `print 1 < 2 < 3` |
| Name error | Undeclared variable, or a reserved or built-in name used as a variable | `print y`, `y = 3`, `let sqrt = 2` |
| Math error | Division by zero, an impossible operation, or a number that is too large | `print 5 / 0`, `print sqrt(-1)`, `print 10 ^ 1000` |
| Type error | A true/false value used where a number is needed | `let b = 1 < 2`, `print sqrt(1 < 2)` |
| Function error | Unknown function, wrong argument count, or invalid decimal places | `print foo(1)`, `print sqrt(1, 2)`, `print roundUp(1.1, 1.5)` |
| Equation error | A `solve` rule was broken | `solve x + y = 3`, `solve x + 1 = x + 2` |

Line and column reporting:

- **Syntax errors** in a script include the line and the column: `Syntax error on line 3, column 10: ...`
- **Runtime errors** (name, math, type, function, and equation errors) include the line only: `Math error on line 2: Cannot divide by zero`
- **In the REPL** no line or column is shown.
- Errors in scripts are printed to standard error and make the script exit with code `1`.

A script with a syntax error, for example:

```text
let x = 4

print x +
```

prints nothing to standard output and reports:

```text
Syntax error on line 3, column 10: I expected a number, a variable, or '(' but found the end of the line.
```

A script with a runtime error prints its earlier output first:

```text
print 1
print 5 / 0
print 3
```

```text
1
Math error on line 2: Cannot divide by zero
```

## Project Structure

```text
PyMathDSL/
├── main.py
├── lexer.py
├── parser.py
├── ast_nodes.py
├── interpreter.py
├── environment.py
├── functions.py
├── equation_solver.py
├── numeric.py
├── errors.py
├── requirements.txt
├── .gitignore
└── README.md
```

| File | Responsibility |
|---|---|
| `main.py` | Command-line interface: REPL and script mode |
| `lexer.py` | Converts source text into tokens with line and column |
| `parser.py` | Recursive-descent parser that builds the syntax tree (precedence is set by `BINARY_LEVELS`) |
| `ast_nodes.py` | Syntax tree node definitions (numbers, variables, operators, calls, and statements) |
| `interpreter.py` | Executes statements and evaluates expressions (operators live in the `OPERATORS` table) |
| `environment.py` | Variable storage and declaration rules |
| `functions.py` | All built-in functions in one `FUNCTIONS` table, plus argument checks |
| `equation_solver.py` | Linear equation solver used by `solve` |
| `numeric.py` | Number helpers and output formatting |
| `errors.py` | Error classes and message formatting |
| `requirements.txt` | Notes that no external packages are needed (Python 3.10+) |
| `.gitignore` | Keeps `__pycache__/`, `*.pyc`, and editor leftovers out of Git |

There is no `tests/` folder and no `examples/` folder.

How a program runs: the **lexer** turns text into tokens, the **parser** builds a syntax tree, and the **interpreter** walks the tree, using the **environment** for variables, **functions.py** for built-ins, and **equation_solver.py** for `solve`. For example, `print 2 + 3 * 4` becomes:

```text
Print
 └─ BinOp(+)
     ├─ Number(2)
     └─ BinOp(*)
         ├─ Number(3)
         └─ Number(4)
```

`3 * 4` sits deeper in the tree because `*` has higher precedence, so it is calculated first.

## Verified Examples

Each row was run in a fresh session, and the output is exactly what the program printed. Try them in the REPL.

| Input | Output |
|---|---|
| `print 2 + 3 * 4` | `14` |
| `print 10 - 4 - 3` | `3` |
| `print 2 ^ 3 ^ 2` | `512` |
| `print -2 ^ 2` | `-4` |
| `print 0.1 + 0.2` | `3/10` |
| `print 10 / 4` | `5/2` |
| `print 7 % 4` | `3` |
| `print 2 == 2` | `true` |
| `print 2 ~= 3` | `true` |
| `print 2 < 3` | `true` |
| `print 3 > 2` | `true` |
| `print 2 <= 2` | `true` |
| `print 3 >= 3` | `true` |
| `solve x + 4 = 14` | `x = 10` |
| `solve 3 * (x - 1) = 12` | `x = 5` |
| `print sqrt(16)` | `4` |
| `print roundUp(3.14159, 2)` | `3.15` |
| `print percentage(25, 200)` | `12.5` |
| `print areaRectangle(3, 4)` | `12` |
| `print y` | Name error |
| `print 5 / 0` | Math error |
| `print 5 +` | Syntax error |
| `print 1 < 2 < 3` | Syntax error |
| `solve x * x = 4` | Equation error |
| `solve sqrt(x) = 2` | Equation error |

To check script mode, save the `basic.math` example from [Running a `.math` Script](#running-a-math-script), run `python main.py basic.math`, and confirm it prints `380` and `x = 10`, and that the exit code is `0`.

There is no automated test suite yet.

## Current Limitations

- **No comments.** `#` is not supported. The lexer rejects it as an unknown character, so never put `#` in a program.
- **No conditionals.** There is no `if`, no `else`, and no blocks. `if` is not a keyword, so a line starting with it is treated as a variable name and reported as a syntax error.
- **`solve` is limited to linear equations with one unknown.** It supports `+`, `-`, unary signs, multiplication by constants, and division by constants. Powers, remainders, function calls containing the unknown, multiplying the unknown by itself, and dividing by the unknown are rejected. Comparison operators cannot appear in a `solve` statement, and the unknown must not already have a value.
- **`solve` and float values.** If a float from a function (for example `roundUp(0.001, 2)`) appears inside an equation, the solver uses the float's exact binary value, so the answer can be an unexpectedly large fraction.
- **No stored booleans.** `true` and `false` can only be displayed with `print`. They cannot be typed, stored in variables, compared again, or used as numbers.
- **No chained comparisons.** Compare two values at a time.
- **Language features that do not exist:** implicit multiplication (`2x`), scientific notation (`1e3`), strings, user-defined functions, loops, input, several statements on one line, and non-ASCII variable names.
- **Limits:** an exponent larger than 999 in absolute value, decimal places above 999 for `roundUp` and `roundDown`, and results too large to calculate are all reported as errors.
- **Function results are floats.** Results from `dec`, `sqrt`, `pct`, `percentage`, the rounding functions, and the geometry functions show normal floating-point rounding behavior.