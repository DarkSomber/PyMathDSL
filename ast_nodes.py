"""AST node types. Statements carry the source line for error reporting.

Expressions are Number, Var, UnaryOp, BinOp and Call. Every binary operator, arithmetic or
comparison, is a BinOp with a different `op`.
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
    op: str                      # + - * / % ^ == ~= < > <= >=
    left: "Expr"
    right: "Expr"


@dataclass(frozen=True)
class Call:                      # built-in function call, e.g. sqrt(16)
    name: str
    args: list["Expr"]


Expr = Union[Number, Var, UnaryOp, BinOp, Call]


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