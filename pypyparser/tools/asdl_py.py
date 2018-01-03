"""
Generate AST node definitions from an ASDL description.
"""

import sys
import os
import asdl


class ASDLVisitor(asdl.VisitorBase):

    def __init__(self, stream, data):
        super(ASDLVisitor, self).__init__()
        self.stream = stream
        self.data = data

    def visitModule(self, mod, *args):
        for df in mod.dfns:
            self.visit(df, *args)

    def visitSum(self, sum, *args):
        for tp in sum.types:
            self.visit(tp, *args)

    def visitType(self, tp, *args):
        self.visit(tp.value, *args)

    def visitProduct(self, prod, *args):
        for field in prod.fields:
            self.visit(field, *args)

    def visitConstructor(self, cons, *args):
        for field in cons.fields:
            self.visit(field, *args)

    def visitField(self, field, *args):
        pass

    def emit(self, line, level=0):
        indent = "    "*level
        self.stream.write(indent + line + "\n")


def is_simple_sum(sum):
    assert isinstance(sum, asdl.Sum)
    for constructor in sum.types:
        if constructor.fields:
            return False
    return True


class ASTNodeVisitor(ASDLVisitor):

    def visitType(self, tp):
        self.visit(tp.value, tp.name)

    def visitSum(self, sum, base):
        self.emit("class %s(AST):" % (base,))
        self.make_constructor(sum.attributes, sum)
        self.emit("")

        for cons in sum.types:
            self.visit(cons, base, sum.attributes)
            self.emit("")

    def visitProduct(self, product, name):
        self.emit("class %s(AST):" % (name,))
        self.make_fields(product.fields)
        self.emit("")
        self.make_constructor(product.fields + product.attributes, product)
        self.emit("")
        self.emit("")

    def visitConstructor(self, cons, base, extra_attributes):
        self.emit("class %s(%s):" % (cons.name, base))
        if cons.fields:
            self.make_fields(cons.fields)
            self.emit("")
        self.make_constructor(cons.fields, cons, extra_attributes, base)
        self.emit("")

    def visitField(self, field):
        self.emit("self.%s = %s" % (field.name, field.name), 2)

    def make_fields(self, fields):
        self.emit("_fields = %s" % (tuple(f.name for f in fields),), 1)

    def make_constructor(self, fields, node, extras=None, base=None):
        if fields or extras:
            arg_fields = fields + extras if extras else fields
            args = ", ".join(str(field.name) for field in arg_fields)
            self.emit("def __init__(self, %s):" % args, 1)
            for field in fields:
                self.visit(field)
            if extras:
                base_args = ", ".join(str(field.name) for field in extras)
                self.emit("%s.__init__(self, %s)" % (base, base_args), 2)
        else:
            self.emit("pass", 1)


class ASDLData(object):

    def __init__(self, tree):
        simple_types = set()
        prod_simple = set()
        field_masks = {}
        required_masks = {}
        optional_masks = {}
        cons_attributes = {}
        def add_masks(fields, node):
            required_mask = 0
            optional_mask = 0
            for i, field in enumerate(fields):
                flag = 1 << i
                if field not in field_masks:
                    field_masks[field] = flag
                else:
                    assert field_masks[field] == flag
                if field.opt:
                    optional_mask |= flag
                else:
                    required_mask |= flag
            required_masks[node] = required_mask
            optional_masks[node] = optional_mask
        for tp in tree.dfns:
            if isinstance(tp.value, asdl.Sum):
                sum = tp.value
                if is_simple_sum(sum):
                    simple_types.add(tp.name)
                else:
                    attrs = [field for field in sum.attributes]
                    for cons in sum.types:
                        add_masks(attrs + cons.fields, cons)
                        cons_attributes[cons] = attrs
            else:
                prod = tp.value
                prod_simple.add(tp.name)
                add_masks(prod.fields, prod)
        prod_simple.update(simple_types)
        self.cons_attributes = cons_attributes
        self.simple_types = simple_types
        self.prod_simple = prod_simple
        self.field_masks = field_masks
        self.required_masks = required_masks
        self.optional_masks = optional_masks


HEAD = r"""
class AST:
    _fields = ()

"""

visitors = [ASTNodeVisitor]


def main(argv):
    if len(argv) == 3:
        def_file, out_file = argv[1:]
    elif len(argv) == 1:
        print("Assuming default values of Python.asdl and ast.py")
        here = os.path.dirname(__file__)
        def_file = os.path.join(here, "Python.asdl")
        out_file = os.path.join(here, "..", "ast.py")
    else:
        print >> sys.stderr, "invalid arguments"
        return 2
    mod = asdl.parse(def_file)
    data = ASDLData(mod)
    fp = open(out_file, "w")
    try:
        fp.write(HEAD)
        for visitor in visitors:
            visitor(fp, data).visit(mod)
    finally:
        fp.close()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
