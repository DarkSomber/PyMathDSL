"""Number representation shared by the interpreter, functions and environment.

Values are Python `Fraction` (exact) or `float`. Literals and + - * / % ^ with
integer exponents stay exact; sqrt of a non-perfect square, circle formulas and
fractional exponents produce floats. True/false results are plain `bool` and are
NOT numbers.
"""
from fractions import Fraction
import math

from errors import MathDomainError

TOO_LARGE = "That number is too large to calculate."


def is_number(value):
    return isinstance(value, (Fraction, float)) and not isinstance(value, bool)


def to_float(value):
    try:
        return float(value)
    except OverflowError:
        raise MathDomainError(TOO_LARGE) from None


def to_decimal_fraction(value):
    """Exact Fraction for a number. A float is read as the decimal it displays
    (0.1 -> 1/10), not as its binary approximation (3602879701896397/36028797018963968)."""
    if isinstance(value, Fraction):
        return value
    return Fraction(repr(value))


def check_finite(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise MathDomainError(TOO_LARGE)
    return value


def format_number(value):
    """Display rules: whole numbers print without a decimal point; fractions 
    print as fractions; everything else prints as float."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if not is_number(value):
        return str(value)
    if isinstance(value, Fraction):
        if value.denominator == 1:
            try:
                return str(value.numerator)
            except ValueError:
                raise MathDomainError(TOO_LARGE) from None
        try:
            return str(value)
        except ValueError:      # numerator/denominator beyond Python's integer-to-text limit
            raise MathDomainError(TOO_LARGE) from None
    if value.is_integer() and abs(value) < 1e16:
        return str(int(value))
    return repr(value)