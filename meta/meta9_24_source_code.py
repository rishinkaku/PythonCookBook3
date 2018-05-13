import ast
import inspect

x = 42
print(type(eval('2 + 3*4 + x')))  # int
exec('for i in range(10): print(i, end=" ")')
print()
ex = ast.parse('2 + 3*4 + x', mode='eval')  # _ast.Expression
print(ast.dump(ex))

top = ast.parse('for i in range(10): print(i)', mode='exec')
print(ast.dump(top))


class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.loaded = set()
        self.stored = set()
        self.deleted = set()

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.loaded.add(node.id)
        elif isinstance(node.ctx, ast.Store):
            self.stored.add(node.id)
        elif isinstance(node.ctx, ast.Del):
            self.deleted.add(node.id)


code = '''
for i in range(10):
    print(i, end=" ")
del i
'''
top = ast.parse(code, mode='exec')
c = CodeAnalyzer()
c.visit(top)
print('Loaded:', c.loaded)
print('Stored:', c.stored)
print('Deleted:', c.deleted)
exec(compile(top, '<stdin>', 'exec'))


# Node visitor that lowers globally accessed names into
# the function body as local variables.
class NameLower(ast.NodeVisitor):

    def __init__(self, lowered_names):
        self.lowered_names = lowered_names

    def visit_FunctionDef(self, node):
        # Compile some assignments to lower the constants
        code = '__globals = globals()\n'
        code += '\n'.join("{0} = __globals['{0}']".format(name)
                          for name in self.lowered_names)
        code_ast = ast.parse(code, mode='exec')
        # Inject new statements into the function body
        node.body[:0] = code_ast.body
        # Save the function object
        self.func = node


# Decorator that turns global names into locals
def lower_names(*namelist):
    def lower(func):
        srclines = inspect.getsource(func).splitlines()
        # Skip source lines prior to the @lower_names decorator
        for n, line in enumerate(srclines):
            if '@lower_names' in line:
                break
        src = '\n'.join(srclines[n + 1:])
        # Hack to deal with indented code
        if src.startswith((' ', '\t')):
            src = 'if 1:\n' + src
        top = ast.parse(src, mode='exec')

        # Transform the AST
        cl = NameLower(namelist)
        cl.visit(top)

        # Execute the modified AST
        temp = {}
        exec(compile(top, '', 'exec'), temp, temp)

        # Pull out the modified code object
        func.__code__ = temp[func.__name__].__code__
        return func

    return lower


INCR = 1


@lower_names('INCR')
def countdown(n):
    while n > 0:
        n -= INCR


"""
equals to
def countdown(n):
    __globals = globals()
    INCR = __globals['INCR']
    while n > 0:
        n -= INCR

faster
"""
