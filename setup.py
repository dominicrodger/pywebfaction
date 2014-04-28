#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


readme = open('README.rst').read()

setup(
    name='pywebfaction',
    version='0.1.0',
    description='A tool for interacting with the WebFaction API.',
    long_description=readme,
    author='Dominic Rodger',
    author_email='dominicrodger@gmail.com',
    url='https://github.com/dominicrodger/pywebfaction',
    packages=[
        'pywebfaction',
    ],
    package_dir={'pywebfaction':
                 'pywebfaction'},
    include_package_data=True,
    install_requires=[
    ],
    license="BSD",
    zip_safe=False,
    keywords='pywebfaction',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    tests_require=[
        "pytest==2.5.2",
        "pytest-cov==1.6",
        "httpretty==0.8.0",
    ],
    cmdclass={'test': PyTest},
)
