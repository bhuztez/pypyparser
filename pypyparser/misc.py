class ForbiddenNameAssignment(Exception):

    def __init__(self, name, node):
        self.name = name
        self.node = node


def check_forbidden_name(name, node=None):
    """Raise an error if the name cannot be assigned to."""
    if name in ("None", "__debug__"):
        raise ForbiddenNameAssignment(name, node)



def new_identifier(name):
    # Check whether there are non-ASCII characters in the identifier; if
    # so, normalize to NFKC
    for c in name:
        if ord(c) > 0x80:
            break
    else:
        return name

    import unicodedata
    return unicodedata.normalize('NFKC', name)
