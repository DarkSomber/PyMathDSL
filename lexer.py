"""Lexer: source text -> tokens (with line/column). Statements end at NEWLINE.

Only + and - are supported for now. Search the project for FUTURE to find every place where
the cut features plug back in; the README lists the steps in order.
"""
from collections import namedtuple
from fractions import Fraction

from errors import LexError

# kind is one of: NUMBER IDENT KEYWORD OP NEWLINE EOF
Token = namedtuple("Token", "kind value text line col")

KEYWORDS = {"let", "print", "solve"}

ONE_CHAR_OPS = set("+-()=")
# FUTURE (* / % ^):     add "*/%^"   -> set("+-*/%^()=")
# FUTURE (functions):   add ","      (separates function arguments)
# FUTURE (comparisons): add "<>"

TWO_CHAR_OPS = set()
# FUTURE (comparisons): TWO_CHAR_OPS = {"==", "!=", "<=", ">="}

# Symbols the language will get later. For now they give a friendly "not available yet" message.
# FUTURE: delete a character from this string when you add it to ONE_CHAR_OPS above.
NOT_YET = "*/%^,<>"

DIGITS = "0123456789"


def _is_ident_start(ch):
    return ch.isascii() and (ch.isalpha() or ch == "_")


def tokenize(source):
    tokens = []
    i, n = 0, len(source)
    line, line_start = 1, 0

    def add(kind, value, text, start):
        tokens.append(Token(kind, value, text, line, start - line_start + 1))

    while i < n:
        ch = source[i]
        if ch == "\n":
            add("NEWLINE", None, "\n", i)
            line += 1
            line_start = i + 1
            i += 1
        elif ch in " \t\r":
            i += 1
        elif ch in DIGITS:
            j = i
            while j < n and source[j] in DIGITS:
                j += 1
            if j < n and source[j] == ".":
                if j + 1 >= n or source[j + 1] not in DIGITS:
                    raise LexError("A decimal point must be followed by digits, e.g. 3.5",
                                   line, j - line_start + 1)
                j += 1
                while j < n and source[j] in DIGITS:
                    j += 1
            text = source[i:j]
            try:
                add("NUMBER", Fraction(text), text, i)   # exact decimals: 0.1 + 0.2 is 0.3
            except ValueError:
                raise LexError("That number has too many digits.", line, i - line_start + 1) from None
            i = j
        elif _is_ident_start(ch):
            j = i
            while j < n and (_is_ident_start(source[j]) or source[j] in DIGITS):
                j += 1
            word = source[i:j]
            add("KEYWORD" if word in KEYWORDS else "IDENT", word, word, i)
            i = j
        elif source[i:i + 2] in TWO_CHAR_OPS:
            add("OP", source[i:i + 2], source[i:i + 2], i)
            i += 2
        elif ch in ONE_CHAR_OPS:
            add("OP", ch, ch, i)
            i += 1
        else:
            col = i - line_start + 1
            if ch in NOT_YET:
                raise LexError(f"The symbol '{ch}' isn't available yet. "
                               "Right now only + and - are supported.", line, col)
            if ch == ".":
                raise LexError("Unexpected '.'. Write decimals with a digit on both sides, e.g. 0.5", line, col)
            if ch == "!":
                raise LexError("Unexpected '!'.", line, col)
            raise LexError(f"I don't understand the character '{ch}'. "
                           "Only numbers, names, + - ( ) and = are allowed.", line, col)
    add("EOF", None, "", n)
    return tokens