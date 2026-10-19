"""Variable storage with declaration rules and value validation."""
from errors import DeclarationError, MathTypeError, UndefinedVariableError
from numeric import check_finite, format_number, is_number


class Environment:
    def __init__(self):
        self._vars = {}

    @staticmethod
    def _validate(value):
        if not is_number(value):
            raise MathTypeError(f"Variables can only hold numbers, but this gave "
                                f"{format_number(value)}. Use print to see true/false results.")
        check_finite(value)

    def has(self, name):
        return name in self._vars

    def declare(self, name, value):
        """`let name = value` (re-declaring an existing name just replaces its value)."""
        self._validate(value)
        self._vars[name] = value

    def assign(self, name, value):
        """`name = value` (the name must already be declared)."""
        self.require_declared(name)
        self._validate(value)
        self._vars[name] = value

    def require_declared(self, name):
        if name not in self._vars:
            raise DeclarationError(f"'{name}' hasn't been declared yet. "
                                   f"Declare it first with: let {name} = ...")

    def get(self, name):
        if name not in self._vars:
            raise UndefinedVariableError(f"The variable '{name}' is not defined. "
                                         f"Declare it first with: let {name} = ...")
        return self._vars[name]