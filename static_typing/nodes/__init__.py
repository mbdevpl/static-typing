"""Modified versions of usual AST nodes so that static type information can be stored in them."""

from .statically_typed import StaticallyTyped
from .module import StaticallyTypedModule
from .function_def import StaticallyTypedFunctionDef
from .class_def import StaticallyTypedClassDef
from .declaration import StaticallyTypedAssign, StaticallyTypedAnnAssign
from .context import StaticallyTypedFor, StaticallyTypedWith
# , StaticallyTypedWhile, StaticallyTypedIf
