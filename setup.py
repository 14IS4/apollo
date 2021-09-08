#!/usr/bin/env python
from os.path import abspath
from os.path import dirname
from os.path import join
from setuptools import setup
from setuptools import find_packages

cwd = abspath(dirname(__file__))

with open(join(cwd, 'README.md'), 'r') as readme_file:
    long_description = readme_file.read()

with open(join(cwd, 'requirements.txt')) as requirements_file:
    requirements = requirements_file.read().splitlines()

setup(
    name='apollo',
    version='1.0',
    author='Kendrick Horeftis',
    author_email='kendrick@horeft.is',
    description=(
        'Wrapper around dbt cli and serves as a '
        'base for the web launcher/scheduler'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    install_requires=requirements,
    entry_points='''
    [console_scripts]
    apollo=apollo.wrapper:main
    ''',
    python_requires='>=3.6',
    packages=find_packages(exclude=['tests']),
    platforms='any',
    package_data={'apollo': ['templates/*.yml']},
    include_package_data=True,
)