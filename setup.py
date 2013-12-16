#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == "publish":
    os.system("python setup.py sdist upload")
    sys.exit()

required = [
    'requests>=1.2.0',
    'lxml>=3.2.3',
    'docopt>=0.6.1'
]

setup(
    name='viafsbn',
    version='0.1',
    description='Simple library for extracting data from Wikipedia templates',
    author='Cristian Consonni',
    author_email='kikkocristian@gmail.com',
    url='https://github.com/SpazioDati/Wikipedia-Template-Parser',
    scripts=['scripts/viafsbn'],
    packages=['viafsbn'],
    install_requires=required,
    license='MIT',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Internet',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
)
