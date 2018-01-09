from .pytoken import Token
from . import future, parser, pytokenizer, pygram, error, consts


def _normalize_encoding(encoding):
    """returns normalized name for <encoding>

    see dist/src/Parser/tokenizer.c 'get_normal_name()'
    for implementation details / reference

    NOTE: for now, parser.suite() raises a MemoryError when
          a bad encoding is used. (SF bug #979739)
    """
    if encoding is None:
        return None
    # lower() + '_' / '-' conversion
    encoding = encoding.replace('_', '-').lower()
    if encoding == 'utf-8' or encoding.startswith('utf-8-'):
        return 'utf-8'
    for variant in ['latin-1', 'iso-latin-1', 'iso-8859-1']:
        if (encoding == variant or
            encoding.startswith(variant + '-')):
            return 'iso-8859-1'
    return encoding

def _check_for_encoding(s):
    eol = s.find(b'\n')
    if eol < 0:
        return _check_line_for_encoding(s)[0]
    enc, again = _check_line_for_encoding(s[:eol])
    if enc or not again:
        return enc
    eol2 = s.find(b'\n', eol + 1)
    if eol2 < 0:
        return _check_line_for_encoding(s[eol + 1:])[0]
    return _check_line_for_encoding(s[eol + 1:eol2])[0]


def _check_line_for_encoding(line):
    """returns the declared encoding or None"""
    i = 0
    for i in range(len(line)):
        if line[i] == 0x23: # '#'
            break
        if line[i] not in (0x20,0x9,0xc): # ' \t\014':
            return None, False  # Not a comment, don't read the second line.
    return pytokenizer.match_encoding_declaration(line[i:]), True


class CompileInfo:
    """Stores information about the source being compiled.

    * filename: The filename of the source.
    * mode: The parse mode to use. ('exec', 'eval', or 'single')
    * flags: Parser and compiler flags.
    * encoding: The source encoding.
    * last_future_import: The line number and offset of the last __future__
      import.
    * hidden_applevel: Will this code unit and sub units be hidden at the
      applevel?
    * optimize: optimization level:
        -1 = same as interpreter,
         0 = no optmiziation,
         1 = remove asserts,
         2 = remove docstrings.
    """

    def __init__(self, filename, mode="exec", flags=0, future_pos=(0, 0),
                 hidden_applevel=False, optimize=-1):
        self.filename = filename
        self.mode = mode
        self.encoding = None
        self.flags = flags
        self.optimize = optimize
        self.last_future_import = future_pos
        self.hidden_applevel = hidden_applevel


_targets = {
'eval' : pygram.syms.eval_input,
'single' : pygram.syms.single_input,
'exec' : pygram.syms.file_input,
}

class PythonParser(parser.Parser):

    def __init__(self, future_flags=future.futureFlags_3_5,
                 grammar=pygram.python_grammar):
        parser.Parser.__init__(self, grammar)
        self.future_flags = future_flags

    def parse_source(self, bytessrc, compile_info):
        """Main entry point for parsing Python source.

        Everything from decoding the source to tokenizing to building the parse
        tree is handled here.
        """
        # Detect source encoding.
        explicit_encoding = False
        enc = None
        if compile_info.flags & consts.PyCF_SOURCE_IS_UTF8:
            enc = 'utf-8'

        if isinstance(bytessrc, bytes) and not (compile_info.flags & consts.PyCF_IGNORE_COOKIE):
            if bytessrc.startswith(b"\xEF\xBB\xBF"):
                bytessrc = bytessrc[3:]
                enc = 'utf-8'
                # If an encoding is explicitly given check that it is utf-8.
                decl_enc = _check_for_encoding(bytessrc)
                explicit_encoding = (decl_enc is not None)
                if decl_enc and decl_enc != "utf-8":
                    raise error.SyntaxError("UTF-8 BOM with %s coding cookie" % decl_enc,
                                            filename=compile_info.filename)
            else:
                enc = _normalize_encoding(_check_for_encoding(bytessrc))
                explicit_encoding = (enc is not None)
                if enc is None:
                    enc = 'utf-8'

        if not isinstance(bytessrc, str):
            try:
                textsrc = bytessrc.decode(enc) if enc is not None else bytessrc.decode()
            except LookupError:
                raise error.SyntaxError("Unknown encoding: %s" % enc,
                                        filename=compile_info.filename)
            except UnicodeDecodeError as e:
                raise error.SyntaxError(str(e))
        else:
            textsrc = bytessrc


        flags = compile_info.flags
        if explicit_encoding:
            flags |= consts.PyCF_FOUND_ENCODING

        # The tokenizer is very picky about how it wants its input.
        source_lines = textsrc.splitlines(True)
        if source_lines and not source_lines[-1].endswith("\n"):
            source_lines[-1] += '\n'
        if textsrc and textsrc[-1] == "\n":
            flags &= ~consts.PyCF_DONT_IMPLY_DEDENT

        self.prepare(_targets[compile_info.mode])
        tp = 0
        try:
            last_value_seen = None
            next_value_seen = None
            try:
                # Note: we no longer pass the CO_FUTURE_* to the tokenizer,
                # which is expected to work independently of them.  It's
                # certainly the case for all futures in Python <= 2.7.
                tokens = pytokenizer.generate_tokens(source_lines, flags)

                newflags, last_future_import = (
                    future.add_future_flags(self.future_flags, tokens))
                compile_info.last_future_import = last_future_import
                compile_info.flags |= newflags
                self.grammar = pygram.python_grammar
                tokens_stream = iter(tokens)

                for tp, value, lineno, column, line in tokens_stream:
                    next_value_seen = value
                    if self.add_token(tp, value, lineno, column, line):
                        break
                    last_value_seen = value
                last_value_seen = None
                next_value_seen = None

                if compile_info.mode == 'single':
                    for tp, value, lineno, column, line in tokens_stream:
                        if tp == Token.ENDMARKER.value:
                            break
                        if tp == Token.NEWLINE.value:
                            continue

                        if tp == Token.COMMENT.value:
                            for tp, _, _, _, _ in tokens_stream:
                                if tp == Token.NEWLINE.value:
                                    break
                        else:
                            new_err = error.SyntaxError
                            msg = ("multiple statements found while "
                                   "compiling a single statement")
                            raise new_err(msg, lineno, column,
                                          line, compile_info.filename)

            except error.TokenError as e:
                e.filename = compile_info.filename
                raise
            except error.TokenIndentationError as e:
                e.filename = compile_info.filename
                raise
            except parser.ParseError as e:
                # Catch parse errors, pretty them up and reraise them as a
                # SyntaxError.
                new_err = error.IndentationError
                if tp == Token.INDENT.value:
                    msg = "unexpected indent"
                elif e.expected == Token.INDENT.value:
                    msg = "expected an indented block"
                else:
                    new_err = error.SyntaxError
                    if (last_value_seen in ('print', 'exec') and
                            bool(next_value_seen) and
                            next_value_seen != '('):
                        msg = "Missing parentheses in call to '%s'" % (
                            last_value_seen,)
                    else:
                        msg = "invalid syntax"
                raise new_err(msg, e.lineno, e.column, e.line,
                              compile_info.filename)
            else:
                tree = self.root
        finally:
            # Avoid hanging onto the tree.
            self.root = None
        if enc is not None:
            compile_info.encoding = enc
        return tree
