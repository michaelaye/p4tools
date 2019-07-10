#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

setup(
    name='p4tools',
    version='0.8.0',
    description="Tools for Planet Four data analysis.",
    long_description=readme + '\n\n' + history,
    author="K.-Michael Aye",
    author_email='kmichael.aye@gmail.com',
    url='https://github.com/michaelaye/p4tools',
    packages=find_packages(include=['p4tools']),
    entry_points={
        'console_scripts': [
            'p4tools=p4tools.cli:main'
        ]
    },
    package_dir={'p4tools':
                 'p4tools'},
    include_package_data=True,
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib',
        'shapely',
        'intake'
    ],
    license="ISC license",
    zip_safe=False,
    keywords='p4tools',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    test_suite='tests',
    tests_require='pytest',
    setup_requires='pytest_runner',
)
