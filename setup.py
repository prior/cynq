#!/usr/bin/env python
from setuptools import setup, find_packages

VERSION = '2.3.11'

setup(
    name='cynq',
    version=VERSION,
    author='prior',
    author_email='mprior@hubspot.com',
    packages=find_packages(),
    url='https://github.com/HubSpot/cynq',
    download_url='https://github.com/HubSpot/cynq/tarball/v%s'%VERSION,
    license='LICENSE.txt',
    description='A data synchronizer',
    long_description=open('README.rst').read(),
    install_requires=[
        'sanetime>=4,<5',
    ],
)

