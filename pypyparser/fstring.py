from string import Formatter
from . import ast, consts, parsestring


def add_constant_string(joined_pieces, w_string, atom_node):
    is_unicode = isinstance(w_string, str)
    # Implement implicit string concatenation.
    if joined_pieces:
        prev = joined_pieces[-1]
        if is_unicode and isinstance(prev, ast.Str):
            w_string = prev.s + w_string
            del joined_pieces[-1]
        elif not is_unicode and isinstance(prev, ast.Bytes):
            w_string = prev.s + w_string
            del joined_pieces[-1]
    node = ast.Str if is_unicode else ast.Bytes
    joined_pieces.append(node(w_string, atom_node.get_lineno(),
                                        atom_node.get_column()))


def string_parse_literal(astbuilder, atom_node):
    joined_pieces = []
    fmode = False

    try:
        for i in range(atom_node.num_children()):
            w_next = parsestring.parsestr(atom_node.get_child(i).get_value())
            if not isinstance(w_next, parsestring.FString):
                add_constant_string(joined_pieces, w_next, atom_node)
            else:
                astbuilder.error("f-strings not supported yet",
                                 atom_node)
                fmode = True
    except UnicodeError as e:
        raise astbuilder.error('(%s) %s' % ("unicode error", str(e)), atom_node)
    except ValueError as e:
        raise astbuilder.error('(%s) %s' % ("value error", str(e)), atom_node)

    if not fmode and len(joined_pieces) == 1:   # <= the common path
        return joined_pieces[0]   # ast.Str, Bytes or FormattedValue

    # with more than one piece, it is a combination of Str and
    # FormattedValue pieces---if there is a Bytes, then we got
    # an invalid mixture of bytes and unicode literals
    for node in joined_pieces:
        if isinstance(node, ast.Bytes):
            astbuilder.error("cannot mix bytes and nonbytes literals",
                             atom_node)
    assert fmode
    assert False
