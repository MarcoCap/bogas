"""BOard GAme Simulator.

This file is adapted from (many thanks):
https://github.com/pypa/sampleproject

See also:
https://packaging.python.org/en/latest/distributing.html
"""

from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

__author__ = "Marco Capitani"
__copyright__ = "Copyright 2017, Marco Capitani"
__credits__ = []
__license__ = "GPLv2"
__version__ = "0.1"
__maintainer__ = "Marco Capitani"
__status__ = "Pre-Alpha"


here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='bogas',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.1.0',

    description='Universal BOard GAme Simulator',
    long_description=long_description,

    # The project's main homepage.
    url='TBD',

    # Author details
    author='Marco Capitani',
    author_email='capitani.mrc@gmail.com',

    # Choose your license
    license='GPLv2',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',

        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop'
        'Topic :: Games/Entertainment :: Board Games',

        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',

        'Programming Language :: Python :: 3.6',
    ],

    keywords='board-game game-development',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['tornado', 'pynacl'],

    # You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': [],
        'bogastest': [],
    },

    # package_data={
    #     'bogas': [],
    # },

    # See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    # entry_points={
    #     'console_scripts': [
    #         'bogas=bogas:main',
    #     ],
    # },
)
