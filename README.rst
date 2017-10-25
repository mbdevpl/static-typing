.. role:: python(code)
    :language: python


static-typing
=============

.. image:: https://img.shields.io/pypi/v/static-typing.svg
    :target: https://pypi.python.org/pypi/static-typing
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

.. image:: https://img.shields.io/pypi/l/static-typing.svg
    :target: https://github.com/mbdevpl/static-typing/blob/master/NOTICE
    :alt: license

Attempt to add static type information to Python abstract syntax trees (ASTs).

Works best with ASTs from ``typed_ast`` module, however it also works with built-in ``ast`` module.

Be advised that this is an ongoing work, and current implementation is subject to sudden changes.


how to use
----------

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


how it's implemented
--------------------

First of all a type hint resolver has been implemented. It uses provided Python symbol tables
to resolve type hints into actual type objects using introspection, and stores the resolved type
hints directly in the AST. Thus, Python type information becomes static.

By default, the resolver uses only built-in symbols when called directly or through ``augment()``.
However, when called through ``parse()`` it uses ``globals()`` and ``locals()`` of the caller
by default.

Secondly, new fields have been added to several AST nodes, currently these are: ``Module``,
``FunctionDef``, ``ClassDef``, ``Assign``, ``AnnAssign``, ``For`` and ``With``. These new fields
store useful static type information in an organized and easy-to-access manner.

For ``Module``:

*   defined constants (TODO)
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

Thirdly, an AST augumenting function was implemented. This function resolves type hints in the AST
and replaces all ordinary AST nodes listed above with their extended versions.


requirements
------------

Python version >= 3.4.

Python libraries as specified in `<requirements.txt>`_.

Building and running tests additionally requires packages listed in `<test_requirements.txt>`_.

Tested on Linux and Windows.
