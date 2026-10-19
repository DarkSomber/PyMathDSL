"""Built-in math functions for the DSL.

Every function is registered once in FUNCTIONS (name -> handler, argument count, and the
parameter list shown in "takes exactly N arguments" errors). call_function() does the shared
checks - the name exists, every argument is a number, the argument count is right - and then
calls the handler with plain numbers. A negative radius, side or dimension is always a
MathDomainError.
"""
from collections import namedtuple
from fractions import Fraction
import math

from errors import FunctionError, MathDomainError, MathTypeError
from numeric import format_number, is_number, to_decimal_fraction, to_float

MAX_DECIMAL_PLACES = 999   # same spirit as the exponent limit in the interpreter


# ---- conversion and rounding ----
def _frac(value):
    # Fractions stay as they are; floats are read as the decimal they display (0.1 -> 1/10).
    return to_decimal_fraction(value)


def _dec(value):
    return to_float(value)


def _decimal_places(name, value):
    """The decimalPlaces argument of roundUp/roundDown: a whole number from 0 to MAX_DECIMAL_PLACES."""
    exact = to_decimal_fraction(value)
    if exact.denominator != 1:
        raise FunctionError(f"Function '{name}' needs a whole number of decimal places, "
                            f"but got {format_number(value)}.")
    places = exact.numerator
    if places < 0:
        raise FunctionError("Decimal places cannot be negative.")
    if places > MAX_DECIMAL_PLACES:
        raise FunctionError(f"Decimal places cannot be more than {MAX_DECIMAL_PLACES}.")
    return places


def _round(name, rounder, value, places):
    """Round toward +infinity (math.ceil) or -infinity (math.floor). Exact fractions are used so
    values like 0.07 or 1.1 are never nudged by binary floating-point error."""
    exact = to_decimal_fraction(value)
    factor = 10 ** _decimal_places(name, places)
    return to_float(Fraction(rounder(exact * factor), factor))


def _round_up(value, places):
    return _round("roundUp", math.ceil, value, places)


def _round_down(value, places):
    return _round("roundDown", math.floor, value, places)


# ---- roots and percentages ----
def _sqrt(value):
    val = to_float(value)
    if val < 0:
        raise MathDomainError("Cannot compute square root of a negative number.")
    return math.sqrt(val)


def _pct(value):
    """Converts a number into a percent: pct(50) is 0.5."""
    return to_float(value) / 100


def _percentage(part, total):
    """What percent `part` is of `total`."""
    part, total = to_float(part), to_float(total)
    if total == 0:
        raise MathDomainError("Cannot calculate percentage with a zero total.")
    return (part / total) * 100.0


# ---- geometry ----
def _non_negative(message, *values):
    """Convert every value to a float, then reject the call if any of them is negative."""
    numbers = [to_float(value) for value in values]
    if any(n < 0 for n in numbers):
        raise MathDomainError(message)
    return numbers


def _area_circle(radius):
    r, = _non_negative("Radius cannot be negative.", radius)
    return math.pi * (r ** 2)


def _perimeter_circle(radius):
    r, = _non_negative("Radius cannot be negative.", radius)
    return 2 * math.pi * r


def _area_triangle(base, height):
    base, height = _non_negative("Triangle dimensions cannot be negative.", base, height)
    return 0.5 * base * height


def _perimeter_triangle(side_a, side_b, side_c):
    a, b, c = _non_negative("Triangle side lengths cannot be negative.", side_a, side_b, side_c)
    return a + b + c


def _area_rectangle(width, height):
    w, h = _non_negative("Rectangle dimensions cannot be negative.", width, height)
    return w * h


def _perimeter_rectangle(width, height):
    w, h = _non_negative("Rectangle dimensions cannot be negative.", width, height)
    return 2 * (w + h)


# ---- registry ----
Builtin = namedtuple("Builtin", "handler arity params")   # params: text for the arity error, or None

FUNCTIONS = {
    "frac": Builtin(_frac, 1, None),
    "dec": Builtin(_dec, 1, None),
    "roundUp": Builtin(_round_up, 2, "value, decimalPlaces"),
    "roundDown": Builtin(_round_down, 2, "value, decimalPlaces"),
    "sqrt": Builtin(_sqrt, 1, None),
    "pct": Builtin(_pct, 1, None),
    "percentage": Builtin(_percentage, 2, "part, total"),
    "areaCircle": Builtin(_area_circle, 1, "radius"),
    "perimeterCircle": Builtin(_perimeter_circle, 1, "radius"),
    "circleCircumference": Builtin(_perimeter_circle, 1, "radius"),
    "areaTriangle": Builtin(_area_triangle, 2, "base, height"),
    "perimeterTriangle": Builtin(_perimeter_triangle, 3, "sideA, sideB, sideC"),
    "areaRectangle": Builtin(_area_rectangle, 2, "width, height"),
    "perimeterRectangle": Builtin(_perimeter_rectangle, 2, "width, height"),
}


def is_function(name):
    return name in FUNCTIONS


def call_function(name, args):
    if not is_function(name):
        raise FunctionError(f"The function '{name}' does not exist.")
    for arg in args:
        # true/false results (from comparisons) are not numbers
        if not is_number(arg):
            raise MathTypeError(f"Function '{name}' needs numbers, but got {format_number(arg)}.")
    builtin = FUNCTIONS[name]
    if len(args) != builtin.arity:
        noun = "argument" if builtin.arity == 1 else "arguments"
        params = f": ({builtin.params})" if builtin.params else ""
        raise FunctionError(f"Function '{name}' takes exactly {builtin.arity} {noun}{params}.")
    return builtin.handler(*args)