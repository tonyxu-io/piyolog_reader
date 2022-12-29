from distutils.core import setup
from setuptools import find_packages

install_requires = [
    "pandas",
    "numpy"
]


setup(
    name='piyolog_reader',
    version='0.0.0',
    author='shu65',
    author_email='dolphinripple@gmail.com',
    packages=find_packages(),
    install_requires=install_requires,
)