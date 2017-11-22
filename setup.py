#!/usr/bin/env python
from setuptools import setup


requirements = [
    'click',
    'colorful',
    'ipdb',
    'ipython',
    'nose',
    'prompt_toolkit',
    'pycryptodome',
    'sqlalchemy',
]

setup(
    name='passwords',
    version='0.0.1',
    url='https://www.github.com/cieplak/passwords',
    description='password manager',
    packages=['passwords'],
    include_package_data=True,
    install_requires=requirements,
    tests_require=['nose'],
    scripts=['bin/passwords'],
)
