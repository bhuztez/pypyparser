import io

class FString:
    def __init__(self, unparsed):
        self.unparsed = unparsed


def parsestr(s):
    """Parses a string or unicode literal, and return usually
    a wrapped value.  If we get an f-string, then instead return
    an unparsed but unquoted W_FString instance.

    Yes, it's very inefficient.
    Yes, CPython has very similar code.
    """
    # we use ps as "pointer to s"
    # q is the virtual last char index of the string
    ps = 0
    quote = s[ps]
    rawmode = False
    unicode_literal = True
    saw_u = False
    saw_f = False

    # string decoration handling
    if quote == 'b' or quote == 'B':
        ps += 1
        quote = s[ps]
        unicode_literal = False
    elif quote == 'u' or quote == 'U':
        ps += 1
        quote = s[ps]
        saw_u = True
    elif quote == 'r' or quote == 'R':
        ps += 1
        quote = s[ps]
        rawmode = True
    elif quote == 'f' or quote == 'F':
        ps += 1
        quote = s[ps]
        saw_f = True

    if not saw_u:
        if quote == 'r' or quote == 'R':
            ps += 1
            quote = s[ps]
            rawmode = True
        elif quote == 'b' or quote == 'B':
            ps += 1
            quote = s[ps]
            unicode_literal = False
        elif quote == 'f' or quote == 'F':
            ps += 1
            quote = s[ps]
            saw_f = True
    elif quote != "'" and quote != '"':
        raise ValueError("invalid syntax")

    assert quote == "'" or quote == '"', 'parser passed unquoted literal'

    ps += 1
    q = len(s) - 1
    assert s[q] == quote, 'parser passed unmatched quotes in literal'

    if q-ps >= 4 and s[ps] == quote and s[ps+1] == quote:
        # triple quotes
        ps += 2
        assert s[q-1] == quote or s[q-2] == quote, 'parser passed unmatched triple quotes in literal'
        q -= 2

    assert 0 <= ps <= q
    substr = s[ps : q]

    if not unicode_literal:
        for c in substr:
            if ord(c) >= 0x80:
                raise SyntaxError("bytes can only contain ASCII literal characters.")
        substr = substr.encode()

    if not rawmode:
        if unicode_literal:
            substr = decode_unicode_escape(substr)
        else:
            substr = decode_bytes_escape(substr)

    if saw_f:
        return FString(substr)
    else:
        return substr


UNICODE_ESCAPE = {
    '\n': '',  # newline
    '\\': '\\',
    '\'': '\'',
    '\"': '\"',
    'a': '\a',
    'b': '\b',
    'f': '\f',
    'n': '\n',
    'r': '\r',
    't': '\t',
    'v': '\v',
}

OCTAL_CHARS = '01234567'
HEX_CHARS = '0123456789ABCDEFabcdef'

def decode_unicode_escape(s):
    buf = io.StringIO()

    while True:
        r = s.split('\\', 1)
        buf.write(r[0])
        if len(r) == 1:
            break

        s = r[1]
        if not s:
            raise ValueError(r"Trailing \ in string")

        c = UNICODE_ESCAPE.get(s[0], None)
        if c is not None:
            buf.write(c)
            s = s[1:]
        elif s[0] == 'x': # x
            if len(s) < 3 or s[1] not in HEX_CHARS or s[2] not in HEX_CHARS:
                raise ValueError(r"invalid \x escape")
            buf.write(chr(int(s[1:3], 16)))
            s = s[3:]
        elif s[0] in OCTAL_CHARS:
            if len(s) > 1 and s[1] in OCTAL_CHARS:
                if len(s) > 2 and s[2] in OCTAL_CHARS:
                    buf.write(chr(int(s[:3], 8) & 0xFF))
                    s = s[3:]
                else:
                    buf.write(chr(int(s[:2], 8)))
                    s = s[2:]
            else:
                buf.write(chr(int(s[:1], 8)))
                s = s[1:]
        elif s[0] == 'u':
            if len(s) < 5 or any(c not in HEX_CHARS for c in s[1:5]):
                raise ValueError(r"invalid \u escape")
            buf.write(chr(int(s[1:5], 16)))
            s = s[5:]

        elif s[0] == 'U':
            if len(s) < 9 or any(c not in HEX_CHARS for c in s[1:9]):
                raise ValueError(r"invalid \U escape")
            u = int(s[1:9], 16)
            if u > 0x10FFFF:
                raise UnicodeError("illegal Unicode character")
            buf.write(chr(u))
            s = s[9:]
        else:
            buf.write('\\')

    return buf.getvalue()


BYTES_ESCAPE = {
    0xa: b'',  # newline
    0x5c: b'\\',
    0x27: b'\'',
    0x22: b'\"',
    0x61: b'\a',
    0x62: b'\b',
    0x66: b'\f',
    0x6e: b'\n',
    0x72: b'\r',
    0x74: b'\t',
    0x76: b'\v',
}

OCTAL_BYTES = frozenset(b'01234567')
HEX_BYTES = frozenset(b'0123456789ABCDEFabcdef')

def decode_bytes_escape(s):
    buf = io.BytesIO()

    while True:
        r = s.split(b'\\', 1)
        buf.write(r[0])
        if len(r) == 1:
            break

        s = r[1]
        if not s:
            raise ValueError(r"Trailing \ in string")

        c = BYTES_ESCAPE.get(s[0], None)
        if c is not None:
            buf.write(c)
            s = s[1:]
        elif s[0] == 0x78: # x
            if len(s) < 3 or s[1] not in HEX_BYTES or s[2] not in HEX_BYTES:
                raise ValueError(r"invalid \x escape")
            buf.write(bytes([int(s[1:3], 16)]))
            s = s[3:]
        elif s[0] in OCTAL_BYTES:
            if len(s) > 1 and s[1] in OCTAL_BYTES:
                if len(s) > 2 and s[2] in OCTAL_BYTES:
                    buf.write(bytes([int(s[:3], 8) & 0xFF]))
                    s = s[3:]
                else:
                    buf.write(bytes([int(s[:2], 8)]))
                    s = s[2:]
            else:
                buf.write(bytes([int(s[:1], 8)]))
                s = s[1:]
        else:
            buf.write(b'\\')

    return buf.getvalue()
