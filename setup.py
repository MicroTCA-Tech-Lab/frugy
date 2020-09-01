#!/usr/bin/env python3

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
#   license='BSD',
    description='FRU Generator YAML',
    long_description=readme_contents,
    long_description_content_type='text/markdown',
    keywords='ipmi fru microtca amc fmc picmg vita',
    install_requires=requirements,
    packages=packages,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
#       'License :: OSI Approved :: BSD License',
    ],
    entry_points={
        'console_scripts': [
            'frugy=frugy.cli:main',
        ],
    },
    python_requires='>=3.6'
)
