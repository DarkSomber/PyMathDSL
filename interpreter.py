"""Interpreter: walks the AST and computes results. Nothing is ever passed to eval()/exec()."""
from ast_nodes import Assign, BinOp, Call, Let, Number, Print, Solve, UnaryOp, Var
from environment import Environment
from equation_solver import solve_linear
from errors import (DeclarationError, DivisionByZeroError, MathDomainError, MathDSLError,
                    MathTypeError)
from numeric import TOO_LARGE, check_finite, format_number, is_number
from functions import call_function, is_function


# Every binary operator and what it does. The parser decides precedence (BINARY_LEVELS in
# parser.py); this table decides behavior. Values are exact fractions (0.1 + 0.2 is exactly 0.3).
OPERATORS = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
    "%": lambda a, b: a % b,
    "^": lambda a, b: a ** b,
    "==": lambda a, b: a == b,
    "~=": lambda a, b: a != b,
    "<": lambda a, b: a < b,
    ">": lambda a, b: a > b,
    "<=": lambda a, b: a <= b,
    ">=": lambda a, b: a >= b,
}
# A new binary operator also needs its symbol in lexer.ONE_CHAR_OPS / TWO_CHAR_OPS and a level
# in parser.BINARY_LEVELS.


class Interpreter:
    def __init__(self, env=None):
        self.env = env or Environment()

    # ---- statements ----
    def run(self, statements):
        """Execute statements in order; return the printed lines."""
        outputs = []
        for stmt in statements:
            line = self.execute(stmt)
            if line is not None:
                outputs.append(line)
        return outputs

    def execute(self, stmt):
        """Execute one statement. Returns text to display, or None."""
        try:
            return self._execute(stmt)
        except MathDSLError as err:
            if err.line is None and stmt.line:
                err.line = stmt.line
            raise
        except RecursionError:
            raise MathDomainError("This expression is nested too deeply.", stmt.line or None) from None

    def _execute(self, stmt):
        if isinstance(stmt, Let):
            if is_function(stmt.name):
                raise DeclarationError(f"'{stmt.name}' is a built-in function name; pick another.")
            self.env.declare(stmt.name, self.evaluate(stmt.expr))
        elif isinstance(stmt, Assign):
            self.env.require_declared(stmt.name)
            self.env.assign(stmt.name, self.evaluate(stmt.expr))
        elif isinstance(stmt, Print):
            return format_number(self.evaluate(stmt.expr))
        elif isinstance(stmt, Solve):
            name, value = solve_linear(stmt.left, stmt.right, self.evaluate, self.env.has)
            return f"{name} = {format_number(value)}"
        else:
            raise MathDSLError("That kind of statement isn't supported.")
        return None

    # ---- expressions ----
    def evaluate(self, node):
        if isinstance(node, Number):
            return node.value
        if isinstance(node, Var):
            return self.env.get(node.name)
        if isinstance(node, UnaryOp):
            value = self._number(self.evaluate(node.operand), f"Unary '{node.op}'")
            return -value if node.op == "-" else value
        if isinstance(node, BinOp):
            return self._binary(node.op, self.evaluate(node.left), self.evaluate(node.right))
        if isinstance(node, Call):
            args = [self.evaluate(arg) for arg in node.args]
            try:
                result = call_function(node.name, args)
            except OverflowError:       # e.g. areaCircle(10 ^ 200): float overflow inside a function
                raise MathDomainError(TOO_LARGE) from None
            return check_finite(result)
        raise MathDSLError("That kind of expression isn't supported.")

    @staticmethod
    def _number(value, context):
        # true/false results (from comparisons) must not be used as numbers.
        if not is_number(value):
            raise MathTypeError(f"{context} needs numbers, but got {format_number(value)}.")
        return value

    def _binary(self, symbol, a, b):
        a, b = self._number(a, f"'{symbol}'"), self._number(b, f"'{symbol}'")
        if symbol == "^" and abs(b) > 999:   # a limit per step; nested cases like (9 ^ 999) ^ 999 are caught later
            raise MathDomainError(TOO_LARGE)
        try:
            result = OPERATORS[symbol](a, b)
            if isinstance(result, complex):   # a negative base with a fractional exponent
                raise MathDomainError("A negative number can't be raised to a fractional power.")
            return check_finite(result)
        except OverflowError:
            raise MathDomainError(TOO_LARGE) from None
        except ZeroDivisionError: 
            raise DivisionByZeroError("Cannot divide by zero") from None