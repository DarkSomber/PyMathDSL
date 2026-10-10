"""Error types. Each category is its own class so callers (and tests) can tell
exactly what went wrong. Every error may carry a line/column for helpful messages."""


class MathDSLError(Exception):
    category = "Error"

    def __init__(self, message, line=None, col=None):
        super().__init__(message)
        self.message = message
        self.line = line
        self.col = col

    def format(self, show_line=True):
        where = ""
        if show_line and self.line:
            where = f" on line {self.line}"
            if self.col:
                where += f", column {self.col}"
        return f"{self.category}{where}: {self.message}"

    def __str__(self):
        return self.format()


# --- source-level problems -------------------------------------------------
class LexError(MathDSLError):
    """Invalid character or malformed number."""
    category = "Syntax error"


class ParseError(MathDSLError):
    """Malformed statement or expression."""
    category = "Syntax error"


# --- names -------------------------------------------------------------------
class UndefinedVariableError(MathDSLError):
    category = "Name error"


class DeclarationError(MathDSLError):
    """Bad declaration: reassigning an undeclared variable, reserved name, ..."""
    category = "Name error"


# --- evaluation --------------------------------------------------------------
# Used now: MathDomainError (numbers too large). The rest below are for features that are
# not switched on yet (they are kept here so restoring a feature needs no edits to this file):
#   DivisionByZeroError (/ %)   MathTypeError (comparisons)   FunctionError (functions)
#   EquationError family (solve)
class DivisionByZeroError(MathDSLError):
    category = "Math error"


class MathDomainError(MathDSLError):
    """Valid syntax but impossible math: sqrt(-1), negative radius, huge results."""
    category = "Math error"


class MathTypeError(MathDSLError):
    """A true/false value used where a number is needed (or stored in a variable)."""
    category = "Type error"


class FunctionError(MathDSLError):
    """Unknown function, wrong number of arguments, wrong argument type."""
    category = "Function error"


# --- equations -----------------------------------------------------------------
class EquationError(MathDSLError):
    category = "Equation error"


class NonlinearEquationError(EquationError):
    pass


class MultipleUnknownsError(EquationError):
    pass


class NoSolutionError(EquationError):
    pass


class InfiniteSolutionsError(EquationError):
    pass

