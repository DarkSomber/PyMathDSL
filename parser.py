"""Recursive-descent parser. Grammar (EBNF) for the language as it is today:

    program    = { [ statement ] NEWLINE } [ statement ] ;
    statement  = "let" IDENT "=" expression
               | IDENT "=" expression
               | "print" expression
               | "solve" expression "=" expression ;     (* sides are sums; see SUM_LEVEL *)
    expression = comparison ;
    comparison = sum [ ( "==" | "~=" | "<" | ">" | "<=" | ">=" ) sum ] ;   (* not chainable *)
    sum        = product { ( "+" | "-" ) product } ;
    product    = unary { ( "*" | "/" | "%" ) unary } ;
    unary      = ( "-" | "+" ) unary | power ;
    power      = primary [ "^" unary ] ;
    primary    = NUMBER | IDENT | call | "(" expression ")" ;
    call       = IDENT "(" [ expression { "," expression } ] ")" ;
    NUMBER     = DIGIT { DIGIT } [ "." DIGIT { DIGIT } ] ;
    IDENT      = ( LETTER | "_" ) { LETTER | DIGIT | "_" } ;

"""
from ast_nodes import Assign, BinOp, Call, Let, Number, Print, Solve, UnaryOp, Var
from errors import ParseError
from lexer import tokenize

# Binary operator precedence, LOOSEST first. Each tuple is one level; operators in a level are
# left-associative. Adding a level here is all the parser needs for a new left-to-right operator.
BINARY_LEVELS = [("==", "~=", "<", ">", "<=", ">="), ("+", "-",), ("*","/","%")]
COMPARISON_LEVEL = 0                              # the loosest level; comparisons can't be chained
SUM_LEVEL = BINARY_LEVELS.index(("+", "-",))     # used by `solve`: its sides can't contain comparisons

END_OF_STATEMENT = ("NEWLINE", "EOF")


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # ---- helpers ----
    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def at_op(self, *ops):
        tok = self.peek()
        return tok.kind == "OP" and tok.value in ops

    @staticmethod
    def describe(tok):
        return "the end of the line" if tok.kind in END_OF_STATEMENT else f"'{tok.text}'"

    def error(self, message, tok=None):
        tok = tok or self.peek()
        return ParseError(message, tok.line, tok.col)

    def expect_op(self, op, hint=""):
        if not self.at_op(op):
            raise self.error(f"Expected '{op}' but found {self.describe(self.peek())}.{hint}")
        return self.advance()

    # ---- program / statements ----
    def parse_program(self):
        statements = []
        while True:
            while self.peek().kind == "NEWLINE":
                self.advance()
            if self.peek().kind == "EOF":
                return statements
            statements.append(self.statement())

    def statement(self):
        tok = self.peek()
        if tok.kind == "KEYWORD" and tok.value == "let":
            self.advance()
            name = self.advance()
            if name.kind == "KEYWORD":
                raise self.error(f"'{name.text}' is a keyword and can't be a variable name.", name)
            if name.kind != "IDENT":
                raise self.error("After 'let' I expected a variable name, e.g. let x = 5", name)
            self.expect_op("=", " Declare variables like this: let x = 5")
            stmt = Let(name.value, self.expression(), tok.line)
        elif tok.kind == "KEYWORD" and tok.value == "print":
            self.advance()
            stmt = Print(self.expression(), tok.line)
        elif tok.kind == "KEYWORD" and tok.value == "solve":
            self.advance()
            left = self.binary(SUM_LEVEL)
            self.expect_op("=", " An equation looks like: solve x + 4 = 14")
            stmt = Solve(left, self.binary(SUM_LEVEL), tok.line)
        
        elif tok.kind == "IDENT":
            # Check if this identifier is actually a function call on its own line
            next_tok = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if next_tok and next_tok.kind == "OP" and next_tok.value == "(":
                raise self.error(
                    f"Did you forget 'print'? To use '{tok.text}(...)', "
                    f"write 'print {tok.text}(...)' or assign it to a variable with 'let'.", tok
                )
            self.advance()
            if not self.at_op("="):
                raise self.error(f"'{tok.text}' must be followed by '=' to assign a value, "
                                 f"but I found {self.describe(self.peek())}.")
            self.advance()
            stmt = Assign(tok.value, self.expression(), tok.line)
        else:
            raise self.error("A statement must start with 'let', 'print', or a "
                             "variable name (to reassign it).")
        self.end_of_statement()
        return stmt

    def end_of_statement(self):
        tok = self.peek()
        if tok.kind in END_OF_STATEMENT:
            return
        hint = ""
        if tok.kind == "KEYWORD":
            hint = " Put each statement on its own line."
        elif tok.kind in ("IDENT", "NUMBER") or self.at_op("("):
            hint = " Did you forget an operator? Multiplication must be written with * "
        elif self.at_op(")"):
            hint = " There is a ')' with no matching '('."
        raise self.error(f"Unexpected {self.describe(tok)}.{hint}")

    # ---- expressions ----
    def expression(self):
        return self.binary(0)

    def binary(self, level):
        """One precedence level of left-associative binary operators (see BINARY_LEVELS)."""
        if level == len(BINARY_LEVELS):
            return self.unary()
        node = self.binary(level + 1)
        while self.at_op(*BINARY_LEVELS[level]):
            op = self.advance().value
            node = BinOp(op, node, self.binary(level + 1))
            if level == COMPARISON_LEVEL and self.at_op(*BINARY_LEVELS[level]):
                raise self.error("Comparisons can't be chained, so something like 1 < 2 < 3 isn't "
                                 "allowed. Compare two values at a time.")
        return node

    def unary(self):
        if self.at_op("-", "+"):
            op = self.advance().value
            return UnaryOp(op, self.unary())
        return self.power()

    def power(self):
        # Power sits below unary, so -2^2 means -(2^2); it is right-associative: 2^3^2 = 2^(3^2).
        base = self.primary()
        if self.at_op("^"):
            self.advance()
            return BinOp("^", base, self.unary())
        return base

    def primary(self):
        tok = self.advance()
        if tok.kind == "NUMBER":
            return Number(tok.value)
        if tok.kind == "IDENT":
            if self.at_op("("):
                return self.call(tok)
            return Var(tok.value)
        if tok.kind == "OP" and tok.value == "(":
            node = self.expression()
            self.expect_op(")", " Every '(' needs a matching ')'.")
            return node
        raise self.error(f"I expected a number, a variable, or '(' but found "
                         f"{self.describe(tok)}.", tok)

    def call(self, name_tok):
        self.advance()                                # the "("
        args = []
        if not self.at_op(")"):
            args.append(self.expression())
            while self.at_op(","):
                self.advance()
                args.append(self.expression())
        self.expect_op(")", " Close the function call with ')' and separate arguments with commas.")
        return Call(name_tok.value, args)


def parse(source):
    """Source text -> list of statements. Raises LexError / ParseError."""
    try:
        return Parser(tokenize(source)).parse_program()
    except RecursionError:
        raise ParseError("This expression is nested too deeply.") from None