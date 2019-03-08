#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
import requirements

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

setup_requirements = []
with open('requirements/prod.txt', 'r') as fd:
    for req in requirements.parse(fd):
        setup_requirements.append(req.name)

test_requirements = []
with open('requirements/test.txt', 'r') as fd:
    for req in requirements.parse(fd):
        test_requirements.append(req.name)

setup(
    name='p4_tools',
    version='0.1.0',
    description="Tools for Planet Four data reduction and analysis.",
    long_description=readme + '\n\n' + history,
    author="K.-Michael Aye",
    author_email='kmichael.aye@gmail.com',
    url='https://github.com/michaelaye/p4_tools',
    packages=find_packages(include=['p4_tools']),
    entry_points={
        'console_scripts': [
            'p4_tools=p4_tools.cli:main'
        ]
    },
    package_dir={'p4_tools':
                 'p4_tools'},
    include_package_data=True,
    install_requires='pandas',
    license="ISC license",
    zip_safe=False,
    keywords='p4_tools',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
