#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

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
    test_suite='tests',
)
