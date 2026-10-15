"""Built-in math functions for the DSL."""
from fractions import Fraction
import math
from numeric import to_float


def call_function(name, args):
    if name == "frac":
        if len(args) != 1:
            raise ValueError("Function 'frac' takes exactly 1 argument.")
        val = args[0]
        if isinstance(val, Fraction):
            return val
        
        # Convert whatever value we have to a float, then get its exact fraction ratio
        f_val = to_float(val)
        numerator, denominator = f_val.as_integer_ratio()
        return Fraction(numerator, denominator)
    
    elif name == "dec":
        if len(args) != 1:
            raise ValueError("Function 'dec' takes exactly 1 argument.")
        return to_float(args[0])

    elif name in ("round_up", "round_down"):
        if len(args) != 2:
            raise ValueError(f"Function '{name}' takes exactly 2 arguments: (value, decimal_places).")
        val = to_float(args[0])
        places = int(args[1])
        if places < 0:
            raise ValueError("Decimal places cannot be negative.")
        factor = 10 ** places
        if name == "round_up":
            return math.ceil(val * factor) / factor
        else:
            return math.floor(val * factor) / factor

    raise NameError(f"Unknown function '{name}'")


def is_function(name):
    return name in ("frac", "dec", "round_up", "round_down")