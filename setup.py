__author__ = 'florian'

from setuptools import setup

with open('README.md') as f:
    readme = f.read()

setup(
    name = "",
    description = "",
    long_description = readme,
    version = "",
    author = "",
    author_email = "",
    py_modules = [],
    url = "",
    license = "",
    install_requires=[
        'python_dateutil',
        'pyquery',
        'cssselect',    # required by pyquery
        'requests',
        'rauth',
        'lxml',
        'pyyaml'
    ],
    classifiers = []
)