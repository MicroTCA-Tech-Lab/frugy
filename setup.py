#!/usr/bin/env python3
"""
SPDX-License-Identifier: BSD-3-Clause
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY.
See LICENSE.txt for license details.
"""

import setuptools
from pathlib import Path as path
from frugy import __version__

readme_contents = path('./README.md').read_text()
requirements = path('./requirements.txt').read_text().splitlines()
packages=setuptools.find_packages(include=['frugy'])

setuptools.setup(
    name='frugy',
    version=__version__,
    author='Patrick Huesmann',
    author_email='patrick.huesmann@desy.de',
    url='https://techlab.desy.de',
    license='BSD',
    description='FRU Generator YAML',
    long_description=readme_contents,
    long_description_content_type='text/markdown',
    keywords='ipmi fru microtca amc fmc picmg vita',
    install_requires=requirements,
    packages=packages,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
    ],
    entry_points={
        'console_scripts': [
            'frugy=frugy.cli:main',
        ],
    },
    python_requires='>=3.6'
)
