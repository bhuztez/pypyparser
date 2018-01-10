"""Python token definitions."""

class Token:
    ENDMARKER        = 1
    NAME             = 2
    NUMBER           = 3
    STRING           = 4
    NEWLINE          = 5
    INDENT           = 6
    DEDENT           = 7
    LPAR             = 8
    RPAR             = 9
    LSQB             = 10
    RSQB             = 11
    COLON            = 12
    COMMA            = 13
    SEMI             = 14
    PLUS             = 15
    MINUS            = 16
    STAR             = 17
    SLASH            = 18
    VBAR             = 19
    AMPER            = 20
    LESS             = 21
    GREATER          = 22
    EQUAL            = 23
    DOT              = 24
    PERCENT          = 25
    BACKQUOTE        = 26
    LBRACE           = 27
    RBRACE           = 28
    EQEQUAL          = 29
    NOTEQUAL         = 30
    LESSEQUAL        = 31
    GREATEREQUAL     = 32
    TILDE            = 33
    CIRCUMFLEX       = 34
    LEFTSHIFT        = 35
    RIGHTSHIFT       = 36
    DOUBLESTAR       = 37
    PLUSEQUAL        = 38
    MINEQUAL         = 39
    STAREQUAL        = 40
    SLASHEQUAL       = 41
    PERCENTEQUAL     = 42
    AMPEREQUAL       = 43
    VBAREQUAL        = 44
    CIRCUMFLEXEQUAL  = 45
    LEFTSHIFTEQUAL   = 46
    RIGHTSHIFTEQUAL  = 47
    DOUBLESTAREQUAL  = 48
    DOUBLESLASH      = 49
    DOUBLESLASHEQUAL = 50
    AT               = 51
    ATEQUAL          = 52
    RARROW           = 53
    ELLIPSIS         = 54
    OP               = 55
    ASYNC            = 56
    AWAIT            = 57
    ERRORTOKEN       = 58

    # extra PyPy-specific tokens
    COMMENT          = 59
    NIL              = 60


OPMAP = {
    "(":   Token.LPAR,
    ")":   Token.RPAR,
    "[":   Token.LSQB,
    "]":   Token.RSQB,
    ":":   Token.COLON,
    ",":   Token.COMMA,
    ";":   Token.SEMI,
    "+":   Token.PLUS,
    "-":   Token.MINUS,
    "*":   Token.STAR,
    "/":   Token.SLASH,
    "|":   Token.VBAR,
    "&":   Token.AMPER,
    "<":   Token.LESS,
    ">":   Token.GREATER,
    "=":   Token.EQUAL,
    ".":   Token.DOT,
    "%":   Token.PERCENT,
    "`":   Token.BACKQUOTE,
    "{":   Token.LBRACE,
    "}":   Token.RBRACE,
    "==":  Token.EQEQUAL,
    "!=":  Token.NOTEQUAL,
    "<>":  Token.NOTEQUAL,
    "<=":  Token.LESSEQUAL,
    ">=":  Token.GREATEREQUAL,
    "~":   Token.TILDE,
    "^":   Token.CIRCUMFLEX,
    "<<":  Token.LEFTSHIFT,
    ">>":  Token.RIGHTSHIFT,
    "**":  Token.DOUBLESTAR,
    "+=":  Token.PLUSEQUAL,
    "-=":  Token.MINEQUAL,
    "*=":  Token.STAREQUAL,
    "/=":  Token.SLASHEQUAL,
    "%=":  Token.PERCENTEQUAL,
    "&=":  Token.AMPEREQUAL,
    "|=":  Token.VBAREQUAL,
    "^=":  Token.CIRCUMFLEXEQUAL,
    "<<=": Token.LEFTSHIFTEQUAL,
    ">>=": Token.RIGHTSHIFTEQUAL,
    "**=": Token.DOUBLESTAREQUAL,
    "//":  Token.DOUBLESLASH,
    "//=": Token.DOUBLESLASHEQUAL,
    "@":   Token.AT,
    "@=":  Token.ATEQUAL,
    "->":  Token.RARROW,
    "...": Token.ELLIPSIS,
}
