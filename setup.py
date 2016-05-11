import io
import os
import re
from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys

PKG_NAME = 'atmdb'

HERE = os.path.abspath(os.path.dirname(__file__))

PATTERN = r'^{target}\s*=\s*([\'"])(.+)\1$'

AUTHOR = re.compile(PATTERN.format(target='__author__'), re.M)
DOCSTRING = re.compile(r'^([\'"])\1\1(.+)\1\1\1$', re.M)
VERSION = re.compile(PATTERN.format(target='__version__'), re.M)


def parse_init():
    with open(os.path.join(HERE, PKG_NAME, '__init__.py')) as f:
        file_data = f.read()
    return [regex.search(file_data).group(2) for regex in
            (AUTHOR, DOCSTRING, VERSION)]


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


long_description = read('README.rst')
author, description, version = parse_init()


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = [
            '--pylint',
            '--pylint-error-types=FEW',
            '--runslow',
        ]
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    author=author,
    author_email='mail@jonrshar.pe',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only',
    ],
    cmdclass={'test': PyTest},
    description=description,
    install_requires=['aiohttp', 'python-dateutil'],
    license='License :: OSI Approved :: ISC License (ISCL)',
    long_description=long_description,
    name=PKG_NAME,
    packages=[PKG_NAME],
    platforms='any',
    tests_require=[
        'asynctest',
        'pylint',
        'pytest',
        'pytest-asyncio',
        'pytest-pylint',
    ],
    url='http://github.com/textbook/atmdb/',
    version=version,
)