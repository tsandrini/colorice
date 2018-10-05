import sys

assert sys.version_info >= (3, 5), 'use python 3.5 or above'

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

package_name = 'colorice'


class PyTest(TestCommand):


    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = [
            '--cov-report',
            'term-missing',
            '--cov',
            'colorice',
            '--verbose'
        ]


    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True


    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


exec(open('colorice/settings.py').read())
setup(
    name=package_name,
    version=__version__,
    description='',
    long_description='',
    author='Patrik Janoušek, Tomáš Sandrini',
    author_email='patrikjanousek97@gmail.com, tomas.sandrini@seznam.cz',
    license='GPLv2',
    packages=find_packages(exclude=['tests']),
    install_requires=[
    ],
    tests_require=[
        'pytest-cov',
        'pytest',
    ],
    cmdclass={'test': PyTest},
)
