"""Modified versions of usual AST nodes so that static type information can be stored in them."""

from .statically_typed import StaticallyTyped
from .module import StaticallyTypedModule

_ = '''
class StaticallyTypedFor(ast_module.For, StaticallyTyped):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scope_vars = {}
        self.add_type_info()

    def add_type_info(self):
        pass


class StaticallyTypedWhile(ast_module.While, StaticallyTyped):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scope_vars = {}
        self.add_type_info()

    def add_type_info(self):
        pass


class StaticallyTypedIf(ast_module.If, StaticallyTyped):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.if_true_vars = {}
        self.if_false_vars = {}
        self.add_type_info()

    def add_type_info(self):
        pass


class StaticallyTypedWith(ast_module.With, StaticallyTyped):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scope_vars = {}
        self.add_type_info()

    def add_type_info(self):
        pass
'''
