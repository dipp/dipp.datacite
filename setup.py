#!/usr/bin/env python
#
# Setup script for the dipp library
# $Id: setup.py 4739 2014-01-10 14:04:49Z reimer $
#
# Usage: python setup.py install
#

from setuptools import setup, find_packages

__version__ = '0.1.1'

def _read(doc):
    return open(doc, 'rb').read()

setup(name='dipp.datacite',
      version=__version__,
      description="manage dois at datacite",
      long_description=_read('README.rst').decode('utf-8'),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Peter Reimer',
      author_email='reimer@hbz-nrw.de',
      url='',
      license='DFSL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['dipp', 'dipp.datacite'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'httplib2',
          'ssl'
          # -*- Extra requirements: -*-
      ],
     entry_points={
        'console_scripts':[
            'dippDataCite=dipp.datacite.datacite:main',
          ]  
     },
     )
