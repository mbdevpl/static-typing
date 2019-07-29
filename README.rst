.. role:: python(code)
    :language: python


=============
static-typing
=============

Augument Python 3 abstract syntax trees (ASTs) with static type information.

.. image:: https://img.shields.io/pypi/v/static-typing.svg
    :target: https://pypi.org/project/static-typing
    :alt: package version from PyPI

.. image:: https://travis-ci.org/mbdevpl/static-typing.svg?branch=master
    :target: https://travis-ci.org/mbdevpl/static-typing
    :alt: build status from Travis CI

.. image:: https://ci.appveyor.com/api/projects/status/github/mbdevpl/static-typing?branch=master&svg=true
    :target: https://ci.appveyor.com/project/mbdevpl/static-typing
    :alt: build status from AppVeyor

.. image:: https://api.codacy.com/project/badge/Grade/c10705787cbf4ebeafa95d18459fd690
    :target: https://www.codacy.com/app/mbdevpl/static-typing
    :alt: grade from Codacy

.. image:: https://codecov.io/gh/mbdevpl/static-typing/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/mbdevpl/static-typing
    :alt: test coverage from Codecov

.. image:: https://img.shields.io/github/license/mbdevpl/static-typing.svg
    :target: https://github.com/mbdevpl/static-typing/blob/master/NOTICE
    :alt: license

Python is a dynamically typed programming language.
However, much of typically seen Python code would work even if it was statically typed!

With this package, one can insert static type information into Python abstract syntax trees (ASTs),
so assuming that given code would work if Python was statically typed,
one can reason about the types in the code statically, ahead of execution.

Such augmented AST is mainly intended for analysis/consumption using other tools.

Works best with ASTs from ``typed_ast`` module, however it also works with built-in ``ast`` module.

Be advised that this is an ongoing work, and current implementation is subject to sudden changes.

Support of ``typed_ast`` will be dropped after Python 3.8 is released, as its functionality will be
merged into the built-in AST parser.

.. contents::
    :backlinks: none


How to use
==========

You can use the ``static_typing`` module to parse the code directly using ``parse()`` function:

.. code:: python

    import static_typing as st
    class MyClass:
        pass
    module = st.parse('def my_fun(obj: MyClass) -> MyClass: return obj')
    # TODO: currently there is no public API yet
    functions = module._functions
    my_fun = module._functions['my_fun']
    assert MyClass in my_fun._params['obj']

Or, you can augment existing AST using ``augment()`` function:

.. code:: python

    import static_typing as st
    import typed_ast.ast3
    module = typed_ast.ast3.parse('''def spam(): x, y, z = 'ham', 42, 3.1415  # type: str, int, float''')
    module = st.augment(module)
    # TODO: currently there is no public API yet
    function = module._functions['spam']
    assert len(function._local_vars) == 3
    assert float in function._local_vars['z']

For more examples see `<examples.ipynb>`_ notebook.


AST manipulation
----------------

Additionally to the main features, the library contains ``static_typing.ast_manipulation``
module which contains low-level tools and building blocks allowing for:

*   recursive AST traversal,
*   AST validation,
*   recursive AST transformations,
*   AST transcribing (from ``typed_ast`` to built-in ``ast`` and vice versa) and
*   resolving type hints (described in detail below).


How it's implemented
====================

The process or static typing, which the ``augment()`` function implements, has 3 main steps:

*   type hint resolution,
*   type information combining and
*   AST rewriting.


Type hint resolution
--------------------

In all applicable nodes, type hints are stored in fields ``type_comment``, ``annotation``
and ``returns``. The type hint resolver reads those fields -- which themseves are either raw strings
or ASTs.

It uses provided Python symbol tables to resolve type hints into actual type objects using
introspection.

By default, the resolver uses only built-in symbols when called directly or through ``augment()``.
However, when called through ``parse()`` it uses ``globals()`` and ``locals()`` of the caller
by default.

The resolved type hints are stored directly in the AST. Specifically, each resolved field is stored
in a correspondingly named field, which is either ``resolved_type_comment``, ``resolved_annotation``
or ``resolved_returns``.

Thus, static type information becomes available in the AST.


Type information combining
--------------------------

For each AST node that might contain any name declarations, an exetended version of a node
is provided. Each extended AST node has new fields that store those declared names and type
information associated with each name.

These new fields store all type information from all resolved type hints within any local scope,
so that a type conflict or lack of type information can be detected. Also, based on this combined
information, type inference can be performed.

Specifically, new versions of following AST nodes with new fields are provided: ``Module``,
``FunctionDef``, ``ClassDef``, ``Assign``, ``AnnAssign``, ``For`` and ``With``. Those new versions
have their names prefixed ``StaticallyTyped...``.

A list of entities for which information is gathered in those new fields follows.

For ``Module``:

*   defined variables
*   defined functions
*   defined classes

For ``FunctionDef``:

*   parameters and their types
*   return types
*   kind  (i.e. function, instance method, class method, static method, etc.)
*   local variables and their types

For ``ClassDef``:

*   defined methods (all together and grouped by kind)
*   class fields and their types
*   instance fields and their types

For ``Assign`` and ``AnnAssign``:

*   assignment targets and their types

For ``For``:

*   index variables and their types

For ``With``:

*   context variables and their types


AST rewriting
-------------

The AST rewriting means replacing ordinary AST nodes listed above with their extended versions.


Requirements
============

Python version 3.5 or later.

Python libraries as specified in `<requirements.txt>`_.

Building and running tests additionally requires packages listed in `<test_requirements.txt>`_.

Tested on Linux and Windows.
