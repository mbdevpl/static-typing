

def scan_Assign_target(
        target: t.Union[ast_module.Name, ast_module.Tuple],
        type_comment: t.Optional[tuple]) -> t.Sequence[t.Tuple[str, t.Sequence[type]]]:
    """Scan target of Assign node."""
    if isinstance(target, ast_module.Tuple):
        if type_comment is None:
            type_comment = [None for _ in target.elts]
        elif isinstance(type_comment, (ast.Tuple, ast_module.Tuple)):
            warnings.warn('wtf', FutureWarning)
            type_comment = type_comment.elts
        variables = []
        for elt, cmnt in zip(target.elts, type_comment):
            variables += scan_Assign_target(elt, cmnt)
        return variables

    #if isinstance(target, ast_module.Attribute):
    #    return [(target, type_comment)]
    #assert isinstance(target, ast_module.Name), type(target)
    return [(target, type_comment)]


def scan_Assign(node: ast_module.Assign) -> t.Sequence[t.Tuple[str, t.Sequence[type]]]:
    """Scan Assign node."""
    variables = []
    for target in node.targets:
        variables += scan_Assign_target(target, node.type_comment)
    return variables


def scan_AnnAssign(node: ast_module.AnnAssign) -> t.Sequence[t.Tuple[str, t.Sequence[type]]]:
    """Scan AnnAssign node."""
    #assert isinstance(node.target, ast_module.Name)
    return [(node.target, node.annotation)]

