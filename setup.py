"""Build script for static_typing package."""

import setup_boilerplate


class Package(setup_boilerplate.Package):

    """Package metadata."""

    name = 'static-typing'
    description = 'add static type information to Python abstract syntax trees'
    download_url = 'https://github.com/mbdevpl/static-typing'
    classifiers = [
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Education',
        'Topic :: Scientific/Engineering',
        'Topic :: Utilities']
    keywords = [
        'ast', 'parser', 'parsing', 'static type information', 'type analysis', 'types', 'typing']


if __name__ == '__main__':
    Package.setup()
