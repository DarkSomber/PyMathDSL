"""AST node types. Statements carry the source line for error reporting.

Only the nodes needed for + and - (plus let / print / solve) exist right now.

FUTURE (functions): add this node, then use it in parser.py and interpreter.py
    @dataclass(frozen=True)
    class Call:
        name: str
        args: List["Expr"]
    ...and add Call to the Expr union below.

(* / % ^ and comparisons need no new node: they are BinOp nodes with a different `op`.)
"""
from dataclasses import dataclass
from fractions import Fraction
from typing import Union


# ---- expressions ----
@dataclass(frozen=True)
class Number:
    value: Fraction


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class UnaryOp:
    op: str                      # "-" or "+"
    operand: "Expr"


@dataclass(frozen=True)
class BinOp:
    op: str                      # "+" or "-" for now
    left: "Expr"
    right: "Expr"


Expr = Union[Number, Var, UnaryOp, BinOp]


# ---- statements ----
@dataclass(frozen=True)
class Let:
    name: str
    expr: Expr
    line: int = 0


@dataclass(frozen=True)
class Assign:
    name: str
    expr: Expr
    line: int = 0


@dataclass(frozen=True)
class Print:
    expr: Expr
    line: int = 0


@dataclass(frozen=True)
class Solve:
    left: Expr                   # solve <left> = <right>
    right: Expr
    line: int = 0