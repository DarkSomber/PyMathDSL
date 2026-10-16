"""Built-in math functions for the DSL."""
from fractions import Fraction
import math
from numeric import to_float
from errors import MathDomainError, FunctionError


def call_function(name, args):
    if name == "frac":
        if len(args) != 1:
            raise FunctionError("Function 'frac' takes exactly 1 argument.")
        val = args[0]
        if isinstance(val, Fraction):
            return val
        
        # Convert whatever value we have to a float, then get its exact fraction ratio
        f_val = to_float(val)
        numerator, denominator = f_val.as_integer_ratio()
        return Fraction(numerator, denominator)
    
    elif name == "dec":
        if len(args) != 1:
            raise FunctionError("Function 'dec' takes exactly 1 argument.")
        return to_float(args[0])

    # rounds the number up or down to the specified number of decimal places
    elif name in ("roundUp", "roundDown"):
        if len(args) != 2:
            raise FunctionError(f"Function '{name}' takes exactly 2 arguments: (value, decimalPlaces).")
        val = to_float(args[0])
        places = int(args[1])
        if places < 0:
            raise FunctionError("Decimal places cannot be negative.")
        factor = 10 ** places
        if name == "roundUp":
            return math.ceil(val * factor) / factor
        else:
            return math.floor(val * factor) / factor

    # Square root function: calculates the square root of a number
    elif name == "sqrt":
        if len(args) != 1:
            raise FunctionError("Function 'sqrt' takes exactly 1 argument.")
        val = to_float(args[0])
        if val < 0:
            raise MathDomainError("Cannot compute square root of a negative number.")
        return math.sqrt(val)

    # Percentage functions
    # converts number into percent
    elif name == "pct":
        if len(args) != 1:
            raise FunctionError("Function 'pct' takes exactly 1 argument.")
        val = to_float(args[0])
        return val / 100

    # finds the percentage value of a given number or variable (percent, given)
    elif name == "percentage":
        if len(args) != 2:
            raise FunctionError("Function 'percentage' takes exactly 2 arguments: (part, total).")
        part = to_float(args[0])
        total = to_float(args[1])
        if total == 0:
            raise MathDomainError("Cannot calculate percentage with a zero total.")
        return (part / total) * 100.0

    # Geometric Formula Functions:  Uses the most commonly used Geometric formulas

    # Formulas for a circle 
    # areaCircle(radius)
    elif name == "areaCircle":
        if len(args) != 1:
            raise FunctionError("Function 'areaCircle' takes exactly 1 argument: (radius).")
        r = to_float(args[0])
        if r < 0:
            raise MathDomainError("Radius cannot be negative.")
        return math.pi * (r ** 2)  # = pi * r^2, in sq units
    
    # perimeterCircle(radius) or circleCircumference(radius)
    elif name == "perimeterCircle" or name == "circleCircumference":
        if len(args) != 1:
            raise FunctionError(f"Function '{name}' takes exactly 1 argument: (radius).")
        r = to_float(args[0])
        if r < 0:
            raise MathDomainError("Radius cannot be negative.")
        return 2 * math.pi * r

    # triangle formulas
    # areaTriangle(base, height)
    elif name == "areaTriangle":
        if len(args) != 2:
            raise FunctionError("Function 'areaTriangle' takes exactly 2 arguments: (base, height).")
        base = to_float(args[0])
        height = to_float(args[1])
        if base < 0 or height < 0:
            raise FunctionError("Triangle dimensions cannot be negative.")
        return 0.5 * base * height
    
    # perimeterTriangle(sideA, sideB, sideC)
    elif name == "perimeterTriangle":
        if len(args) != 3:
            raise FunctionError("Function 'perimeterTriangle' takes exactly 3 arguments: (sideA, sideB, sideC).")
        a = to_float(args[0])
        b = to_float(args[1])
        c = to_float(args[2])
        if a < 0 or b < 0 or c < 0:
            raise FunctionError("Triangle side lengths cannot be negative.")
        return a + b + c

    # rectangle formulas
    # areaRectangle(width, height)
    elif name == "areaRectangle":
        if len(args) != 2:
            raise FunctionError("Function 'areaRectangle' takes exactly 2 arguments: (width, height).")
        w = to_float(args[0])
        h = to_float(args[1])
        if w < 0 or h < 0:
            raise FunctionError("Rectangle dimensions cannot be negative.")
        return w * h
    
    # perimeterRectangle(width, height)
    elif name == "perimeterRectangle":
        if len(args) != 2:
            raise FunctionError("Function 'perimeterRectangle' takes exactly 2 arguments: (width, height).")
        w = to_float(args[0])
        h = to_float(args[1])
        if w < 0 or h < 0:
            raise FunctionError("Rectangle dimensions cannot be negative.")
        return 2 * (w + h)

    raise FunctionError(f"The function '{name}' does not exist.")


def is_function(name):
    return name in (
        "frac", "dec", "roundUp", "roundDown", 
        "sqrt", "pct", "percentage", 
        "areaCircle", "circleCircumference", "perimeterCircle",
        "areaTriangle", "perimeterTriangle",
        "areaRectangle", "perimeterRectangle"
    )