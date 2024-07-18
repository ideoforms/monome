#!/usr/bin/env python3

from setuptools import setup

setup(
    name = 'monome',
    version = '0.0.1',
    description = 'Synchronous I/O for monome devices',
    long_description = open("README.md", "r").read(),
    long_description_content_type = "text/markdown",
    author = 'Daniel Jones',
    author_email = 'dan-code@erase.net',
    url = 'https://github.com/ideoforms/monome',
    packages = ['monome'],
    install_requires = ['python-osc'],
    keywords = ('audio', 'sound', 'music', 'control', 'monome', 'grid', 'arc'),
    classifiers = [
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Artistic Software',
        'Topic :: Communications',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
    ]
)
