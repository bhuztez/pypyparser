"""Python token definitions."""

from enum import Enum, auto

class Token(Enum):
    ENDMARKER = auto()
    NAME = auto()
    NUMBER = auto()
    STRING = auto()
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    LPAR = auto()
    RPAR = auto()
    LSQB = auto()
    RSQB = auto()
    COLON = auto()
    COMMA = auto()
    SEMI = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    VBAR = auto()
    AMPER = auto()
    LESS = auto()
    GREATER = auto()
    EQUAL = auto()
    DOT = auto()
    PERCENT = auto()
    BACKQUOTE = auto()
    LBRACE = auto()
    RBRACE = auto()
    EQEQUAL = auto()
    NOTEQUAL = auto()
    LESSEQUAL = auto()
    GREATEREQUAL = auto()
    TILDE = auto()
    CIRCUMFLEX = auto()
    LEFTSHIFT = auto()
    RIGHTSHIFT = auto()
    DOUBLESTAR = auto()
    PLUSEQUAL = auto()
    MINEQUAL = auto()
    STAREQUAL = auto()
    SLASHEQUAL = auto()
    PERCENTEQUAL = auto()
    AMPEREQUAL = auto()
    VBAREQUAL = auto()
    CIRCUMFLEXEQUAL = auto()
    LEFTSHIFTEQUAL = auto()
    RIGHTSHIFTEQUAL = auto()
    DOUBLESTAREQUAL = auto()
    DOUBLESLASH = auto()
    DOUBLESLASHEQUAL = auto()
    AT = auto()
    ATEQUAL = auto()
    RARROW = auto()
    ELLIPSIS = auto()
    OP = auto()
    ASYNC = auto()
    AWAIT = auto()
    ERRORTOKEN = auto()

    # extra PyPy-specific tokens
    COMMENT = auto()
    NIL = auto()


OPMAP = {
    "(":   Token.LPAR.value,
    ")":   Token.RPAR.value,
    "[":   Token.LSQB.value,
    "]":   Token.RSQB.value,
    ":":   Token.COLON.value,
    ",":   Token.COMMA.value,
    ";":   Token.SEMI.value,
    "+":   Token.PLUS.value,
    "-":   Token.MINUS.value,
    "*":   Token.STAR.value,
    "/":   Token.SLASH.value,
    "|":   Token.VBAR.value,
    "&":   Token.AMPER.value,
    "<":   Token.LESS.value,
    ">":   Token.GREATER.value,
    "=":   Token.EQUAL.value,
    ".":   Token.DOT.value,
    "%":   Token.PERCENT.value,
    "`":   Token.BACKQUOTE.value,
    "{":   Token.LBRACE.value,
    "}":   Token.RBRACE.value,
    "==":  Token.EQEQUAL.value,
    "!=":  Token.NOTEQUAL.value,
    "<>":  Token.NOTEQUAL.value,
    "<=":  Token.LESSEQUAL.value,
    ">=":  Token.GREATEREQUAL.value,
    "~":   Token.TILDE.value,
    "^":   Token.CIRCUMFLEX.value,
    "<<":  Token.LEFTSHIFT.value,
    ">>":  Token.RIGHTSHIFT.value,
    "**":  Token.DOUBLESTAR.value,
    "+=":  Token.PLUSEQUAL.value,
    "-=":  Token.MINEQUAL.value,
    "*=":  Token.STAREQUAL.value,
    "/=":  Token.SLASHEQUAL.value,
    "%=":  Token.PERCENTEQUAL.value,
    "&=":  Token.AMPEREQUAL.value,
    "|=":  Token.VBAREQUAL.value,
    "^=":  Token.CIRCUMFLEXEQUAL.value,
    "<<=": Token.LEFTSHIFTEQUAL.value,
    ">>=": Token.RIGHTSHIFTEQUAL.value,
    "**=": Token.DOUBLESTAREQUAL.value,
    "//":  Token.DOUBLESLASH.value,
    "//=": Token.DOUBLESLASHEQUAL.value,
    "@":   Token.AT.value,
    "@=":  Token.ATEQUAL.value,
    "->":  Token.RARROW.value,
    "...": Token.ELLIPSIS.value,
}
