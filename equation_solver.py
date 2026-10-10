"""Symbolic solver for linear equations with exactly one unknown (used by `solve`).


Every side is reduced to the form  a*x + b  (a, b exact Fractions). Names that
already have a value are treated as constants; any undefined name is an unknown.

Only + and - exist right now, so the `*`, `/`, `^` ... branches inside linear() are not reachable
yet; they are kept so the solver keeps working unchanged when those operators come back.
"""
from fractions import Fraction

from ast_nodes import BinOp, Number, UnaryOp, Var
from errors import (DivisionByZeroError, EquationError, InfiniteSolutionsError,
                    MultipleUnknownsError, NoSolutionError, NonlinearEquationError)


def _names(node):
    if isinstance(node, Var):
        return [node.name]
    if isinstance(node, UnaryOp):
        return _names(node.operand)
    if isinstance(node, BinOp):
        return _names(node.left) + _names(node.right)
    # FUTURE (functions): once the Call node exists, add `Call` to the import above and:
    # if isinstance(node, Call):
    #     return [n for arg in node.args for n in _names(arg)]
    return []


def solve_linear(left, right, evaluate, is_known):
    """Return (unknown_name, solution as Fraction).

    evaluate(node)  -> numeric value of a node that has no unknowns
    is_known(name)  -> True when a variable already has a value
    """
    names = _names(left) + _names(right)
    unknowns = sorted({n for n in names if not is_known(n)})
    if len(unknowns) > 1:
        raise MultipleUnknownsError(
            f"This equation has more than one unknown ({', '.join(unknowns)}). "
            "Only one unknown variable is supported; give the others values with 'let'.")
    if not unknowns:
        known = sorted(set(names))
        hint = ""
        if known:
            who = f"{known[0]} already has a value" if len(known) == 1 else \
                f"{', '.join(known)} already have values"
            hint = (f" {who}, so nothing is left to solve for. To solve for a variable, "
                    "don't declare it with 'let' first.")
        raise EquationError("This equation has no unknown variable." + hint)
    name = unknowns[0]

    def has_unknown(node):
        return name in _names(node)

    def constant(node):
        value = evaluate(node)
        return Fraction(value)           # exact; floats convert exactly

    def linear(node):
        """Return (a, b) such that node == a*name + b."""
        if not has_unknown(node):
            return Fraction(0), constant(node)
        if isinstance(node, Var):
            return Fraction(1), Fraction(0)
        if isinstance(node, UnaryOp):
            a, b = linear(node.operand)
            return (-a, -b) if node.op == "-" else (a, b)
        if isinstance(node, BinOp):
            if node.op in "+-":
                a1, b1 = linear(node.left)
                a2, b2 = linear(node.right)
                return (a1 + a2, b1 + b2) if node.op == "+" else (a1 - a2, b1 - b2)
            if node.op == "*":
                a1, b1 = linear(node.left)
                a2, b2 = linear(node.right)
                if a1 != 0 and a2 != 0:
                    raise NonlinearEquationError(
                        f"This equation multiplies {name} by itself, so it isn't linear. "
                        "Only linear equations are supported.")
                return a1 * b2 + a2 * b1, b1 * b2
            if node.op == "/":
                if has_unknown(node.right):
                    raise NonlinearEquationError(
                        f"This equation divides by something containing {name}, so it isn't "
                        "linear. You can only divide by a constant.")
                divisor = constant(node.right)
                if divisor == 0:
                    raise DivisionByZeroError("You can't divide by zero.")
                a, b = linear(node.left)
                return a / divisor, b / divisor
        raise NonlinearEquationError(
            f"This equation uses {name} in a way that isn't linear (powers, remainders and "
            "functions of the unknown are not supported).")

    a1, b1 = linear(left)
    a2, b2 = linear(right)
    a, b = a1 - a2, b2 - b1                  # a*x = b
    if a == 0:
        if b == 0:
            raise InfiniteSolutionsError(
                f"Every value of {name} satisfies this equation (infinitely many solutions).")
        raise NoSolutionError(f"No value of {name} satisfies this equation (no solution).")
    return name, b / a
