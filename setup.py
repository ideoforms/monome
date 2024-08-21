#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name = 'monome',
    version = '0.0.1',
    description = 'Synchronous I/O for monome devices',
    long_description = open("README.md", "r").read(),
    long_description_content_type = "text/markdown",
    author = 'Daniel Jones',
    author_email = 'dan-code@erase.net',
    url = 'https://github.com/ideoforms/monome',
    packages = find_packages(),
    install_requires = ['python-osc', 'singleton-decorator', 'numpy'],
    keywords = ('audio', 'sound', 'music', 'control', 'monome', 'grid', 'arc'),
    classifiers = [
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Artistic Software',
        'Topic :: Communications',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
    ]
)
