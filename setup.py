from __future__ import print_function
from setuptools import setup, find_packages
import os
import io

PACKAGE = "scoutmasterapi_builder"
NAME = "scoutmasterapi_builder"
DESCRIPTION = 'ScoutMaster API client' 
AUTHOR = "Rinus Vijftigschild"
AUTHOR_EMAIL = 'rinus.vijftigschild@aerovision.nl'
URL = 'https://github.com/AeroVision-code/ScoutMasterAPI-builder/'
LICENSE="LicenseRef-Proprietary"
VERSION = "0.0.1"

here = os.path.abspath(os.path.dirname(__file__))

def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md')

setup(
    name=NAME,
    version=VERSION,
    url=URL,
    download_url='https://github.com/AeroVision-code/ScoutMasterAPI-builder/archive/refs/heads/main.zip',
    license='LicenseRef-Proprietary',
    author=AUTHOR,
    install_requires=['numpy>=2.2.2'],
    extras_require = {},
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=long_description,
    packages=find_packages(), 
    include_package_data=True,
    platforms='any',
    test_suite='',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: LicenseRef-Proprietary',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering']
)