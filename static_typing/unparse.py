"""Unparse utility function"""

import io

from .unparser import Unparser


def unparse(tree) -> str:
    stream = io.StringIO()
    Unparser(tree, file=stream)
    return stream.getvalue()
